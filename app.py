from flask import *
from flask_sqlalchemy import *
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
#setting up database

content = ""

def getTemperature(location):
    url = "https://www.google.com/search?q=temperature+in+" + location.strip()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    temp = soup.find(class_="BNeawe iBp4i AP7Wnd")
    correctedLocation = soup.find(class_="BNeawe tAd8D AP7Wnd")

    if temp:
        return "The temp in " + correctedLocation.text + " is " + temp.text
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
