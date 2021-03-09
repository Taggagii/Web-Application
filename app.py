from flask import *
from flask_sqlalchemy import *
import os
from packages.polls.polls import Polls

db_name = "site.db"

app = Flask(__name__)
polls_class = Polls(db_name)

page_link_dict = {"Home": "home",
        "About" : "about",
        "Pseudocode": "pseudocode",
        "Weather": "weather",
        "Polls": "polls",
                  }


@app.route("/")
def default():
    return redirect("/home/")

@app.route("/home/")
def index():
    return render_template("home.html", pages = page_link_dict, currentPage ="Home")

@app.route("/weather/", methods = ['GET'])
def weather():
    return render_template("weather.html", pages = page_link_dict, currentPage ="Weather")

@app.route('/about/')
def about():
    return render_template('about.html', pages = page_link_dict, currentPage ="About")

@app.route("/pseudocode/")
def pseudocode():
    return render_template('pseudocode.html', pages = page_link_dict, currentPage ='Pseudocode')

@app.route("/polls/")
def polls():
    return render_template('polls.html', pages = page_link_dict, currentPage ='Polls')


@app.route("/polls/createpoll/", methods = ['GET', 'POST'])
def create_poll():
    if request.method == "POST":
        poll_question = request.form['pollQuestion']
        poll_choices = request.form.getlist('pollChoices')[:-1]
        print(poll_question)
        print(poll_choices)
        polls_class.add_poll(poll_question, poll_choices)
        print(polls_class.polls)
        return redirect("/polls/")
    else:
        return render_template("createpoll.html")

@app.route("/polls/<int:id>/")
def show_poll(id):
    print(polls_class.get_poll(id))
    return render_template("show_poll.html", pages = page_link_dict, currentPage = 'Polls', polls_dict = polls_class.get_poll(id))



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
