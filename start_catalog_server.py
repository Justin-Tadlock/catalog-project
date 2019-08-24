import psycopg2
import json
import random, string
import httplib2, requests, bleach
import sys

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    make_response,
    render_template
)

from database_setup import Base, User, Category, Sub_Category, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)

# Add the secret key for the app
try:
    app.secret_key = open('secret_key.txt', 'r').read()
except IOError as ioe:
    print('Error: Please create a \'secret_key.txt\' file within the app\'s directory')
    print(ioe.pgerror)
    print(ioe.diag.message_detail)
    sys.exit(1)


# Get Secrets Data
try:
    SECRET_DATA = json.loads(open('client_secrets.json', 'r').read())['web']
    CLIENT_ID = SECRET_DATA['client_id']
    CLIENT_SECRET = SECRET_DATA['client_secret']

    # Get the redirect uri from the file in the form of '/url'
    CLIENT_REDIRECT = SECRET_DATA['redirect_uris'][0]
    CLIENT_REDIRECT = '/%s' % (CLIENT_REDIRECT.split('/')[-1])
except:
    print('ERROR: Please download your \'client_secrets.json\' file from your \'https://console.developers.google.com\' project')


# Add the client id to all templates
try:
    app.add_template_global(name='client_id', f=CLIENT_ID)
except:
    print('ERROR: Could not add jinja2 global client id variable')

# Adding db functionality for CRUD operations
engine = create_engine('sqlite:///item_catalog.db?check_same_thread=False')
DBsession = sessionmaker(bind=engine)
session = DBsession()


def Log(msg, err=False):
    if not err and app.debug:
        print('INFO: %s' % (msg))
    else:
        print('ERROR: %s' % (msg))


def Generate_State_Token():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state


@app.route('/')
def Index():
    main_categories = session.query(Category).all()
    sub_categories = session.query(Sub_Category).all()
    items = session.query(Item).order_by(Item.id.desc()).limit(10).all()

    return render_template(
        'index.html',
        title='Item Catalog',
        main_categories=main_categories,
        sub_categories=sub_categories,
        items=items
    )

@app.route('/show/<int:main_cat_id>')
def Show_Category(main_cat_id):
    main_category = session.query(Category).filter_by(id=main_cat_id).one_or_none()
    main_categories = session.query(Category).all()
    sub_categories = session.query(Sub_Category).filter_by(cat_id=main_cat_id).all()
    items = session.query(Item).filter_by(cat_id=main_cat_id).all()

    return render_template(
        'show-category.html',
        title='Item Catalog',
        main_category=main_category,
        main_categories=main_categories,
        sub_categories=sub_categories,
        items=items
    )

@app.route('/addCategory')
def Add_Category():
    return render_template(
        'add-category.html',
        title="Item Catalog"
    )


@app.route('/editCategory/<int:main_cat_id>')
def Edit_Category(main_cat_id):
    main_category = session.query(Category).filter_by(id=main_cat_id).one_or_none()

    return render_template(
        'edit-category.html',
        title="Item Catalog",
        main_category=main_category
    )


@app.route('/deleteCategory/<int:main_cat_id>')
def Delete_Category(main_cat_id):
    main_category = session.query(Category).filter_by(id=main_cat_id).one_or_none()

    return render_template(
        'delete-category.html',
        title="Item Catalog",
        main_category=main_category
    )


@app.route('/addItem/<int:main_id>/<int:sub_id>')
@app.route('/addItem/<int:main_id>')
@app.route('/addItem')
def Add_Item(main_id=None, sub_id=None):
    main_categories = session.query(Category).all()
    sub_categories = session.query(Sub_Category).all()

    return render_template(
        'add-item.html', 
        main_categories=main_categories, 
        main_id=main_id,
        sub_categories=sub_categories,
        sub_id=sub_id
    )

@app.route('/deleteItem/<int:item_id>')
def Delete_Item(item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()

    return render_template(
        'delete-item.html', 
        item=item
    )

@app.route('/editItem/<int:item_id>')
def Edit_Item(item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    main_categories = session.query(Category).all()
    sub_categories = session.query(Sub_Category).all()

    return render_template(
        'edit-item.html', 
        item=item,
        main_categories=main_categories,
        sub_categories=sub_categories
    )


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
