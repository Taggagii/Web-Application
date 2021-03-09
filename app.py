from flask import *
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from packages.weather import Weather
from models import get_all_weather, add_weather, reset_weather
from packages.polls.polls import Polls
app = Flask(__name__)

db_file = 'site.db'

weather_obj = Weather(db_file)
polls_class = Polls(db_file)

page_link_dict = {
        "Home": "/home/",
        "About" : "/about/",
        "Pseudocode": "/pseudocode/",
        "Weather": "/weather/",
        "Polls": "/polls/"
                  }


@app.route("/")  # Just a redirect for the default end point. All homepage changes should be made to /home/
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


@app.route("/weather/", methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        if error := weather_obj.add_weather(request.form['location']):
            error_dict = {'source': '/weather/', 'error': error}
            return render_template("error.html",
                               pages=page_link_dict,
                               currentPage="Error",
                               e=error_dict)
        else:
            return redirect('/weather/')
    else:
        weather_data = weather_obj.get_all_weather()
        print('testing', weather_data)
        return render_template("weather.html",
                               pages=page_link_dict,
                               currentPage="Weather",
                               weather_readings=weather_data)



@app.route("/weather/delete/<int:reading_id>", methods=['GET', 'POST'])
def delete_weather(reading_id):
    weather_obj.delete_weather(reading_id)
    return redirect('/weather/')


@app.route("/polls/createpoll/", methods = ['GET', 'POST'])
def create_poll():
    if request.method == "POST":
        poll_question = request.form['pollQuestion']
        poll_choices = request.form.getlist('pollChoices')[:-1]
        print(poll_question)
        print(poll_choices)
        polls_class.add_poll(poll_question, poll_choices)
        id = max(polls_class.polls.keys())
        return redirect("/polls/" + str(id) + "/")
    else:
        return render_template("createpoll.html")


@app.route("/polls/")
def polls():
    return render_template('polls.html', pages=page_link_dict, currentPage='Polls')

@app.route("/polls/<int:id>/")
def show_poll(id):
    print(polls_class.get_poll(id))
    return render_template("show_poll.html", pages = page_link_dict, currentPage = 'Polls', polls_dict = polls_class.get_poll(id))


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

