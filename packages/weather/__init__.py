from bs4 import BeautifulSoup
from datetime import datetime

class WeatherRequest:
    def __init__(self,  database, location=None):
        self.db = database
        self.location_raw = location
