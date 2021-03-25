from bs4 import BeautifulSoup
import requests
import sqlite3 as sql

'''This is a hacked-together "API" which uses web scraping to programitically access a webspage. Specifically, it
appends a target location to a google query, which will cause google to display the resultant weather data on the page.
The HTML element containing the data we want has a known identifier, which we use to find it and pull its data. if we
fail to find the element, it spits back an error.'''
def get_temperature(location):
    url = "https://www.google.com/search?q=temperature+in+" + location.strip()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    temp = soup.find(class_="BNeawe iBp4i AP7Wnd")
    if temp:
        temp = [i.strip() for i in temp.text.split('°')]
        corrected_location = soup.find(class_="BNeawe tAd8D AP7Wnd")
        location_text = [i.strip() for i in corrected_location.text.split(',')]

        weather_dict = {'city': location_text[0],
                        'country': location_text[1],
                        'temperature': temp[0],
                        'unit': temp[1],
                        'error': None}
    else:
        weather_dict = {'error': f'Could not resolve location {location}'}

    return weather_dict

# Weather is a class whose methods are accessed in the main function by way of an instance, weather_obj
class Weather:
    # Connects to the instance's database
    def connect(self):
        return sql.connect(self.db)

    # Runs a local SQL script file on the database to generate the weather table inside
    def initialize_weather_table(self):
        con = self.connect()
        # Any time we send commands to the database, it's done through our connection's cursor. The cursor also stores
        # return data, if we send a request to get information
        # The cursor executes SQL, a lighweight programming language used specifically to commincate with databases
        cursor = con.cursor()
        with open('weather.sql', 'r') as schema:
            script = schema.read()
            cursor.executescript(script)
        con.commit()
        con.close()

    #The constructor takes the path to the database file and resets the weather table (not normally needed once deployed)
    def __init__(self, db_path):
        self.db = db_path
        self.initialize_weather_table()

    #Gets all weather data from the table for a specific user
    def get_all_weather(self, username=None):
        con = self.connect()
        cursor = con.cursor()
        if username:
            cursor.execute('SELECT * FROM weather WHERE username = ?', (username,))
        else:
            cursor.execute('SELECT * FROM weather WHERE username IS NULL')
        weather_data_rows = cursor.fetchall()
        con.close()
        return weather_data_rows

    #Gets weather from a requested location, and adds it to the database if successful
    def add_weather(self, location_raw, username=None):
        data = get_temperature(location_raw)
        if data['error']:
            return data['error']
        else:
            con = self.connect()
            cursor = con.cursor()
            if username:
                cursor.execute('INSERT INTO weather (city, country, temperature, unit, username) VALUES (?, ?, ?, ?, ?)',
                               (data['city'], data['country'], data['temperature'], data['unit'], username))
            else:
                cursor.execute('INSERT INTO weather (city, country, temperature, unit) VALUES (?, ?, ?, ?)',
                               (data['city'], data['country'], data['temperature'], data['unit']))
            con.commit()
            con.close()

    #Deletes a weather entry by its unique id
    def delete_weather(self, weather_id):
        con = self.connect()
        cursor = con.cursor()
        cursor.execute(f'DELETE FROM weather WHERE id={weather_id}')
        con.commit()
        con.close()











