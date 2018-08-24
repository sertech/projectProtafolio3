import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalogApp.db')
DBSession = sessionmaker(bind=engine)
session = DBSession()

new_items = json.loads("""{
    "all_items":[
        {
            "t_itemName": "test1",
            "t_itemDescription": "Ullamco dolore "
        },
        {
            "t_itemName": "test2",
            "t_itemDescription": "Ullamco dolore "
        },
        {
            "t_itemName": "test3",
            "t_itemDescription": "Ullamco dolore "
        },
        {
            "t_itemName": "test4",
            "t_itemDescription": "Ullamco dolore "
        },
        {
            "t_itemName": "test5",
            "t_itemDescription": "Ullamco dolore "
        },
        {
            "t_itemName": "test6",
            "t_itemDescription": "Ullamco dolore "
        },
        {
            "t_itemName": "test7",
            "t_itemDescription": "Ullamco dolore "
        },
        {
            "t_itemName": "test8",
            "t_itemDescription": "Ullamco dolore "
        }
    ]
}""")

for x_item in new_items['all_items']:
    new_item = Item(t_itemName=str(x_item['t_itemName']), t_itemDescription=str(x_item['t_itemDescription']), t_userId=1, t_catId=1)
    print('adding..:%s' % x_item)
    session.add(new_item)
    session.commit()
