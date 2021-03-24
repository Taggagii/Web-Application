from flask import *
import os, random, glob
from packages.weather import Weather
from packages.polls.polls import Polls
from packages.login import Login
from packages.markbook import Markbook
from datetime import timedelta
app = Flask(__name__)
app.secret_key = "1234"
app.permanent_session_lifetime = timedelta(minutes=10)

db_file = 'site.db'

weather_obj = Weather(db_file)
polls_class = Polls(db_file)
login_obj = Login(db_file)
markbook_obj = Markbook(db_file)

page_link_dict = {
        "Home": "/home/",
        "About": "/about/",
        "Weather": "/weather/",
        "Polls": "/polls/",
        "Markbook": "/markbook/"
                  }

my_path = os.getcwd().replace('\\', '/') + "/static/audio"
songs = [i.replace(my_path + "\\", "") for i in glob.glob(my_path + "/*.mp3")]

# All endpoint returns should follow the format return render_template("<current page>.html", pages=page_link_dict,
# current_page="<current page>" <page data>=dictionary_of_parameters) or a redirect
@app.route("/")
@app.route("/home/")
def index():
    return render_template("home.html", pages=page_link_dict, current_page="Home",  song = random.choices(songs)[0], session=session)


@app.route('/about/')
def about():
    return render_template('about.html', pages=page_link_dict, current_page="About",  song = random.choices(songs)[0], session=session)


@app.route("/pseudocode/")
def pseudocode():
    return render_template('pseudocode.html', pages=page_link_dict, current_page="Pseudocode",  song = random.choices(songs)[0], session=session)


@app.route("/weather/", methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        error = None
        if 'user' in session:
            error = weather_obj.add_weather(request.form['location'], username=session['user'])
        else:
            error = weather_obj.add_weather(request.form['location'])

        if error:
            error_dict = {'source': '/weather/', 'error': error, 'redirect_msg': 'Go back'}
            return render_template("error.html",
                               pages=page_link_dict,
                               current_page="Error",
                               e=error_dict,  song = random.choices(songs)[0], session=session)
        else:
            return redirect('/weather/')
    # Weather data display
    else:
        if 'user' in session:
            weather_data = weather_obj.get_all_weather(session['user'])
        else:
            weather_data = weather_obj.get_all_weather()
        return render_template("weather.html",
                               pages=page_link_dict,
                               current_page="Weather",
                               weather_readings=weather_data,
                                song = random.choices(songs)[0], session=session)


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
            return redirect('/profile/')
        else:
            login_data['error'] = "Incorrect password. Make sure the account exists"

    return render_template("login.html", pages=page_link_dict, current_page='Login', login_data=login_data,  song = random.choices(songs)[0], session=session)


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    signup_data = {}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password != "":
            if login_obj.sign_up(username, password):
                session['user'] = username
                return redirect(url_for('profile'))
            else:
                signup_data['error'] = "That username has already been taken. Please choose another."
        else:
            signup_data['error'] = "You must enter a password."
            return render_template('signup.html', pages=page_link_dict, current_page='Signup', signup_data=signup_data,
                                    song = random.choices(songs)[0], session=session)
    else:
        return render_template('signup.html', pages=page_link_dict, current_page='Signup', signup_data=signup_data,  song = random.choices(songs)[0], session=session)


@app.route('/logout/')
def logout():
    if 'user' in session:
        del session['user']
        return redirect(url_for('login'))
    else:
        return redirect(url_for('home'))


@app.route('/change/', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST' and 'user' in session:
        user_data = {'username': session['user']}
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['reenter']
        new_password = request.form['new_password']
        if new_password != "":
            if password == password2:
                if login_obj.log_in(username, password):
                    login_obj.change_password(username, new_password)
                    user_data['error'] = "Password successfully changed!"
                else:
                    user_data['error'] = "Incorrect password Try again"
            else:
                user_data['error'] = "Make sure your current passwords match"
        else:
            user_data['error'] = "You must enter a new password"
        return render_template('profile.html',
                        pages=page_link_dict,
                        current_page="Profile",
                        user_data=user_data,
                        song=random.choices(songs)[0], session=session)
    else:
        return redirect(url_for('profile'))



@app.route('/profile/')
def profile():
    if session['user']:
        user_data = {'username': session['user']}
        return render_template('profile.html',
                               pages=page_link_dict,
                               current_page="Profile",
                               user_data=user_data,
                                song = random.choices(songs)[0], session=session)
    else:
        return redirect(url_for('login'))


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
    return render_template('polls.html', pages=page_link_dict, current_page='Polls',  song = random.choices(songs)[0], session=session)


@app.route("/polls/vote/<int:id>/", methods = ['GET', 'POST'])
def vote_poll(id):
    if request.method == "POST":
        if "choices" in request.form:
            choice = request.form["choices"]
            polls_class.vote(id, choice)
        return redirect("/polls/" + str(id) + "/")
    else:
        if id in polls_class.polls.keys():
            return render_template("vote_poll.html", pages = page_link_dict, current_page='Polls', polls_dict=polls_class.get_poll(id),  song = random.choices(songs)[0], session=session)
        else:
            return redirect("/polls/")

        
@app.route("/polls/<int:id>/")
def show_poll(id):
    return render_template("show_poll.html", pages=page_link_dict, current_page="Polls", polls_dict=polls_class.get_poll(id),  song = random.choices(songs)[0], session=session)


def markbook():
    if 'user' in session:

        if request.method == 'POST':
            class_name = request.form['class_name']
            return redirect(url_for('new_class', name=class_name))

        elif request.method == 'GET':
            markbooks_dict = markbook_obj.get_user_classes(session['user'])
            return render_template('markbook_home.html',
                                   pages=page_link_dict,
                                   current_page="Markbook",
                                   session=session,
                                   markbooks_dict=markbooks_dict)

    else:
        return not_logged_in("Log in to access your markbooks. Don't have an account? Sign up!")


@app.route('/markbook/new/<string:name>/', methods=['GET', 'POST'])
def new_class(name):
    if 'user' in session:
        if request.method == 'POST':
            grade = request.form['grade']
            if isinstance(grade, int):
                if not(12 < grade or grade < 9):
                    return markbook_error_switch(4)
            else:
                return markbook_error_switch(4)
            code = request.form['code']
            start = request.form['start']
            end = request.form['end']
            markbook_obj.add_class(name, session['user'])

        else:
            class_edit_dict = {'name': name}
            return render_template('markbook_edit_class.html',
                            pages=page_link_dict,
                            current_page="Markbook",
                            class_edit_dict=class_edit_dict,
                            session=session)
    else:
        return not_logged_in("Log in to access your markbooks. Don't have an account? Sign up!")


def markbook_error_switch(code):
    error = ""
    if code == 1:
        error = "Not a valid course code"
    elif code == 2:
        error = "Not a valid start date"
    elif code == 3:
        error = "Not a valid end date"
    elif code == 4:
        error = "Not a valid grade"
    markbooks_dict = {'error': error}
    return render_template('markbook_home.html',
                           pages=page_link_dict,
                           current_page='Markbook',
                           session=session,
                           markbooks_dict=markbooks_dict)




@app.route('/markbook/new/', methods=['GET', 'POST'])
def new_class():
    if request.method == 'POST':
        pass
        redirect(url_for('markbook'))
    else:
        redirect(url_for('markbook'))


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
    app.run(host='192.168.1.222', debug=False, port=25565, threaded=True)
    #app.run(debug=True)

