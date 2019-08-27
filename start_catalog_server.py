import psycopg2
import json
import random
import string
import httplib2
import requests
import bleach
import sys

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    make_response,
    flash,
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
    return dict(client_id=gAuth.CLIENT_ID,
                categories=session.query(Category).all(),
                state=Generate_State_Token(),
                authenticated=Is_Authenticated())


def Log(msg, err=False):
    if not err and app.debug:
        print('INFO: %s' % (msg))
    else:
        print('ERROR: %s' % (msg))


def Generate_State_Token():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits
        ) for x in range(32)
    )

    login_session['state'] = state

    return state


def Get_Category_IDs(form):
    # Get the item category string
    if form['item_category'] == 'Other':
        item_category = form['item_category_other']

        # Determine if we need to add the category to the db
        category = session.query(Category).filter_by(name=item_category).all()
        if category == []:
            session.add(Category(name=item_category))
            session.commit()

    else:
        item_category = form['item_category']

    # Get the cat_id of the category object from the db
    cat_id = session.query(Category).filter_by(name=item_category).one().id

    # Get the item sub category string
    if form['item_sub_category'] == 'Other':
        item_sub_category = form['item_sub_category_other']

        # Determine if we need to add the category to the db
        sub_category = session.query(Sub_Category).filter_by(
            name=item_sub_category).all()
        if sub_category == []:
            session.add(Sub_Category(name=item_sub_category, cat_id=cat_id))
            session.commit()
    else:
        item_sub_category = form['item_sub_category']

    # Get the sub_cat_id of the category object from the db
    sub_cat_id = session.query(Sub_Category).filter_by(
        name=item_sub_category, cat_id=cat_id).one().id

    return {
        'cat_id': cat_id,
        'cat_name': item_category,
        'sub_cat_id': sub_cat_id,
        'sub_cat_name': item_sub_category
    }


def Is_Authenticated():
    return ('user' in login_session)


def Logout_Session():
    if Is_Authenticated():
        print("Logging out the user")
        login_session.pop('user', None)
        login_session.pop('state', None)


def Get_User_Info(user_info):
    Log('Enter: Get_User_Info')

    user = session.query(User).filter_by(
        name=user_info.get('name'),
        email=user_info.get('email')
    ).one_or_none()

    if user is not None:
        Log('   Finding user %s... Found!' % (user.email))

        ret_info = {
            'name': user.name,
            'email': user.email,
            'picture': user.picture,
            'user_id': user.id
        }

        return ret_info
    else:
        Log('   Finding user %s... Not found! Adding user to db...' % (
            user_info.get('email')
        ))

        return Add_User(user_info)


def Add_User(user_info):
    Log('Enter: Add_User')

    try:
        new_user = User(
            name=user_info.get('name'),
            email=user_info.get('email'),
            picture=user_info.get('picture')
        )
        session.add(new_user)
        session.commit()

        return Get_User_Info(user_info)
    except Exception as e:
        Log('Unable to add new user.')
        Log(str(e))

        return None


@app.route('/authenticated')
def Authenticated():
    if Is_Authenticated():
        return make_response(
            jsonify(
                message="User is already logged in",
                status=200,
                data=True
            )
        )
    else:
        return make_response(
            jsonify(
                message="User is not logged in",
                status=200,
                data=False
            )
        )


@app.route('/gconnect', methods=['POST'])
def G_Login():
    print('Enter G_Login()')

    if 'state' in request.form:
        if request.form['state'] != login_session['state']:
            return redirect(url_for('Index'))

        if not Is_Authenticated():
            print('Attempt to log in to Google...')
            user_json = gAuth.Google_Callback()

            if user_json:
                user_data = json.loads(user_json)

                # If we don't have the user in our db, add them.
                if Get_User_Info(user_data) is None:
                    return make_response(
                        jsonify(
                            message="Could not log the user in",
                            status=501
                        )
                    )
                else:
                    login_session['user'] = user_data
            else:
                Logout_Session()

            return make_response(jsonify(
                message="Successfully logged in. Reload the page.",
                status=200,
                data=True
            ))
        else:
            return make_response(jsonify(
                message="Already logged in",
                status=200,
                data=False
            ))
    else:
        print('Error: \'state\' is not within the request')

        return redirect(url_for('Index'))


@app.route('/logout', methods=['POST'])
def Logout():
    Logout_Session()

    return make_response(
        jsonify(
            message="User logged out",
            status=200,
            data="Logged Out"
        )
    )


@app.route('/')
def Index():
    items = session.query(Item).order_by(Item.id.desc()).limit(10).all()

    return render_template(
        'index.html',
        title='Latest Items',
        items=items
    )


@app.route('/show/<int:main_cat_id>')
def Show_Category(main_cat_id):
    main_category = session.query(Category).filter_by(
        id=main_cat_id).one_or_none()
    sub_categories = session.query(
        Sub_Category).filter_by(cat_id=main_cat_id).all()
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
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )
    
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


@app.route('/editCategory/<int:main_cat_id>', methods=['GET', 'POST'])
def Edit_Category(main_cat_id):
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    category = session.query(Category).filter_by(id=main_cat_id).one_or_none()

    if request.method == 'POST':
        if category and login_session['user']['id'] == category.user_id:
            form = request.form

            category.name = form['category_name']

            session.add(category)
            session.commit()
        else:
            flash("You don't have the right access to edit %s" %
                  (category.name))

        return redirect(url_for('Index'))

    return render_template(
        'edit-category.html',
        title="Item Catalog",
        category=category
    )


@app.route('/deleteCategory/<int:main_cat_id>', methods=['GET', 'POST'])
def Delete_Category(main_cat_id):
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    category = session.query(Category).filter_by(id=main_cat_id).one_or_none()

    if request.method == 'POST':
        if category and login_session['user']['id'] == category.user_id:
            session.delete(category)
            session.commit()
        else:
            flash("You don't have the right access to delete %s" %
                  (category.name))

        return redirect(url_for('Index'))

    return render_template(
        'delete-category.html',
        title="Item Catalog",
        category=category
    )


@app.route('/editSubCategory/<int:main_cat_id>/<int:sub_cat_id>', 
           methods=['GET', 'POST'])
def Edit_Sub_Category(main_cat_id, sub_cat_id):
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    sub_category = session.query(Sub_Category).filter_by(
        id=sub_cat_id).one_or_none()

    if request.method == 'POST':
        if (sub_category and 
            login_session['user']['id'] == sub_category.user_id):
            form = request.form

            sub_category.name = form['category_name']

            session.add(sub_category)
            session.commit()

            items = session.query(Item).filter_by(
                sub_cat_id=sub_category.id).all()
            for item in items:
                item.sub_category = form['category_name']

                session.add(item)
                session.commit()
        else:
            flash("You don't have the right access to edit %s" %
                  (sub_category.name))

        return redirect(url_for('Show_Category', main_cat_id=main_cat_id))

    return render_template(
        'edit-category.html',
        title="Item Catalog",
        category=sub_category,
        main_cat_id=main_cat_id
    )


@app.route('/deleteSubCategory/<int:main_cat_id>/<int:sub_cat_id>', 
           methods=['GET', 'POST'])
def Delete_Sub_Category(main_cat_id, sub_cat_id):
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    sub_category = session.query(Sub_Category).filter_by(
        id=sub_cat_id).one_or_none()

    if request.method == 'POST':
        if (sub_category and 
            login_session['user']['id'] == sub_category.user_id):
            
            session.query(Item).filter_by(sub_cat_id=sub_cat_id).delete()

            session.query(Sub_Category).filter_by(id=sub_cat_id).delete()

            session.commit()
        else:
            flash("You don't have the right access to delet %s" %
                  (sub_category.name))

        return redirect(url_for('Show_Category', main_cat_id=main_cat_id))

    return render_template(
        'delete-category.html',
        title="Item Catalog",
        category=sub_category,
        main_cat_id=main_cat_id
    )


@app.route('/addItem/<int:main_id>/<int:sub_id>', methods=['GET', 'POST'])
@app.route('/addItem/<int:main_id>', methods=['GET', 'POST'])
@app.route('/addItem', methods=['GET', 'POST'])
def Add_Item(main_id=None, sub_id=None):
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    if request.method == 'POST':
        form = request.form

        # Get the category names and IDs based on selected fields in the form.
        cat_data = Get_Category_IDs(form)

        # Add the item to the db
        session.add(
            Item(
                name=form['item_name'],
                price=form['item_price'],
                category=cat_data['cat_name'],
                sub_category=cat_data['sub_cat_name'],
                description=form['item_description'],
                cat_id=cat_data['cat_id'],
                sub_cat_id=cat_data['sub_cat_id']
            )
        )
        session.commit()

        return redirect(
            url_for(
                'Show_Category', 
                main_cat_id=cat_data['cat_id']
            )
        )

    sub_categories = session.query(Sub_Category).all()

    return render_template(
        'add-item.html',
        main_id=main_id,
        sub_id=sub_id,
        sub_categories=sub_categories
    )


@app.route('/editItem/<int:item_id>', methods=['GET', 'POST'])
def Edit_Item(item_id):
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    item = session.query(Item).filter_by(id=item_id).one_or_none()

    if request.method == 'POST':
        if item and login_session['user']['id'] == item.user_id:
            form = request.form

            # Get the category names and IDs based on 
            # selected fields in the form.
            cat_data = Get_Category_IDs(form)

            # Update the item's data.
            item.name = form['item_name']
            item.price = form['item_price']
            item.category = cat_data['cat_name']
            item.sub_category = cat_data['sub_cat_name']
            item.description = form['item_description']
            item.cat_id = cat_data['cat_id']
            item.sub_cat_id = cat_data['sub_cat_id']

            # Update the db
            session.add(item)
            session.commit()
        else:
            flash("You don't have the right access to edit %s" % (item.name))

        return redirect(
            url_for(
                'Show_Category', 
                main_cat_id=item.cat_id
            )
        )

    sub_categories = session.query(Sub_Category).all()

    return render_template(
        'edit-item.html',
        item=item,
        sub_categories=sub_categories
    )


@app.route('/deleteItem/<int:item_id>', methods=['GET', 'POST'])
def Delete_Item(item_id):
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    item = session.query(Item).filter_by(id=item_id).one_or_none()

    if request.method == 'POST':
        if item and login_session['user']['id'] == item.user_id:
            session.delete(item)
            session.commit()
        else:
            flash("You don't have the right access to delete %s" % (item.name))

        return redirect(
            url_for(
                'Show_Category', 
                main_cat_id=item.cat_id
            )
        )

    return render_template(
        'delete-item.html',
        item=item
    )


# API Functions


@app.route('/api/all/categories')
def API_All_Categories():
    categories = session.query(Category).all()

    return jsonify(
        Category=[
            category.serialize for category in categories
        ]
    )


@app.route('/api/all/subCategories')
def API_All_Sub_Categories():
    categories = session.query(Sub_Category).all()

    return jsonify(
        Category=[
            category.serialize for category in categories
        ]
    )


@app.route('/api/all/items')
def API_All_Items():
    items = session.query(Item).all()

    return jsonify(
        Item=[
            item.serialize for item in items
        ]
    )


@app.route('/api/category/<int:main_cat_id>')
def API_Category_Items(main_cat_id):
    items = session.query(Item).filter_by(cat_id=main_cat_id).all()

    return jsonify(
        Item=[
            item.serialize for item in items
        ]
    )


@app.route('/api/subCategory/<int:sub_cat_id>')
def API_Sub_Category_Items(sub_cat_id):
    items = session.query(Item).filter_by(sub_cat_id=sub_cat_id).all()

    return jsonify(
        Item=[
            item.serialize for item in items
        ]
    )


@app.route('/api/item/<int:item_id>')
def API_Item(item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()

    return jsonify(Item=item.serialize)


@app.route('/api/all/users')
def API_All_Users():
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    users = session.query(User).all()

    return jsonify(
        User=[
            user.serialize for user in users
        ]
    )


if __name__ == "__main__":
    # Add the secret key for the app
    try:
        app.secret_key = open('secret_key.txt', 'r').read()
    except IOError as ioe:
        print('Error: Please create a \'secret_key.txt\' '
              'file within the app\'s directory')
        print(ioe.pgerror)
        print(ioe.diag.message_detail)
        sys.exit(1)

    # Adding db functionality for CRUD operations
    engine = create_engine('sqlite:///item_catalog.db?check_same_thread=False')
    DBsession = sessionmaker(bind=engine)
    session = DBsession()

    app.debug = True
    app.run(
        ssl_context=('cert.pem', 'key.pem'),
        host="0.0.0.0",
        port=5000
    )
