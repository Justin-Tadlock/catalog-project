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

import psycopg2
import json
import random, string
import httplib2, requests, bleach

from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)

# Add the secret key for the app
try:
    app.secret_key = open('secret_key.txt', 'r').read()
except:
    print('ERROR: Please create a \'secret_key.txt\' file within the app\'s directory')


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

@app.route("/")
def Index():
    return render_template('index.html', title="Catalog")


@app.route('/layout/index')
def Index_Layout():
    return render_template('index_layout.html')


@app.route('/layout/addItem')
def AddItem_Layout():
    return render_template(
        'addItem_layout.html', 
        main_categories=main_categories, 
        sub_categories=sub_categories
    )

@app.route('/layout/deleteItem')
def DeleteItem_Layout():
    item = {
        "name": "Test Item",
        "price": "$5.99",
        "category": "Outdoors",
        "sub_category": "Tents",
        "description": "It's a really small tent for only covering puppies"
    }

    return render_template(
        'deleteItem_layout.html', 
        item=item
    )

@app.route('/layout/editItem')
def EditItem_Layout():
    item = {
        "name": "Test Item",
        "price": "$5.99",
        "category": "Outdoors",
        "sub_category": "Tents",
        "description": "It's a really small tent for only covering puppies"
    }

    return render_template(
        'editItem_layout.html', 
        item=item,
        main_categories=main_categories,
        sub_categories=sub_categories
    )


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
