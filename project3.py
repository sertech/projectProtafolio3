# python functinality imports
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
# DB imports
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Category, Item

app = Flask(__name__)

# connect to the data base and create a session
engine = create_engine('sqlite:///catalogApp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/CatalogApp')
def mainPage():
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(desc(Item.t_id)).limit(7)
    return render_template('main.html', mainCategories = categories, mainItems = latestItems)



@app.route('/CatalogApp/<category_name>/items', methods=['GET', 'POST'])
def catPage(category_name):
    categories = session.query(Category).all()
    for cati in categories:
        if cati.t_catName == category_name:
            catx = cati.t_id
            

    latestItems = session.query(Item).filter_by(t_catId=catx)
    totalItems = session.query(Item).filter_by(t_catId=catx).count()
    print(totalItems)
    return render_template('categoryX.html', catpageCatName=category_name, catpageItems=latestItems, catpageCategories=categories, t_items=totalItems)


@app.route('/CatalogApp/<category_name>/<item_name>', methods=['GET', 'POST'])
def itemPage(category_name, item_name):
    itemX = session.query(Item).filter_by(t_itemName=item_name).first()
        
    return render_template('itemDesc.html', itempage=itemX)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    