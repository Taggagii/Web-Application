from flask import *
import os
from packages.weather import Weather
from packages.polls.polls import Polls
from packages.login import Login
from datetime import timedelta
app = Flask(__name__)
app.secret_key = "1234"
app.permanent_session_lifetime = timedelta(minutes=10)

db_file = 'site.db'

weather_obj = Weather(db_file)
polls_class = Polls(db_file)
login_obj = Login(db_file)

page_link_dict = {
        "Home": "/home/",
        "About": "/about/",
        "Pseudocode": "/pseudocode/",
        "Weather": "/weather/",
        "Polls": "/polls/",
        "Login": "/login/"
                  }


# All endpoint returns should follow the format return("<current page>.html", pages=page_link_dict,
# current_page="<current page>" dictionary_of_parameters)
@app.route("/")
@app.route("/home/")
def index():
    return render_template("home.html", pages=page_link_dict, current_page="Home")


@app.route('/about/')
def about():
    return render_template('about.html', pages=page_link_dict, current_page="About")


@app.route("/pseudocode/")
def pseudocode():
    return render_template('pseudocode.html', pages=page_link_dict, current_page="Pseudocode")


@app.route("/weather/", methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        if error := weather_obj.add_weather(request.form['location']):
            error_dict = {'source': '/weather/', 'error': error}
            return render_template("error.html",
                               pages=page_link_dict,
                               current_page="Error",
                               e=error_dict)
        else:
            return redirect('/weather/')
    else:
        weather_data = weather_obj.get_all_weather()
        return render_template("weather.html",
                               pages=page_link_dict,
                               current_page="Weather",
                               weather_readings=weather_data)


@app.route("/weather/delete/<int:reading_id>", methods=['GET', 'POST'])
def delete_weather(reading_id):
    weather_obj.delete_weather(reading_id)
    return redirect('/weather/')


@app.route("/login/", methods=['GET', 'POST'])
def login():
    login_data = {}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if login_obj.log_in(username, password):
            session.permanent = True
            session['user'] = username
            del page_link_dict['Login']
            page_link_dict[username] = '/profile/'
            return redirect('/profile/')
        else:
            login_data['error'] = "Incorrect password. Make sure the account exists"

    return render_template("login.html", pages=page_link_dict, current_page='Login', login_data=login_data)


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_obj.sign_up(username, password):
            session['user'] = username
            del page_link_dict['Login']
            page_link_dict[username] = '/profile/'
            return redirect(url_for('profile'))
    else:
        return render_template('signup.html', pages=page_link_dict, current_page='Signup')


@app.route('/logout/')
def logout():
    if 'user' in session:
        del page_link_dict[session['user']]
        page_link_dict['Login'] = '/login/'
        del session['user']
        return redirect(url_for('login'))
    else:
        return redirect(url_for('home'))


@app.route('/profile/')
def profile():
    if session['user']:
        user_data = {'username': session['user']}
        return render_template('profile.html',
                               pages=page_link_dict,
                               current_page=user_data['username'],
                               user_data=user_data)
    else:
        return render_template("login.html", pages=page_link_dict, current_page='Login')


@app.route("/polls/createpoll/", methods=['GET', 'POST'])
def create_poll():
    if request.method == "POST":
        poll_question = request.form['pollQuestion']
        poll_choices = request.form.getlist('pollChoices')[:-1]
        polls_class.add_poll(poll_question, poll_choices)
        id = max(polls_class.polls.keys())
        return redirect("/polls/vote/" + str(id) + "/")
    else:
        return render_template("createpoll.html")


@app.route("/polls/")
def polls():
    return render_template('polls.html', pages=page_link_dict, current_page='Polls')


@app.route("/polls/vote/<int:id>/", methods = ['GET', 'POST'])
def vote_poll(id):
    if request.method == "POST":
        if "choices" in request.form:
            choice = request.form["choices"]
            polls_class.vote(id, choice)
        return redirect("/polls/" + str(id) + "/")
    else:
        if id in polls_class.polls.keys():
            return render_template("vote_poll.html", pages = page_link_dict, current_page='Polls', polls_dict=polls_class.get_poll(id))
        else:
            return redirect("/polls/")

        
@app.route("/polls/<int:id>/")
def show_poll(id):
    return render_template("show_poll.html", pages=page_link_dict, current_page="Polls", polls_dict=polls_class.get_poll(id))


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
    #app.run(host='192.168.1.222', debug=False, port=25565, threaded=True)
    app.run(debug=True)

