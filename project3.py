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
    latestItems = session.query(Item).order_by(desc(Item.t_id)).limit(6)
    return render_template('main.html', mainCategories = categories, mainItems = latestItems)



@app.route('/CatalogApp/<category_name>/items')
def catPage(category_name):
    return "this page will display all the categories in one panel and in the second panel it will display all the items in the selected category also it will display the number of items within a category"


@app.route('/CatalogApp/<category_name>/<item_name>')
def itemPage(category_name, item_name):
    return "this page will display the item complete description"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    