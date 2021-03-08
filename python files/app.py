from flask import *
from flask_sqlalchemy import *
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

names = {"Home": "home",
        "About" : "about",
        "Pseudocode": "pseudocode",
        "Weather": "weather",
        }

@app.route("/")
def default():
    return redirect("/home/")

@app.route("/home/")
def index():
    return render_template("home.html", names = names, currentPage = "Home")

@app.route("/weather/", methods = ['GET'])
def weather():
    return render_template("weather.html", names = names, currentPage = "Weather")

@app.route('/about/')
def about():
    return render_template('about.html', names = names, currentPage = "About")

@app.route("/pseudocode/")
def pseudocode():
    return render_template('pseudocode.html', names = names, currentPage = 'Pseudocode')


@app.context_processor
def override_url_for():
    return dict(url_for = dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get('filename', None)
        if filename:
            path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == "__main__":
    app.run(debug=True)
