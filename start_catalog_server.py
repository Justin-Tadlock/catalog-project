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
    render_template,
    session as login_session,
    jsonify
)

from database_setup import Base, User, Category, Sub_Category, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import google_authentication as gAuth

app = Flask(__name__)


@app.context_processor
def Update_Side_Nav():
    return dict(client_id=gAuth.CLIENT_ID, categories=session.query(Category).all())

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
    items = session.query(Item).order_by(Item.id.desc()).limit(10).all()
    state = Generate_State_Token()

    return render_template(
        'index.html',
        title='Latest Items',
        items=items,
        state=state
    )


@app.route('/show/<int:main_cat_id>')
def Show_Category(main_cat_id):
    main_category = session.query(Category).filter_by(id=main_cat_id).one_or_none()
    sub_categories = session.query(Sub_Category).filter_by(cat_id=main_cat_id).all()
    items = session.query(Item).filter_by(cat_id=main_cat_id).all()

    return render_template(
        'show-category.html',
        title='Item Catalog - %s' % (main_category.name),
        main_category=main_category,
        sub_categories=sub_categories,
        items=items
    )


@app.route('/addCategory', methods=['GET', 'POST'])
def Add_Category():
    if request.method == 'POST':
        form = request.form

        new_cat = Category(name=form['category_name'])
        session.add(new_cat)
        session.commit()

        Update_Side_Nav()

        return redirect(url_for('Index'))

    return render_template(
        'add-category.html',
        title="Item Catalog",
    )


@app.route('/editCategory/<int:main_cat_id>', methods=['GET','POST'])
def Edit_Category(main_cat_id):
    category = session.query(Category).filter_by(id=main_cat_id).one_or_none()

    if request.method == 'POST':
        if category:
            form = request.form

            category.name = form['category_name']

            session.add(category)
            session.commit()

        return redirect(url_for('Index'))

    return render_template(
        'edit-category.html',
        title="Item Catalog",
        category=category
    )


@app.route('/deleteCategory/<int:main_cat_id>', methods=['GET','POST'])
def Delete_Category(main_cat_id):
    category = session.query(Category).filter_by(id=main_cat_id).one_or_none()

    if request.method == 'POST':
        if category:
            session.delete(category)
            session.commit()

        return redirect(url_for('Index'))

    return render_template(
        'delete-category.html',
        title="Item Catalog",
        category=category
    )


@app.route('/editSubCategory/<int:main_cat_id>/<int:sub_cat_id>', methods=['GET','POST'])
def Edit_Sub_Category(main_cat_id, sub_cat_id):
    sub_category = session.query(Sub_Category).filter_by(id=sub_cat_id).one_or_none()

    if request.method == 'POST':
        if sub_category:
            form = request.form

            sub_category.name = form['category_name']

            session.add(sub_category)
            session.commit()

            items = session.query(Item).filter_by(sub_cat_id=sub_category.id).all()
            for item in items:
                item.sub_category = form['category_name']
                
                session.add(item)
                session.commit()
        
        return redirect(url_for('Show_Category', main_cat_id=main_cat_id))

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
    return render_template(
        'add-item.html',
        main_id=main_id,
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


# API Functions


@app.route('/api/all/categories')
def API_All_Categories():
    categories = session.query(Category).all()

    return jsonify(Category=[category.serialize for category in categories])


@app.route('/api/all/subCategories')
def API_All_Sub_Categories():
    categories = session.query(Sub_Category).all()

    return jsonify(Category=[category.serialize for category in categories])


@app.route('/api/all/items')
def API_All_Items():
    items = session.query(Item).all()

    return jsonify(Item=[item.serialize for item in items])


@app.route('/api/category/<int:main_cat_id>')
def API_Category_Items(main_cat_id):
    items = session.query(Item).filter_by(cat_id=main_cat_id).all()

    return jsonify(Item=[item.serialize for item in items])


@app.route('/api/subCategory/<int:sub_cat_id>')
def API_Sub_Category_Items(sub_cat_id):
    items = session.query(Item).filter_by(sub_cat_id=sub_cat_id).all()

    return jsonify(Item=[item.serialize for item in items])


@app.route('/api/item/<int:item_id>')
def API_Item(item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()

    return jsonify(Item=item.serialize)



if __name__ == "__main__":
    # Add the secret key for the app
    try:
        app.secret_key = open('secret_key.txt', 'r').read()
    except IOError as ioe:
        print('Error: Please create a \'secret_key.txt\' file within the app\'s directory')
        print(ioe.pgerror)
        print(ioe.diag.message_detail)
        sys.exit(1)

    # Adding db functionality for CRUD operations
    engine = create_engine('sqlite:///item_catalog.db?check_same_thread=False')
    DBsession = sessionmaker(bind=engine)
    session = DBsession()
        
   

    app.debug = True
    app.run(host="0.0.0.0", port=5000)
