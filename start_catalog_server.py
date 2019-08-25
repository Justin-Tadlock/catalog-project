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

import google_authentication as gAuth

app = Flask(__name__)

# Add the secret key for the app
try:
    app.secret_key = open('secret_key.txt', 'r').read()
except IOError as ioe:
    print('Error: Please create a \'secret_key.txt\' file within the app\'s directory')
    print(ioe.pgerror)
    print(ioe.diag.message_detail)
    sys.exit(1)


# Add the client id to all templates
try:
    app.add_template_global(name='client_id', f=gAuth.CLIENT_ID)
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

    state = Generate_State_Token()

    return render_template(
        'index.html',
        title='Latest Items',
        main_categories=main_categories,
        sub_categories=sub_categories,
        items=items,
        state=state
    )

@app.route('/show/<int:main_cat_id>')
def Show_Category(main_cat_id):
    main_category = session.query(Category).filter_by(id=main_cat_id).one_or_none()
    main_categories = session.query(Category).all()
    sub_categories = session.query(Sub_Category).filter_by(cat_id=main_cat_id).all()
    items = session.query(Item).filter_by(cat_id=main_cat_id).all()

    return render_template(
        'show-category.html',
        title='Item Catalog - %s' % (main_category.name),
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
        category=main_category
    )


@app.route('/deleteCategory/<int:main_cat_id>')
def Delete_Category(main_cat_id):
    main_category = session.query(Category).filter_by(id=main_cat_id).one_or_none()

    return render_template(
        'delete-category.html',
        title="Item Catalog",
        category=main_category
    )

@app.route('/editSubCategory/<int:main_cat_id>/<int:sub_cat_id>')
def Edit_Sub_Category(main_cat_id, sub_cat_id):
    sub_category = session.query(Sub_Category).filter_by(id=sub_cat_id).one_or_none()

    return render_template(
        'edit-category.html',
        title="Item Catalog",
        category=sub_category,
        main_cat_id=main_cat_id
    )


@app.route('/deleteSubCategory/<int:main_cat_id>/<int:sub_cat_id>')
def Delete_Sub_Category(main_cat_id, sub_cat_id):
    sub_category = session.query(Sub_Category).filter_by(id=sub_cat_id).one_or_none()

    return render_template(
        'delete-category.html',
        title="Item Catalog",
        category=sub_category,
        main_cat_id=main_cat_id
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
