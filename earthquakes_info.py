from requests import get
from datetime import date
from argparse import ArgumentParser
from os import environ
from dotenv import load_dotenv, find_dotenv
from pprint import pprint


def get_coords(place: str, apikey: str):
    url = "https://geocode-maps.yandex.ru/1.x"
    params = {
        "geocode": place,
        "apikey": apikey,
        "format": "json",
    }
    response = get(url=url, params=params)
    response.raise_for_status()
    most_relevant = response.json()['response']['GeoObjectCollection']['featureMember'][0]
    if not most_relevant:
        return None
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat

def get_earthquakes(starttime: str, endtime: str, latitude: int, longitude: int):
    data = []
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format":"geojson",
        "eventtype": "earthquake",
        "starttime":starttime,
        "endtime":endtime,
        "latitude": latitude,
        "longitude": longitude,
        "maxradius": 180
    }
    response = get(url=url, params=params)
    response.raise_for_status()
    for event in response.json()["features"]:
        data.append({
            "place": event["properties"]["place"],
            "coords": event["geometry"]["coordinates"]
        })
    return data



def find_recent_earthquakes():
    # Получение данных для запроса
    load_dotenv(find_dotenv())
    yandex_api_key = environ["YANDEX_API"]
    parser = ArgumentParser()
    parser.add_argument("place", type=str, help="Место, в радиусе которого будут найдены землетрясения")
    args = parser.parse_args()
    longitude, latitude = get_coords(args.place, apikey=yandex_api_key)
    last_earthquakes = get_earthquakes(f"{date.today().year}-{date.today().month}-{date.today().day-1}", date.today(), latitude, longitude)
    pprint(last_earthquakes)


    
if __name__ == "__main__":
    find_recent_earthquakes()