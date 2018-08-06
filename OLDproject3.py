# ---------------python functinality imports----------------------------------
from flask import (Flask, render_template, request, redirect, jsonify, url_for, flash, g, abort)
from flask import session as login_session
import random
import string
import httplib2
import json
from flask import make_response
import requests
# ----------------------------------------------------------------------

# ----------- google sign in -----------------------------
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
# --------------------------------------------------------

# ------------------------- DB imports---------------------
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Category, Item
# ---------------------------------------------------------

# ----- login and security imports-------------------------
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
# ---------------------------------------------------------

app = Flask(__name__)

# connect to the data base and create a session-----------
engine = create_engine('sqlite:///catalogApp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
# ---------------------------------------------------------


@auth.verify_password
def verify_password(userEmail, password):
    user = session.query(User).filter_by(t_email=userEmail).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/')
@app.route('/CatalogApp')
def mainPage():
    if 'user_email' in login_session:
        print(login_session['user_email'])
        categories = session.query(Category).all()
        latestItems = session.query(Item).order_by(desc(Item.t_id)).limit(7)
        return render_template('privateMain.html', mainCategories = categories, mainItems = latestItems, current_user=login_session['user_email'])    
    else:
        print(" nothin in login session")
        categories = session.query(Category).all()
        latestItems = session.query(Item).order_by(desc(Item.t_id)).limit(7)
        return render_template('publicMain.html', mainCategories = categories, mainItems = latestItems)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usermail']
        password = request.form['userpass']
        if verify_password(username,password):
            current_user = g.user
            categories = session.query(Category).all()
            latestItems = session.query(Item).order_by(desc(Item.t_id)).limit(7)
            login_session['user_name'] = current_user.t_name
            login_session['user_email'] = current_user.t_email
            login_session['user_picture'] = current_user.t_picture
            login_session['user_id'] = current_user.t_id
            print(login_session['user_name'])
            print(login_session['user_email'])
            print(login_session['user_picture'])
            print(login_session['user_id'])
            
            return render_template('privateMain.html', mainCategories = categories, mainItems = latestItems, current_user=current_user.t_email)                   
        else:
            print("Error in login credentials")
            return render_template('login.html') 
    else:
        print("this is the GET and first response")
        return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the user email from the session
    login_session.pop('user_email', None) 
    return redirect(url_for('mainPage'))
    

@app.route('/users', methods=['POST'])
def new_user():
    if request.method == 'POST':
        new_user = User(t_name=request.form['newusername'],t_email=request.form['newusermail'], t_picture='Nothing at all nothing at all')
        new_user.hash_password(request.form['newuserpass'])
        session.add(new_user)
        session.commit()
        return redirect(url_for('login'))
    else:
        print("this is by default the first action its a GET request")
        return render_template('login.html')

@app.route('/CatalogApp/<category_name>/items', methods=['GET', 'POST'])
def catPage(category_name):    
    if 'user_email' in login_session:
        categories = session.query(Category).all()
        for cati in categories:
            if cati.t_catName == category_name:
                catx = cati.t_id            

        latestItems = session.query(Item).filter_by(t_catId=catx)
        totalItems = session.query(Item).filter_by(t_catId=catx).count()
    
        return render_template('categoryX.html', catpageCatName=category_name, catpageItems=latestItems, catpageCategories=categories, t_items=totalItems, current_user=login_session['user_email'])
    else:
        print ('there is nothin is login session')
        categories = session.query(Category).all()
        for cati in categories:
            if cati.t_catName == category_name:
                catx = cati.t_id            

        latestItems = session.query(Item).filter_by(t_catId=catx)
        totalItems = session.query(Item).filter_by(t_catId=catx).count()
        print(totalItems)
        return render_template('publicCategoryX.html', catpageCatName=category_name, catpageItems=latestItems, catpageCategories=categories, t_items=totalItems)


@app.route('/CatalogApp/<category_name>/new_item', methods=['GET', 'POST'])

def newItemPage(category_name):
    if 'user_email' in login_session:
        categories = session.query(Category).all()
        for cati in categories:
            if cati.t_catName == category_name:
                catx = cati.t_id
            
        if request.method == 'POST':
            new_item = Item(t_itemName=request.form['item_name'], t_itemDescription=request.form['i_description'], t_userId=1,t_catId=catx)
            session.add(new_item)
            session.commit()
            flash("new item added to the database")
            return redirect(url_for('mainPage'))
            
        else: # the method used in this call is GET
            print("this is a get call")
            return render_template('newItem.html', current_cat=category_name, current_user=login_session['user_email'])
    else:
        return redirect(url_for('login'))
    

@app.route('/CatalogApp/<category_name>/<item_name>', methods=['GET', 'POST'])
def itemPage(category_name, item_name):
    if 'user_email' in login_session:
        itemX = session.query(Item).filter_by(t_itemName=item_name).first()
        
        return render_template('itemDesc.html', itempage=itemX, category_name=category_name, current_user=login_session['user_email'])
    else:
        itemX = session.query(Item).filter_by(t_itemName=item_name).first()
        
        return render_template('publicItemDesc.html', itempage=itemX, category_name=category_name)

@app.route('/CatalogApp/<item_name>/edit', methods=['GET', 'POST'])

def editItemPage(item_name):
    if 'user_email' in login_session:
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
            flash("item edited")
            return redirect(url_for('mainPage'))


        else:
            print("this is the GET call and its the first part to run")
            return render_template('editItem.html', current_item=edit_item, current_cat=catx, current_user=login_session['user_email'])
            
        return "render_template('itemDesc.html') "
    else:
        return redirect(url_for('login'))
      

@app.route('/CatalogApp/<item_name>/delete', methods=['GET', 'POST'])

def deleteItemPage(item_name):
    if 'user_email' in login_session:
        delete_item = session.query(Item).filter_by(t_itemName=item_name).one()
        categories = session.query(Category).all()
        for cati in categories:
            if cati.t_id == delete_item.t_catId:
                catx = cati

        if request.method == 'POST':
            session.delete(delete_item)
            session.commit()
            flash("item deleted")
            return  redirect(url_for('mainPage'))
        else:
            return render_template('deleteItem.html', current_item=delete_item, current_cat=catx, current_user=login_session['user_email'])
    else:
        return redirect(url_for('login'))

@app.route('/CatalogApp/JSON')
def allCatalogJSON():
    products = session.query(Item).all()
    return jsonify(allproducts=[p.serialize for p in products])    
    
if __name__ == '__main__':
    app.secret_key = 'do not share this baby'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
    