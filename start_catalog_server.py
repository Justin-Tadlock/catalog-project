import psycopg2
import json
import random
import string
import httplib2
import requests
import bleach
import sys
import platform

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
    # Function to update template variables
    return dict(client_id=gAuth.CLIENT_ID,
                categories=session.query(Category).all(),
                state=Generate_State_Token(),
                authenticated=Is_Authenticated())


def Log(msg, err=False):
    # Function for ease of debugging
    if not err and app.debug:
        print('INFO: %s' % (msg))
    else:
        print('ERROR: %s' % (msg))


def Generate_State_Token():
    # Function to generate a state token to help prevent CSRF attacks
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits
        ) for x in range(32)
    )

    login_session['state'] = state

    return state


def Get_Category_IDs(form):
    # Function used to determine if a category and/or sub categories
    # need to be added to the db, then it assigns the category names
    # to strings so that they can be used when adding/editing items.

    # Get the item category string
    if form['item_category'] == 'Other':
        item_category = form['item_category_other']

        # Add the category to the db if it doesn't currently exist
        category = session.query(
            Category
        ).filter_by(
            name=item_category
        ).all()
        if category == []:
            session.add(
                Category(
                    name=item_category,
                    user_id=login_session['user']['user_id']
                )
            )
            session.commit()

    else:
        item_category = form['item_category']

    # Get the cat_id of the category object from the db
    cat_id = session.query(
        Category
    ).filter_by(
        name=item_category
    ).one().id

    # Get the item sub category string
    if form['item_sub_category'] == 'Other':
        item_sub_category = form['item_sub_category_other']

        # Add the category to the db if it doesn't currently exist
        sub_category = session.query(
            Sub_Category
        ).filter_by(
            name=item_sub_category
        ).all()

        if sub_category == []:
            session.add(
                Sub_Category(
                    name=item_sub_category,
                    cat_id=cat_id,
                    user_id=login_session['user']['user_id']
                )
            )
            session.commit()
    else:
        item_sub_category = form['item_sub_category']

    # Get the sub_cat_id of the category object from the db
    sub_cat_id = session.query(
        Sub_Category
    ).filter_by(
        name=item_sub_category,
        cat_id=cat_id
    ).one().id

    return {
        'cat_id': cat_id,
        'cat_name': item_category,
        'sub_cat_id': sub_cat_id,
        'sub_cat_name': item_sub_category
    }


def Is_Authenticated():
    # Function to check is a user is logged in
    return ('user' in login_session)


def Logout_Session():
    # Function to remove user and state tokens from the login_session
    if Is_Authenticated():
        print("Logging out the user")
        login_session.pop('user', None)
        login_session.pop('state', None)

def Get_Glb_Session():
    global session

    return session


def Get_User_Info(user_info):
    # Function to check if a user is within the db
    # If the user is not, then we attempt to add the user.
    # If the add is successful, we then grab the user data from the db
    # and return it.
    session = Get_Glb_Session()

    # Attempt to grab the user data from the db
    user = session.query(User).filter_by(
        name=user_info.get('name'),
        email=user_info.get('email')
    ).one_or_none()

    # Return data if successful
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
        # Attempt to add the user to the db and return that data
        # if the user does not exist.
        Log('   Finding user %s... Not found! Adding user to db...' % (
            user_info.get('email')
        ))

        return Add_User(user_info)


def Add_User(user_info):
    # Function for attempting to add the user data to the db.
    # Will return null if the attempt is unsuccessful
    session = Get_Glb_Session()

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
    # Function used to respond to requests to see if the user is logged in.
    # This is intended for requests through js.
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
    # Function for authenticating using Google Sign-in
    print('Enter G_Login()')

    # Check for state tokens to match for preventing CSRF attacks.
    if 'state' in request.form:
        if request.form['state'] != login_session['state']:
            return redirect(url_for('Index'))

        # Check if the user is already logged in.
        if not Is_Authenticated():
            print('Attempt to log in to Google...')
            user_json = gAuth.Google_Callback()

            # Check for login verified data from Google
            if user_json:
                user_data = json.loads(user_json)

                # Attempt to get the user data from the db
                if Get_User_Info(user_data) is None:
                    # The attempt to get/add the user from/to the db failed.
                    # Send a server error response
                    return make_response(
                        jsonify(
                            message="Could not log the user in",
                            status=501
                        )
                    )
                else:
                    # Attempt was successful, assign the user data to the
                    # login_session
                    login_session['user'] = Get_User_Info(user_data)
            else:
                # User information was not verified by Google,
                # clear session variables to make sure this individual
                # does not receive accidental authentication rights.
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
    # Function used to clear all session data to log the user out
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
    session = Get_Glb_Session()

    # Get the 10 newest items to show in the main page
    items = session.query(Item).order_by(Item.id.desc()).limit(10).all()

    return render_template(
        'index.html',
        title='Latest Items',
        items=items
    )


@app.route('/show/<int:main_cat_id>')
def Show_Category(main_cat_id):
    session = Get_Glb_Session()

    # Get the category that will be shown
    main_category = session.query(
        Category
    ).filter_by(
        id=main_cat_id
    ).one_or_none()

    # Get the sub categories associated with the category
    sub_categories = session.query(
        Sub_Category
    ).filter_by(
        cat_id=main_cat_id
    ).all()

    # Get the items associated with the category
    items = session.query(
        Item
    ).filter_by(
        cat_id=main_cat_id
    ).all()

    return render_template(
        'show-category.html',
        title='Item Catalog - %s' % (main_category.name),
        main_category=main_category,
        sub_categories=sub_categories,
        items=items
    )


@app.route('/addCategory', methods=['GET', 'POST'])
def Add_Category():
    session = Get_Glb_Session()

    # Make sure user is logged in
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    # Check for posts to add a category
    if request.method == 'POST':
        form = request.form

        new_cat = Category(
            name=form['category_name'],
            user_id=login_session['user']['user_id']
        )
        session.add(new_cat)
        session.commit()

        return redirect(url_for('Index'))

    # Render the add category form for GET requests
    return render_template(
        'add-category.html',
        title="Item Catalog",
    )


@app.route('/editCategory/<int:main_cat_id>', methods=['GET', 'POST'])
def Edit_Category(main_cat_id):
    session = Get_Glb_Session()

    # Make sure user is logged in
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    category = session.query(
        Category
    ).filter_by(
        id=main_cat_id
    ).one_or_none()

    # Check for post requests to edit the category
    if request.method == 'POST':
        if (
            category and
            login_session['user']['user_id'] == category.user_id
        ):

            form = request.form

            category.name = form['category_name']

            session.add(category)
            session.commit()
        else:
            flash("You don't have the right access to edit %s" %
                  (category.name))

        return redirect(url_for('Index'))

    # Render the edit category form for GET requests
    return render_template(
        'edit-category.html',
        title="Item Catalog",
        category=category
    )


@app.route('/deleteCategory/<int:main_cat_id>', methods=['GET', 'POST'])
def Delete_Category(main_cat_id):
    session = Get_Glb_Session()

    # Make sure user is logged in
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    category = session.query(
        Category
    ).filter_by(
        id=main_cat_id
    ).one_or_none()

    # Check for post requests to delete the category
    if request.method == 'POST':
        if (
            category and
            login_session['user']['user_id'] == category.user_id
        ):

            session.delete(category)
            session.commit()
        else:
            flash("You don't have the right access to delete %s" %
                  (category.name))

        return redirect(url_for('Index'))

    # Render the delete form for GET requests
    return render_template(
        'delete-category.html',
        title="Item Catalog",
        category=category
    )


@app.route('/editSubCategory/<int:main_cat_id>/<int:sub_cat_id>',
           methods=['GET', 'POST'])
def Edit_Sub_Category(main_cat_id, sub_cat_id):
    session = Get_Glb_Session()
    
    # Make sure user is logged in
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    sub_category = session.query(
        Sub_Category
    ).filter_by(
        id=sub_cat_id
    ).one_or_none()

    # Check for post requests to edit the sub category
    if request.method == 'POST':
        if (
            sub_category and
            login_session['user']['user_id'] == sub_category.user_id
        ):

            form = request.form

            sub_category.name = form['category_name']

            session.add(sub_category)
            session.commit()

            # Update all associated items to the sub category
            items = session.query(
                Item
            ).filter_by(
                sub_cat_id=sub_category.id
            ).all()

            for item in items:
                item.sub_category = form['category_name']

                session.add(item)
                session.commit()
        else:
            flash("You don't have the right access to edit %s" %
                  (sub_category.name))

        return redirect(url_for('Show_Category', main_cat_id=main_cat_id))

    # Render the edit sub category form for GET requests
    return render_template(
        'edit-category.html',
        title="Item Catalog",
        category=sub_category,
        main_cat_id=main_cat_id
    )


@app.route('/deleteSubCategory/<int:main_cat_id>/<int:sub_cat_id>',
           methods=['GET', 'POST'])
def Delete_Sub_Category(main_cat_id, sub_cat_id):
    session = Get_Glb_Session()
    
    # Make sure user is logged in
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    sub_category = session.query(
        Sub_Category
    ).filter_by(
        id=sub_cat_id
    ).one_or_none()

    # Check for post requests to delete the sub category
    if request.method == 'POST':
        if (
            sub_category and
            login_session['user']['user_id'] == sub_category.user_id
        ):

            # Delete all items associated with the sub category
            session.query(
                Item
            ).filter_by(
                sub_cat_id=sub_cat_id
            ).delete()

            # Safe to delete the sub category
            session.query(
                Sub_Category
            ).filter_by(
                id=sub_cat_id
            ).delete()

            session.commit()
        else:
            flash("You don't have the right access to delete %s" %
                  (sub_category.name))

        return redirect(
            url_for(
                'Show_Category',
                main_cat_id=main_cat_id
            )
        )

    # Render the delete category form for GET requests
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
    session = Get_Glb_Session()
    
    # Make sure user is logged in
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    # Check for post requests to add an item
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
                picture=form['item_picture'],
                link=form['item_link'],
                description=form['item_description'],
                cat_id=cat_data['cat_id'],
                sub_cat_id=cat_data['sub_cat_id'],
                user_id=login_session['user']['user_id']
            )
        )
        session.commit()

        return redirect(
            url_for(
                'Show_Category',
                main_cat_id=cat_data['cat_id']
            )
        )

    # Get the sub categories that will be populated in the add item form
    sub_categories = session.query(Sub_Category).all()

    # Render the add item form for GET requests
    return render_template(
        'add-item.html',
        main_id=main_id,
        sub_id=sub_id,
        sub_categories=sub_categories
    )


@app.route('/editItem/<int:item_id>', methods=['GET', 'POST'])
def Edit_Item(item_id):
    session = Get_Glb_Session()
    
    # Make sure user is logged in
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    item = session.query(Item).filter_by(id=item_id).one_or_none()

    # Check for post requests to edit the item
    if request.method == 'POST':
        if item and login_session['user']['user_id'] == item.user_id:
            form = request.form

            # Get the category names and IDs based on
            # selected fields in the form.
            cat_data = Get_Category_IDs(form)

            # Update the item's data.
            item.name = form['item_name']
            item.price = form['item_price']
            item.category = cat_data['cat_name']
            item.sub_category = cat_data['sub_cat_name']
            item.picture = form['item_picture']
            item.link = form['item_link']
            item.description = form['item_description']
            item.cat_id = cat_data['cat_id']
            item.sub_cat_id = cat_data['sub_cat_id']

            # Update the item in the db
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
    # Get the sub categories that will be populated in the edit item form
    sub_categories = session.query(Sub_Category).all()

    # Render the edit item form for GET requests
    return render_template(
        'edit-item.html',
        item=item,
        sub_categories=sub_categories
    )


@app.route('/deleteItem/<int:item_id>', methods=['GET', 'POST'])
def Delete_Item(item_id):
    session = Get_Glb_Session()
    
    # Make sure user is logged in
    if not Is_Authenticated():
        flash('You have to log in to be able to do that!')

        return redirect(
            url_for('Index')
        )

    item = session.query(Item).filter_by(id=item_id).one_or_none()

    # Check for post requests to delete the item
    if request.method == 'POST':
        if item and login_session['user']['user_id'] == item.user_id:
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

    # Render the delete item form for GET requests
    return render_template(
        'delete-item.html',
        item=item
    )


# API Functions


@app.route('/api/all/categories')
def API_All_Categories():
    session = Get_Glb_Session()
    
    categories = session.query(Category).all()

    return jsonify(
        Category=[
            category.serialize for category in categories
        ]
    )


@app.route('/api/all/subCategories')
def API_All_Sub_Categories():
    session = Get_Glb_Session()
    
    categories = session.query(Sub_Category).all()

    return jsonify(
        Category=[
            category.serialize for category in categories
        ]
    )


@app.route('/api/all/items')
def API_All_Items():
    session = Get_Glb_Session()
    
    items = session.query(Item).all()

    return jsonify(
        Item=[
            item.serialize for item in items
        ]
    )


@app.route('/api/category/<int:main_cat_id>')
def API_Category_Items(main_cat_id):
    session = Get_Glb_Session()
    
    items = session.query(Item).filter_by(cat_id=main_cat_id).all()

    return jsonify(
        Item=[
            item.serialize for item in items
        ]
    )


@app.route('/api/subCategory/<int:sub_cat_id>')
def API_Sub_Category_Items(sub_cat_id):
    session = Get_Glb_Session()
    
    items = session.query(Item).filter_by(sub_cat_id=sub_cat_id).all()

    return jsonify(
        Item=[
            item.serialize for item in items
        ]
    )


@app.route('/api/item/<int:item_id>')
def API_Item(item_id):
    session = Get_Glb_Session()
    
    item = session.query(Item).filter_by(id=item_id).one_or_none()

    return jsonify(Item=item.serialize)


@app.route('/api/all/users')
def API_All_Users():
    session = Get_Glb_Session()
    
    # Make sure user is logged in
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

# Add the secret key for the app
try:
    app.secret_key = open('%ssecret_key.txt' % (
        sys.path[0] if platform.system() != 'Windows' \
            else '%s\\' % (sys.path[0])
    ), 'r').read()
except IOError as ioe:
    print('Error: Please create a \'secret_key.txt\' '
            'file within the app\'s directory')
    print(ioe.pgerror)
    print(ioe.diag.message_detail)
    sys.exit(1)

# Adding db functionality for CRUD operations
try:
    engine = create_engine('sqlite:///item_catalog.db?check_same_thread=False')
    DBsession = sessionmaker(bind=engine)
    session = DBsession()
except Exception as e:
    print('Error: Could not get a db session')
    print(str(e))
    sys.exit(1)

if __name__ == "__main__":
    app.debug = True
    app.run(
        ssl_context=('cert.pem', 'key.pem'),
        host="127.0.0.1",
        port=5000
    )
