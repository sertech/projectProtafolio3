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

@app.route('/CatalogApp/<category_name>/new_item', methods=['GET', 'POST'])
def newItemPage(category_name):
    categories = session.query(Category).all()
    for cati in categories:
        if cati.t_catName == category_name:
            catx = cati.t_id
        
    if request.method == 'POST':
        new_item = Item(t_itemName=request.form['item_name'], t_itemDescription=request.form['i_description'], t_userId=1,t_catId=catx)
        session.add(new_item)
        session.commit()
        return redirect(url_for('mainPage'))
        
    else: # the method used in this call is GET
        print("this is a get call")
        return render_template('newItem.html', current_cat=category_name)
    

@app.route('/CatalogApp/<category_name>/<item_name>', methods=['GET', 'POST'])
def itemPage(category_name, item_name):
    itemX = session.query(Item).filter_by(t_itemName=item_name).first()
        
    return render_template('itemDesc.html', itempage=itemX, category_name=category_name)

@app.route('/CatalogApp/<item_name>/edit', methods=['GET', 'POST'])
def editItemPage(item_name):
    edit_item = session.query(Item).filter_by(t_itemName=item_name).one()
    categories = session.query(Category).all()
    for cati in categories:
        if cati.t_id == edit_item.t_catId:
            catx = cati
    
    if request.method == 'POST':
        # values received
        print("receiving values from the form")
        print("item name: %s" % request.form['newItemName'])
        print("item description: %s" % request.form['newDescription'])
        print("item catid: %s" % request.form['categories'])
        

        edit_item.t_itemName = request.form['newItemName']
        edit_item.t_itemDescription = request.form['newDescription']
        edit_item.t_userId = 1
        edit_item.t_catId = int(request.form['categories'])
        session.add(edit_item)
        session.commit()
        return redirect(url_for('mainPage'))


    else:
        print("this is the GET call and its the first part to run")
        return render_template('editItem.html', current_item=edit_item, current_cat=catx)
        
    return "render_template('itemDesc.html') "  

@app.route('/CatalogApp/<item_name>/delete', methods=['GET', 'POST'])
def deleteItemPage(item_name):
    delete_item = session.query(Item).filter_by(t_itemName=item_name).one()
    categories = session.query(Category).all()
    for cati in categories:
        if cati.t_id == delete_item.t_catId:
            catx = cati

    if request.method == 'POST':
        session.delete(delete_item)
        session.commit()
        return  redirect(url_for('mainPage'))
    else:
        return render_template('deleteItem.html', current_item=delete_item, current_cat=catx)
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    