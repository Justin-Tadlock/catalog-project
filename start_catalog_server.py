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


@app.route("/")
def Index():
    return render_template('index.html', title="Catalog")

@app.route('/layout/index')
def Layout():
    return render_template('index_layout.html')


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
