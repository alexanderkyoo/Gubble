#!/usr/bin/env python
import sys
import os
from dotenv import load_dotenv
import flask
import reciept
import io
import db
from authlib.integrations.flask_client import OAuth
from authlib.jose.errors import InvalidClaimError

load_dotenv()

app = flask.Flask(__name__)
app.secret_key = 'your-secret-key'

oauth = OAuth()
oauth.init_app(app)
client_id = os.getenv('AUTH_ID')
client_secret = os.getenv('AUTH_SECRET')

google = oauth.register(
    name='google',
    client_id=client_id,
    client_secret=client_secret,
    #access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    #authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

# Index page
@app.route('/')
def index():
    user_data = flask.session.get('profile')
    html_code = flask.render_template('index.html',
                                      logged_in='profile' in flask.session,
                                      user_data=user_data)
    response = flask.make_response(html_code)
    return response

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    resp = google.authorize_access_token()
    
    if resp is None or resp.get('access_token') is None:
        return 'Access denied', 403

    flask.session['token'] = resp['access_token']

    resp = google.get('userinfo')
    user_info = resp.json()

    flask.session['profile'] = user_info
    flask.session.permanent = True
    flask.session['user_id'] = db.get_or_create_user(user_info['email'], user_info['name'])
    flask.session['inventory_id'] = db.retrieveInventory(flask.session['user_id'])
    return flask.redirect('/')

@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = flask.url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/inventory')
def inventory():
    if 'profile' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    items = db.retrieveItems(flask.session['inventory_id'])
    items = sorted(items, key=lambda item: item['item_id'])
    for item in items:
        cat = db.retrieveCategory(item['category_id'])
        if cat is None:
            item['category'] = 'None'
        else:
            item['category'] = db.retrieveCategory(item['category_id'])['descrip']
    return flask.render_template('inventory.html', logged_in=('profile' in flask.session), items=items)

@app.route('/logout')
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))


@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if flask.request.method == 'POST':
        cat = flask.request.form.get('category_descrip')
        item_name = flask.request.form.get('item_name')
        cat_id = db.retrieveOrInsertCategory(cat, item_name)
        item_info = {
            'item_name': item_name,
            'inventory_id': flask.session['inventory_id'],
            'category_id': cat_id,
            'description': flask.request.form.get('description'),
            'quantity': flask.request.form.get('quantity')
        }
        db.insertItem(item_info)
        return flask.redirect(flask.url_for('inventory'))
    return flask.render_template('add-item.html')


@app.route('/increase-quantity/<int:item_id>', methods=['GET', 'POST'])
def increase_quantity(item_id):
    db.update_quantity(item_id, 1)
    return flask.redirect(flask.url_for('inventory'))

@app.route('/decrease-quantity/<int:item_id>', methods=['GET', 'POST'])
def decrease_quantity(item_id):
    db.update_quantity(item_id, -1)
    return flask.redirect(flask.url_for('inventory'))

@app.route('/recieptscanner', methods=['GET', 'POST'])
def recieptscanner():
    if flask.request.method == 'POST':
        photo = flask.request.files['photo']
        photo_data = io.BytesIO(photo.read())
        text = reciept.parse_text_from_image(photo_data)
        print(text)
        if text != '':
            standardized_text = reciept.analyze_text(text)
            print(standardized_text)
            items = standardized_text.split('\n')
            for item in items:
                item_info = {
                    'item_name': item.split(',')[0].split(': ')[1],
                    'inventory_id': flask.session['inventory_id'],
                    'category_id': db.retrieveOrInsertCategory('', item.split(',')[0].split(': ')[1]),
                    'description': '',
                    'quantity': item.split(',')[1].split(': ')[1]
                }
                db.insertItem(item_info)
        return flask.redirect(flask.url_for('inventory')) 
    return flask.render_template('upload.html', logged_in=('profile' in flask.session))

@app.route('/delete/<int:item_id>', methods=['GET'])
def delete_item(item_id):
    db.delete_item(item_id)
    return flask.redirect(flask.url_for('inventory'))

