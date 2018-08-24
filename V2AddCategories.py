#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalogApp.db')
DBSession = sessionmaker(bind=engine)
session = DBSession()

new_items = json.loads("""{
  "all_items": [
    {
      "t_itemName": "test1",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test2",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test3",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test4",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test5",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test6",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test7",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test8",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test9",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test10",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test11",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test12",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test13",
      "t_itemDescription": "Ipsum aute qui anim",
      "t_userId": 1,
      "t_catId": 1
    },
    {
      "t_itemName": "test14",
      "t_itemDescription": "Qui officia ea dolor id nostrud.",
      "t_userId": 1,
      "t_catId": 1
    }
  ]
}""")

for x_item in new_items['all_items']:
  print(x_item)
  new_item = Item(t_itemName=str(x_item['t_itemName']), t_itemDescription=str(x_item['t_itemDescription']), t_userId=1, t_catId=1)
  print(x_item)


session.add(new_item)
session.commit()
