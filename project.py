from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from data_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/')
    return decorated_function

@app.route('/')
def Category_menu():
    # login_session.clear()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    latest_items = session.query(Item).order_by(Item.id.desc()).all()
    if 'username' not in login_session:
        return render_template('index.html', categories=categories, latest_items=latest_items, STATE=state)
    else:
    	return render_template('login.html', categories=categories, latest_items=latest_items)

@app.route('/catalog/<string:category_name>/items')
def Category_items(category_name):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    curr_category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category=curr_category)
    if 'username' not in login_session:
        return render_template('catalog_category_items.html', categories=categories,
                               items=items, category_name=category_name,
                               STATE=state)
    else:
        return render_template('catalog_category_items_login.html', categories=categories,
                               items=items, category_name=category_name)
	

@app.route('/catalog/<string:category_name>/<string:item_name>')
def Item_description(category_name, item_name):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    item = session.query(Item).filter_by(name=item_name).one_or_none()
    if item is None:
        return render_template('404.html')
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session:
        return render_template('item_description_nologin.html', item=item, STATE=state,
                               creator=creator)
    elif creator.id != login_session['user_id']:
        return render_template('item_description_not_ED.html', item=item,
                               creator=creator)
    else:
        return render_template('item_description.html', item=item,
                               creator=creator)
	

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return Category_menu()
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@login_required
@app.route('/catalog/add/', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        user = getUserInfo(login_session['user_id'])
        category_name = request.form['genre']
        category = session.query(Category).filter_by(name=str(category_name)).one()
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category=category, user_id=login_session['user_id'],
                       user=user)
        session.add(newItem)
        session.commit()
        flash("New item created!")
        return redirect(url_for('Category_menu'))
    else:
        return render_template('add_item.html')

@login_required
@app.route('/catalog/<string:item_name>/delete/', methods=['GET', 'POST'])
def delete_item(item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    if item.user_id == login_session['user_id']:
        if request.method == 'POST' and request.form['submit'] == 'Delete':
            session.delete(item)
            session.commit()
            flash("Item has been deleted.")
            return redirect(url_for('Category_menu'))
        elif request.method == 'POST' and request.form['submit'] == 'Cancel':
            return redirect(url_for('Category_menu'))
        else:
        	return render_template('delete_item.html', item_name=item.name)
    else:
        redirect(url_for('Category_menu'))

@login_required
@app.route('/catalog/<string:item_name>/edit/', methods=['GET', 'POST'])
def edit_item(item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    if item.user_id == login_session['user_id']:
        if request.method == 'POST':
            if request.form['name']:
                item.name = request.form['name']
            if request.form['description']:
                item.description = request.form['description']
            category_name = request.form['genre']
            category = session.query(Category).filter_by(name=str(category_name)
                                                         ).one()
            item.category = category
            session.add(item)
            session.commit()
            flash("Item has been edited.")
            return redirect(url_for('Category_menu'))
        else:
            return render_template('edit_item.html', item_name=item.name)
    else:
        redirect(url_for('Category_menu'))

@app.route('/catalog.json')
def json_func():
    rand = random.randrange(0, session.query(Item).count())
    ran_item = session.query(Item)[rand]
    return jsonify(ran_item.serialize)


@app.route('/catalog.json/all_items/')
def json_all_items():
    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)