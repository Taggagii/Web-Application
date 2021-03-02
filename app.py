from flask import *
from flask_sqlalchemy import *
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#setting up database
db = SQLAlchemy(app)
db.drop_all()


class WeatherLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    #lat = db.Column(db.Decimal, default=None)
    #lon = db.Column(db.Decimal, default=None)
    last_call = db.Column(db.DateTime, default=datetime.utcnow())
    temperature = db.Column(db.Integer, nullable=False)
    #precipitation = db.Column(db.Integer, nullable=False)
    #humidity = db.Column(db.Integer, nullable=False)
    #wind = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String, nullable=False)
    #warnings = db.Column(db.String, default=None)

content = ""

def getTemperature(location):
    url = "https://www.google.com/search?q=temperature+in+" + location.strip()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    temp = [i.strip() for i in soup.find(class_="BNeawe iBp4i AP7Wnd").split('°')]
    corrected_location = soup.find(class_="BNeawe tAd8D AP7Wnd")

    location_text = [i.strip() for i in corrected_location.text.split(',')]
    new_weather_entry = WeatherLocation(city=location_text[0],
                                        country=location_text[1],
                                        temperature=temp[0],
                                        unit=temp[1])

    if temp:
        return "The temp in " + corrected_location.text + " is " + temp.text
    return 'Sorry! We couldn\'t resolve the location: "' + location + '"'


@app.route("/")
def index():
    return render_template("index.html", testing = content)

@app.route("/testing/", methods = ['POST'])
def testing():
    global content
    location = request.form['valuesInput']
    content = getTemperature(location) #get the value
    return redirect('/')

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
    app.run(debug = True)
