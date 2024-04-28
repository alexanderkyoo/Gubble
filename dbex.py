def retrieveOrInsertCategory(category_descrip, item_name):
    try:
        with sqlalchemy.orm.Session(_engine) as session:
            if category_descrip == '':
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
    
# insert new item into the item table, returns item_id
def insertItem(item_info):
    with sqlalchemy.orm.Session(_engine) as session:
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are estimating the usage lifespan of items."},
            {"role": "user", "content": "How many days would you predict that it would take someone to run out of the following. Give an exact number of days, and only a single number, no extra text." + item_info.get('item_name')}
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
            user = session.query(Users).filter(Users.email == email).first()
            if user is not None:
                return user.user_id

            # If the email is not in the Users table, create a new user
            new_user = Users(email=email, name=name, creation=sqlalchemy.func.now())
            session.add(new_user)
            session.commit()
            session.flush() 
            new_inventory = Inventory(user_id=new_user.user_id)
            session.add(new_inventory)
            session.commit()
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