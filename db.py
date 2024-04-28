# file containing all interactions with the database
# contains method for retriving, inserting, and deleting from tables

import os
import sys
import psycopg2
import sqlalchemy.ext.declarative
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

#-----------------------------------------------------------------------
Base = sqlalchemy.ext.declarative.declarative_base()

class Users(Base):
    __tablename__ = 'users'
    user_id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    name = Column(String)
    creation = Column(DateTime, default=datetime.utcnow)

class Inventory(Base):
    __tablename__ = 'inventory'
    inventory_id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship('Users', backref='inventory')

class Category(Base):
    __tablename__ = 'category'
    category_id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    descrip = Column(Text)

class Item(Base):
    __tablename__ = 'item'
    item_id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    inventory_id = Column(Integer, ForeignKey('inventory.inventory_id'))
    category_id = Column(Integer, ForeignKey('category.category_id'))
    item_name = Column(String)
    description = Column(String)
    quantity = Column(Integer)
    expiry = Column(String)

load_dotenv()
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
_engine = sqlalchemy.create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#-----------------------------------------------------------------------
# Database get methods

# retrieves user information from users table if exists
def retrieveUser(user_id):
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            query = session.query(Users).filter(Users.user_id == user_id)
            user = query.first()
            if user is None:
                return None
            else:
                return {'user_id': user.user_id, 'email': user.email, 'name': user.name, 'creation': user.creation}
    except Exception as ex:
        print('retrieveUser', file=sys.stderr)
        print(ex, file=sys.stderr)
        return ex
    
# retrieves all users from users table
def retrieveAllUsers():
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            query = session.query(Users)
            users = query.all()
            if users is None:
                return None
            else:
                return [{'user_id': user.user_id, 'email': user.email, 'name': user.name, 'creation': user.creation} for user in users]
    except Exception as ex:
        print('retrieveAllUsers', file=sys.stderr)
        print(ex, file=sys.stderr)
        return ex
    
# retrieves inventory information from inventory table if exists
def retrieveInventory(user_id):
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            query = session.query(Inventory).filter(Inventory.user_id == user_id)
            inventory = query.first()
            if inventory is None:
                return None
            else:
                return inventory.inventory_id
    except Exception as ex:
        print('retrieveInventory', file=sys.stderr)
        print(ex, file=sys.stderr)
        return ex

# retrieves category information from category table if exists
def retrieveCategory(category_id):
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            query = session.query(Category).filter(Category.category_id == category_id)
            category = query.first()
            if category is None:
                return None
            else:
                return {'category_id': category.category_id, 'descrip': category.descrip}
    except Exception as ex:
        print('retrieveCategory', file=sys.stderr)
        print(ex, file=sys.stderr)
        return ex

# retrieves item information from item table if exists
def retrieveItem(item_id):
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            query = session.query(Item).filter(Item.item_id == item_id)
            item = query.first()
            if item is None:
                return None
            else:
                return {'item_id': item.item_id, 'inventory_id': item.inventory_id, 'item_name': item.item_name, 'category_id': item.category_id, 'expiry': item.expiry, 'quantity': item.quantity, 'description': item.description}
    except Exception as ex:
        print('retrieveItem', file=sys.stderr)
        print(ex, file=sys.stderr)
        return ex
    

def retrieveItems(inventory_id):
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            query = session.query(Item).filter(Item.inventory_id == inventory_id)
            items = query.all()
            if items is None:
                return None
            else:
                return [{'item_id': item.item_id, 'inventory_id': item.inventory_id, 'item_name': item.item_name, 'category_id': item.category_id, 'expiry': item.expiry, 'quantity': item.quantity, 'description': item.description} for item in items]
    except Exception as ex:
        print('retrieveItems', file=sys.stderr)
        print(ex, file=sys.stderr)
        return ex

def retrieveOrInsertCategory(category_descrip, item_name):
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            if category_descrip == '':
                print("gpting")
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are generating a simple category name for this item"},
                        {"role": "user", "content": "Generate the name of a broad home good category that this item might be in: " + item_name}
                    ]
                )
                category_descrip = completion.choices[0].message.content
            query = session.query(Category).filter(Category.descrip == category_descrip)
            category = query.first()

            if category is not None:
                return category.category_id
            else:
                # If the category doesn't exist, create a new one
                return insertCategory({'descrip': category_descrip})
            
    except Exception as ex:
        print('retrieveOrInsertCategory', file=sys.stderr)
        print(ex, file=sys.stderr)
        return ex
#-----------------------------------------------------------------------
# insert/update functions

# insert new request into the request table, returns request_id
def insertUser(user_info):
    with sqlalchemy.orm.Session(_engine) as session:
        row = Users(user_id=user_info.get('user_id'), email=user_info.get('email'), name=user_info.get('name'), creation=user_info.get('creation'))
        session.add(row)
        try:
            # Commit the session to save the changes to the database
            session.commit()
            return row.user_id
        except sqlalchemy.exc.IntegrityError as e:
            # Print any error that occurs during the commit
            print(e)
            session.rollback()
            return False

# insert new inventory into the inventory table, returns inventory_id
def insertInventory(inventory_info):
    with sqlalchemy.orm.Session(_engine) as session:
        row = Inventory(inventory_id=inventory_info.get('inventory_id'), user_id=inventory_info.get('user_id'))
        session.add(row)
        try:
            session.commit()
            return row.inventory_id
        except sqlalchemy.exc.IntegrityError as e:
            print(e)
            session.rollback()
            return False
        
# insert new category into the category table, returns category_id
def insertCategory(category_info):
    with sqlalchemy.orm.Session(_engine) as session:
        row = Category(descrip=category_info.get('descrip'))
        session.add(row)
        try:
            session.commit()
            return row.category_id
        except sqlalchemy.exc.IntegrityError as e:
            print(e)
            session.rollback()
            return False
        
# insert new item into the item table, returns item_id
def insertItem(item_info):
    with sqlalchemy.orm.Session(_engine) as session:
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are estimating the usage lifespan of items."},
            {"role": "user", "content": "How many days would you predict that it would take someone to run out of the following." + item_info.get('item_name') + "Give an exact number of days, and only a single number. Format like this [number] days"}
        ]
        )
        row = Item(item_name=item_info.get('item_name'), inventory_id=item_info.get('inventory_id'), category_id=item_info.get('category_id'), quantity=item_info.get('quantity'), description=item_info.get('description'), expiry=completion.choices[0].message.content)
        session.add(row)
        try:
            session.commit()
            return row.item_id
        except sqlalchemy.exc.IntegrityError as e:
            print(e)
            session.rollback()
            return False

def get_or_create_user(email, name):
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            # Check if the email is in the Users table
            user = session.query(Users).filter(Users.email == email).first()
            if user is not None:
                # If the email is in the Users table, return the user_id
                return user.user_id

            # If the email is not in the Users table, create a new user
            new_user = Users(email=email, name=name, creation=sqlalchemy.func.now())
            session.add(new_user)
            session.commit()
            session.flush()  # Flush the session to assign an ID to new_user

            # Create a new row in the Inventory table
            new_inventory = Inventory(user_id=new_user.user_id)
            session.add(new_inventory)

            # Commit the session to save the changes
            session.commit()

            # Return the new user's ID
            return new_user.user_id
    except Exception as ex:
        print('get_or_create_user', file=sys.stderr)
        print(ex, file=sys.stderr)
        return None
    
def update_quantity(item_id, dir):
    with sqlalchemy.orm.Session(_engine) as session:
        item = session.query(Item).filter(Item.item_id == item_id).first()
        if item:
            item.quantity += dir
            if item.quantity < 0:
                item.quantity = 0
            session.commit()
        else:
            print(f"Item with id {item_id} not found", file=sys.stderr)

def delete_item(item_id):
    with sqlalchemy.orm.Session(_engine) as session:
        item = session.query(Item).filter(Item.item_id == item_id).first()
        if item:
            session.delete(item)
            session.commit()
        else:
            print(f"Item with id {item_id} not found", file=sys.stderr)
#-----------------------------------------------------------------------
# Reset functions, run these to clear tables 

def clear_all_tables():
    with sqlalchemy.orm.Session(_engine) as session:
        try:
            # Iterate over all tables defined in the Base metadata and delete their contents
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
            print("All tables cleared.")
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()
        finally:
            session.close()

if __name__ == '__main__':
    #clear_all_tables()
    print(retrieveItems(1))
    #print(insertItem({"inventory_id": 2, "category_id": 6, "quantity": 12, 'description': "lettuce"}))
    #print(retrieveAllUsers())
    #print(insertFinData(3))
    #print('hello world')