#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------python functinality imports----------------------------------

from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash, g, abort
from flask import session as login_session
import random
import string
import httplib2
import json
from flask import make_response
import requests
import re
import bleach
from functools import wraps


# --------------------------------------------------------

# ----------- google sign in -----------------------------

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# --------------------------------------------------------

# ------------------------- DB imports---------------------

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Category, Item

# ---------------------------------------------------------


# ---------------------------------------------------------

app = Flask(__name__)

# connect to the data base and create a session-----------

engine = create_engine('sqlite:///catalogApp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# ---------------------------------------------------------

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/')
@app.route('/CatalogApp')
def mainPage():
    """This is the start function loads the main page for the catalog app if the user is
    authenticated then loads item adding, editing and deleting; if the user is not the public
    version only for viewing

    Returns:
        html -- renders the onw of two versions of the catalog app
    """

    if 'user_email' in login_session:
        print(login_session['user_email'])
        categories = session.query(Category).all()
        latestItems = \
            session.query(Item).order_by(desc(Item.t_id)).limit(7)
        return render_template('privateMain.html',
                               mainCategories=categories,
                               mainItems=latestItems,
                               current_user=login_session['user_email'],
                               session_type=login_session['type'],
                               user_id=login_session['user_id'])
    else:
        print('nothing in login session')
        categories = session.query(Category).all()
        latestItems = \
            session.query(Item).order_by(desc(Item.t_id)).limit(7)
        return render_template('publicMain.html',
                               mainCategories=categories,
                               mainItems=latestItems)


def login_required(f):
    @wraps(f)
    def decorated_funcion(*args, **kwargs):
        if login_session['user_email'] is not None:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login', provider='local'))
    return decorated_funcion


@app.route('/clientOAuth/<provider>', methods=['POST'])
def login(provider):
    """This function starts the authentication process whether is local or with
    google's aouth 2, after the user has been authenticated login_session will
    populated with the user information to control access.

    Arguments:
        provider {string} -- the html will send in the request a string local or
        google to determine the authentication path

    Returns:
        render_template -- renders the html page according with the type of login
    """

    if provider == 'local':
        username = request.form['usermail']
        password = request.form['userpass']
        user = session.query(User).filter_by(t_email=username).first()
        if user and user.verify_password(password):
            #current_user = g.user
            categories = session.query(Category).all()
            latestItems = \
                session.query(Item).order_by(desc(Item.t_id)).limit(7)

            login_session['user_name'] = user.t_name
            login_session['user_email'] = user.t_email
            login_session['user_picture'] = user.t_picture
            login_session['user_id'] = user.t_id
            login_session['type'] = 'local'

            flash('welcome', category='info')

            return render_template('privateMain.html',
                                   mainCategories=categories,
                                   mainItems=latestItems,
                                   current_user=user.t_email,
                                   session_type=login_session['type'],
                                   user_id=login_session['user_id'])
        else:
            print('Error in login credentials')
            return render_template('login.html')

    elif provider == 'google':
        print("entered the google domain of garubage")
        categories = session.query(Category).all()
        latestItems = \
            session.query(Item).order_by(desc(Item.t_id)).limit(7)
        auth_code = request.data
        # this data  $.ajax({...... data: authResult['code'],
        print("auth_code recieved from google: %s" % auth_code)
        try:
            # upgrade the authorization code into credentials
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
            response.headers['Content-Type'] = 'applicacion/json'
            return response

        # check if the access token is valid
        access_token = credentials.access_token
        print("credentials.access_token: %s" % access_token)
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # if there was an error in the access token info, abort
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        # verify that the access token is used for the intended user
        gplus_id = credentials.id_token['sub']
        print('this is gplus_id: %s' % gplus_id)

        if result['user_id'] != gplus_id:
            response = \
                make_response(json.dumps("Token's user Id doesn't match with given user ID"), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # verify that the access token is valid for this app
        if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("token's client ID does not match app's"), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # check if the user is already connected REVIEW
        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        print('step 2 complete! Access token: %s' % credentials.access_token)

        # get user info
        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        # https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=youraccess_token
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
        print("the answer is....%s" % answer)
        data = answer.json()
        # A
        name = data['name']
        picture = data['picture']
        email = data['email']

        # check if the user already exists if not add him or her
        user = session.query(User).filter_by(t_email=email).first()
        if not user:
            user = User(t_name=name, t_email=email, t_picture=picture)
            session.add(user)
            session.commit()

        login_session['user_name'] = name
        login_session['user_email'] = email
        login_session['user_picture'] = picture
        login_session['user_id'] = user.t_id
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id
        login_session['type'] = 'google'

        return render_template('privateMain.html',
                                mainCategories=categories,
                                mainItems=latestItems,
                                current_user=login_session['user_email'],
                                session_type=login_session['type'],
                                user_id=login_session['user_id'])

    else:
        return 'unssuported provider'

@app.route('/gdisconnect')
def gdisconnect():
    """Removes user from login_session and revokes token from google
    """

    print('im working here...../gdisconnect')
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access token is none')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s' % access_token)
    print('user name is: %s' % login_session['user_name'])

    # execute a GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('the result is %s' % result)
    if result['status'] == '200':
        del login_session['user_name']
        del login_session['user_email']
        del login_session['user_picture']
        del login_session['user_id']
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('mainPage'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user'), 200)
        response.headers['Content-Type'] = 'application/json'

@app.route('/start')
def start():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Removes user from login_session
    """

    # remove the user email from the session
    login_session.clear()
    return redirect(url_for('mainPage'))


@app.route('/users', methods=['POST'])
def new_user():
    """creates a new local user, removes from the input ['/'] character also
    using bleach cleans the input from html, styles, etc. code

    Returns:
        render_template -- loads the login.html after the user is succesfully added to the DB
    """

    if request.method == 'POST':
        if session.query(User).filter_by(t_email=request.form['newusermail']).first():
            return "User already in Database"
        else:
            at_user = User(t_name=bleach.clean(request.form['newusername'], tags=[], attributes={}, styles=[], strip=True),
                       t_email=bleach.clean(request.form['newusermail'], tags=[], attributes={}, styles=[], strip=True),
                       t_picture='Nothing at all nothing at all')
            at_user.hash_password(request.form['newuserpass'])
            session.add(at_user)
            session.commit()
            flash('User added to the DB you can login now', category = 'info')
            return redirect('/start')
    else:
        print('this is by default the first action its a GET request')
        return render_template('login.html')


@app.route('/CatalogApp/<path:category_name>/items', methods=['GET', 'POST'])
def catPage(category_name):
    """Renders a specific category page page which displays the last 7 items added
    also checks if the user is in the login_session before anything else.

    Arguments:
        category_name {string} -- this string is used to search in the database the
        specific tagegory and load its items

    Returns:
        render_template -- renders the html of a particular category and all its items
    """

    if 'user_email' in login_session:
        categories = session.query(Category).all()
        for cati in categories:
            if cati.t_catName == category_name:
                catx = cati.t_id

        latestItems = session.query(Item).filter_by(t_catId=catx)
        totalItems = session.query(Item).filter_by(t_catId=catx).count()

        return render_template(
            'categoryX.html',
            catpageCatName=category_name,
            catpageItems=latestItems,
            catpageCategories=categories,
            t_items=totalItems,
            current_user=login_session['user_email'],
            session_type=login_session['type'],
            user_id=login_session['user_id']
            )
    else:
        print('there is nothin is login session')
        categories = session.query(Category).all()
        for cati in categories:
            if cati.t_catName == category_name:
                catx = cati.t_id

        latestItems = session.query(Item).filter_by(t_catId=catx)
        totalItems = session.query(Item).filter_by(t_catId=catx).count()
        print(totalItems)
        return render_template('publicCategoryX.html',
                               catpageCatName=category_name,
                               catpageItems=latestItems,
                               catpageCategories=categories,
                               t_items=totalItems)


@app.route('/CatalogApp/<path:category_name>/new_item', methods=['GET', 'POST'])
@login_required
def newItemPage(category_name):
    """Add a new item for a specific category to the DB

    Arguments:
        category_name {string} -- variable containing the category name

    Returns:
        render_template -- renders the html page for new item add
    """

    if 'user_email' in login_session:
        categories = session.query(Category).all()
        for cati in categories:
            if cati.t_catName == category_name:
                catx = cati.t_id

        if request.method == 'POST':
            item_name = request.form['item_name']
            item_desc = request.form['i_description']
            if session.query(Item).filter_by(t_itemName=item_name).first():
                return "item already exists"
            else:
                new_item = Item(t_itemName=bleach.clean(item_name, tags=[], attributes={},
                                                    styles=[], strip=True),
                            t_itemDescription=bleach.clean(item_desc, tags=[], attributes={},
                                                            styles=[], strip=True),
                            t_userId=login_session['user_id'], t_catId=catx)
                session.add(new_item)
                session.commit()
                flash('new item added to the database')
                return redirect(url_for('mainPage'))
        else:

            # the method used in this call is GET

            print('this is a get call')
            return render_template('newItem.html',
                                   current_cat=category_name,
                                   current_user=login_session['user_email'],
                                   session_type=login_session['type'])
    else:
        return redirect(url_for('login'))


@app.route('/CatalogApp/<path:category_name>/<item_name>', methods=['GET', 'POST'])
def itemPage(category_name, item_name):
    """Displays the item page renders the edit and delete buttons if the
    user is the owner the item object
    
    Arguments:
        category_name {string} -- [description]
        item_name {string} -- [description]
    
    Returns:
        render_template -- renders the item description page also sends the user_id from
        login_session to determine if the logged user can edit, delete or just view the
        item
    """

    if 'user_email' in login_session:
        itemX = \
            session.query(Item).filter_by(t_itemName=item_name).first()

        return render_template('itemDesc.html', itempage=itemX,
                               category_name=category_name,
                               current_user=login_session['user_email'],
                               session_type=login_session['type'],
                               user_id=login_session['user_id'])
    else:
        itemX = \
            session.query(Item).filter_by(t_itemName=item_name).first()

        return render_template('publicItemDesc.html', itempage=itemX,
                               category_name=category_name)


@app.route('/CatalogApp/<path:item_name>/edit', methods=['GET', 'POST'])
@login_required
def editItemPage(item_name):
    """If the logged user is the owner of the item he can edit it
    
    Arguments:
        item_name {string} -- item name for querying the DB
    
    Returns:
        render_template -- after the has been modified and added to the BD
        the user is redirect to the main page
    """
    edit_item = session.query(Item).filter_by(t_itemName=item_name).one_or_none()
    categories = session.query(Category).all()
    if ('user_email' in login_session) and (edit_item.t_userId == login_session['user_id']):     
        for cati in categories:
            if cati.t_id == edit_item.t_catId:
                catx = cati

        if request.method == 'POST':
            # values received

            edit_item.t_itemName = bleach.clean(request.form['newItemName'],
                                                tags=[], attributes={}, styles=[], strip=True)
            edit_item.t_itemDescription = bleach.clean(request.form['newDescription'],
                                                       tags=[], attributes={}, styles=[], strip=True)
            edit_item.t_userId = login_session['user_id']
            edit_item.t_catId = int(request.form['categories'])
            if session.query(Item).filter_by(t_itemName=bleach.clean(request.form['newItemName'])).first():
                return "This item already exist in the DB or your are using the same name again"
            else:
                session.add(edit_item)
                session.commit()
                flash('item edited')
                return redirect(url_for('mainPage'))
        else:

            print('this is the GET call and its the first part to run')
            return render_template('editItem.html',
                                   current_item=edit_item,
                                   current_cat=catx,
                                   current_user=login_session['user_email'],
                                   session_type=login_session['type'],
                                   user_id = login_session['user_id'])

        return "render_template('itemDesc.html') "
    else:
        response = make_response(json.dumps('The resource requested is Forbidden'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/CatalogApp/<path:item_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteItemPage(item_name):
    """Deletes a selected item from the DB
    
    Arguments:
        item_name {string} -- string describing the item's name
    
    Returns:
        render_template -- after the item is deleted renders the main page
    """
    delete_item = session.query(Item).filter_by(t_itemName=item_name).one_or_none()
    categories = session.query(Category).all()
    if ('user_email' in login_session) and (delete_item.t_userId == login_session['user_id']):

        for cati in categories:
            if cati.t_id == delete_item.t_catId:
                catx = cati

        if request.method == 'POST':
            session.delete(delete_item)
            session.commit()
            flash('item deleted')
            return redirect(url_for('mainPage'))
        else:
            return render_template('deleteItem.html',
                                   current_item=delete_item,
                                   current_cat=catx,
                                   current_user=login_session['user_email'],
                                   session_type=login_session['type'])
    else:
        response = make_response(json.dumps('The resource requested is Forbidden'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/CatalogApp/JSON/all_items')
def allCatalogJSON():
    products = session.query(Item).all()
    return jsonify(allproducts=[p.serialize for p in products])

@app.route('/CatalogApp/JSON/<item_name>')
def x_item(item_name):
    itemX = session.query(Item).filter_by(t_itemName=item_name).first()
    return jsonify(item=itemX.serialize)

if __name__ == '__main__':
    app.secret_key = 'do not share this baby'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

