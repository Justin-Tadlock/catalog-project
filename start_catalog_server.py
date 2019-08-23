from flask import (
    Flask,
    request,
    redirect,
    url_for,
    make_response,
    render_template
)

app = Flask(__name__)
app.secret_key = "Replace me"

# Temp Data
main_categories = ['Outdoors', 'Video Games', 'Technology', 'Kitchen']
sub_categories = {
    "Outdoors": [
        'Boots',
        'Tents',
        'Backpacks',
        'Gloves',
        'Coolers'
    ],
    "Video Games": [
        'Consoles',
        'Games',
        'Accessories'
    ],
    "Technology": [
        'Desktops',
        'Laptops',
        'Monitors',
        'Keyboards',
        'Mice'
    ],
    "Kitchen": [
        'Pots and Pans',
        'Cups',
        'Silverware',
        'Coffee Makers'
    ]
}

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
