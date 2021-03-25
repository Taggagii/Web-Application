from flask import *
import os, random, glob
from packages.weather import Weather
from packages.polls import Polls
from packages.login import Login
from packages.markbook import Markbook
from datetime import timedelta
# Pull all necessary packages from the pipenv. Packages in the "packages" directory were written by us and exist locally
app = Flask(__name__)
app.secret_key = "1234"
app.permanent_session_lifetime = timedelta(minutes=10)

db_file = 'site.db'

weather_obj = Weather(db_file)
polls_obj = Polls(db_file)
login_obj = Login(db_file)
markbook_obj = Markbook(db_file)

'''
Everything the code does operates through an instance of the Flask class. We followed this format for our own packages,
which perfrom all their operations on their respective objects and are linked to the database file, rather than having all
functions live in the same app file. app.py just talks to fucntions in other objects and links the results
together with the HTML and CSS.
'''

# This stores the page names and links for our navigation bar.
page_link_dict = {
        "Home": "/home/",
        "About": "/about/",
        "Weather": "/weather/",
        "Polls": "/polls/",
        "Markbook": "/markbook/"
                  }

my_path = os.getcwd().replace('\\', '/') + "/static/audio"
songs = [i.replace(my_path + "\\", "") for i in glob.glob(my_path + "/*.mp3")]

'''
Flask uses decorators, a special Python tool for linking functions together, in order to redirect requests to our custom
server code. "Endpoints" (app.route) are the paths that tell the server what the client wants and thus, what function to
run. A client will specify where on the site they want to go, and if that endpoint is assigned to a function, that
function will tell Flask what information to render back to the client. 
'''
@app.route("/")
@app.route("/home/")
def index():
# Flask's render_template function takes in 1+ arguments, the first being an HTML file in a directory named 'templates'
# that tells it what page to render, and the rest being variables that Jinja can access when redering the final page
    return render_template("home.html", pages=page_link_dict, current_page="Home",  song = random.choices(songs)[0], session=session)


@app.route('/about/')
def about():
    return render_template('about.html', pages=page_link_dict, current_page="About",  song = random.choices(songs)[0], session=session)


@app.route("/pseudocode/")
def pseudocode():
    return render_template('pseudocode.html', pages=page_link_dict, current_page="Pseudocode",  song = random.choices(songs)[0], session=session)


@app.route("/weather/", methods=['GET', 'POST'])
def weather():
# Much like with databases and SQL, HHTP methods distinguish different types of requests to a page. The standard request
# is a GET request, which is used to just display a page and its information. When we want to send data back to the
# server, we use a post request
    if request.method == 'POST':
        error = None

        '''session is a special dictionary object that is generated behind the scenes by Flask. What makes session
        special is that it is unique for every individual connection to the site (Flask handles the generation and 
        storage of a cookie on each browser that allows it to distinguish this). The value for key user is the user 
        account currently signed in, null if no user is signed in.'''

        if 'user' in session:

            '''All information from the page that sends the request exists in the request object, including any user-
            inputted data. Here we access the element by its name 'location', that tells us where the user wants their 
            weather reading for. That is passed to the weather object's add function'''

            error = weather_obj.add_weather(request.form['location'], username=session['user'])
        else:
            error = weather_obj.add_weather(request.form['location'])

        # if sees "None" as False, and the function will return that by default. If there is an error, the function
        # throws that back as text instead, and the function spits it back to the user
        if error:
            error_dict = {'source': '/weather/', 'error': error, 'redirect_msg': 'Go back'}
            return render_template("error.html",
                               pages=page_link_dict,
                               current_page="Error",
                               e=error_dict,  song = random.choices(songs)[0], session=session)
        else:
            # redirect forwards a (GET) request through to another endpoint, rather than rendering its own page
            return redirect('/weather/')

    else:

        '''When the function recieves a GET request, it asks the database to return all weather entires corresponding to 
        the current user (or to no user, if nobody is logged in). These are passed to the HTML page as it is rendered,
        and Jinja loops through each entry and displays it.'''

        if 'user' in session:
            weather_data = weather_obj.get_all_weather(session['user'])
        else:
            weather_data = weather_obj.get_all_weather()
        return render_template("weather.html",
                               pages=page_link_dict,
                               current_page="Weather",
                               weather_readings=weather_data,
                                song = random.choices(songs)[0], session=session)

'''When each weather entry is generated, it creates a static link to this deletion endpoint. Using the <> syntax, it is 
possible to pass an endpoint function data in the endpoint itself, rather than just data from the page sending the
request. Each entry's deletion link therefore deletes itself in the database.'''

@app.route("/weather/delete/<int:reading_id>", methods=['GET', 'POST'])
def delete_weather(reading_id):
    weather_obj.delete_weather(reading_id)
    return redirect('/weather/')

# Gets user input from the sending form and attempts to log the user in
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


# Takes data from the sending form and attempts to add a new user account. If successful, also logs the user in
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


# Deletes the current user from the session object, logging them out of the site
@app.route('/logout/')
def logout():
    if 'user' in session:
        del session['user']
        return redirect(url_for('login'))
    else:
        return redirect(url_for('home'))


# Verifies the current username and password, then updates the password in the database with the new one
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
        polls_obj.add_poll(poll_question, poll_choices)
        id = max(polls_obj.polls.keys())
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
            polls_obj.vote(id, choice)
        return redirect("/polls/" + str(id) + "/")
    else:
        if id in polls_obj.polls.keys():
            return render_template("vote_poll.html", pages = page_link_dict, current_page='Polls', polls_dict=polls_obj.get_poll(id), song = random.choices(songs)[0], session=session)
        else:
            return redirect("/polls/")

        
@app.route("/polls/<int:id>/")
def show_poll(id):
    return render_template("show_poll.html", pages=page_link_dict, current_page="Polls", polls_dict=polls_obj.get_poll(id), song = random.choices(songs)[0], session=session)


@app.route('/markbook/', methods=['GET', 'POST'])
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


@app.route('/markbook/new/<string:class_name>/', methods=['GET', 'POST'])
def new_class(class_name):
    if 'user' in session:
        if request.method == 'POST':
            class_name = request.form['class_name']
            code = request.form['code']
            grade = request.form['grade']
            start = request.form['start']
            end = request.form['end']

            error = markbook_obj.add_class(class_name, session['user'], code, grade, start, end)
            if error:
                class_edit_dict = {'error': error}
            else:
                return redirect(url_for('markbook'))

        else:
            class_edit_dict = {'name': class_name}

        return render_template('markbook_edit_class.html',
                        pages=page_link_dict,
                        current_page="Markbook",
                        class_edit_dict=class_edit_dict,
                        session=session)
    else:
        return not_logged_in("Log in to create a markbook. Don't have an account? Sign up!")


    '''markbooks_dict = {'error': error}
    return render_template('markbook_home.html',
                           pages=page_link_dict,
                           current_page='Markbook',
                           session=session,
                           markbooks_dict=markbooks_dict)'''


def not_logged_in(error):
    error_dict = {'source': '/login/',
                  'error': error,
                  'redirect_msg': "Login or Sign Up"}
    return render_template('error.html', pages=page_link_dict, current_page='Error', e=error_dict)


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

