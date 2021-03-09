import sqlite3 as sql
from os import path
from datetime import datetime

ROOT = path.dirname(path.relpath(__file__))
db_file = 'site.db'

def connect():
    return sql.connect(path.join(ROOT, db_file))

def add_weather(data):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO weather (city, country, temperature, unit) VALUES (?, ?, ?, ?)',
                   (data['city'], data['country'], data['temperature'], data['unit']))
    connection.commit()
    connection.close()
    return


def get_all_weather():
    connection = connect()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM weather')
    weather_data_rows = cursor.fetchall()
    connection.close()
    return weather_data_rows

def get_at_city():
    connection = connect()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM weather')
    weather_data_rows = cursor.fetchall()
    connection.close()
    return weather_data_rows


def reset_weather():
    connection = connect()
    cursor = connection.cursor()
    with open('weather.sql', 'r') as schema:
        script = schema.read()
        cursor.executescript(script)
    connection.commit()
    connection.close()


