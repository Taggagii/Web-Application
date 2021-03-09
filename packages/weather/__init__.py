from bs4 import BeautifulSoup
from datetime import datetime
import requests
from models import get_all_weather, add_weather, reset_weather


def get_temperature(location):
    url = "https://www.google.com/search?q=temperature+in+" + location.strip()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    temp = [i.strip() for i in soup.find(class_="BNeawe iBp4i AP7Wnd").text.split('°')]
    if temp:
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
    def __init__(self, location):
        self.weather_dict = get_temperature(location)







