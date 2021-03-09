from flask import *
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from packages.weather import Weather
from models import get_all_weather, add_weather, reset_weather

app = Flask(__name__)

page_link_dict = {
        "Home": "/home/",
        "About" : "/about/",
        "Pseudocode": "/pseudocode/",
        "Weather": "/weather/",
        "Polls": "/polls/"
                  }


@app.route("/") #Just a redirect for the default enpoint. All homepage changes should be made to /home/
def default():
    return redirect("/home/")


# All endpoint returns should follow the format return("<current page>.html", pages=page_link_dict,
# currentPage="<current page>" dictionary_of_parameters)

@app.route("/home/")
def index():
    return render_template("home.html", pages=page_link_dict, currentPage="Home")


@app.route('/about/')
def about():
    return render_template('about.html', pages=page_link_dict, currentPage="About")


@app.route("/pseudocode/")
def pseudocode():
    return render_template('pseudocode.html', pages=page_link_dict, currentPage="Pseudocode")


@app.route("/weather/", methods = ['GET', 'POST'])
def weather():
    weather_data = None

    if request.method == 'POST':
        weather_data = Weather(request.form.get('location')).weather_dict
    else:
        pass
    return render_template("weather.html", pages=page_link_dict, currentPage="Weather", weather=weather_data)


@app.route("/polls/")
def polls():
    return render_template('polls.html', pages=page_link_dict, currentPage='Polls')


#Borrowed from https://gist.github.com/itsnauman/b3d386e4cecf97d59c94
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


