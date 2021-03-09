from bs4 import BeautifulSoup
import requests
import sqlite3 as sql
from os import path
from datetime import datetime


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


class Weather:
    def connect(self):
        return sql.connect(self.db)

    def initialize_weather_table(self):
        con = self.connect()
        cursor = con.cursor()
        with open('weather.sql', 'r') as schema:
            script = schema.read()
            cursor.executescript(script)
        con.commit()
        con.close()

    def __init__(self, db_path):
        self.db = db_path
        self.initialize_weather_table()

    def get_all_weather(self):
        con = self.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM weather')
        weather_data_rows = cursor.fetchall()
        con.close()
        return weather_data_rows

    def add_weather(self, location_raw):
        data = get_temperature(location_raw)
        if data['error']:
            return data['error']
        else:
            con = self.connect()
            cursor = con.cursor()
            cursor.execute('INSERT INTO weather (city, country, temperature, unit) VALUES (?, ?, ?, ?)',
                           (data['city'], data['country'], data['temperature'], data['unit']))
            con.commit()
            con.close()

    def delete_weather(self, weather_id):
        con = self.connect()
        cursor = con.cursor()
        cursor.execute(f'DELETE FROM weather WHERE id={weather_id}')
        con.commit()
        con.close()











