from requests import get
from datetime import date
from geopy import distance
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


def dist_compare(usr_lat: int, usr_lon: int, event_lat: int, event_lon: int):
    user_coords = (usr_lat, usr_lon)
    event_coords = (event_lat, event_lon)
    print(user_coords, "\n", event_coords)
    return round(distance.distance(user_coords, event_coords).km)


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
        "maxradiuskm": 20001,
    }
    response = get(url=url, params=params)
    response.raise_for_status()
    for event in response.json()["features"]:
        event_latitude = event["geometry"]["coordinates"][1]
        event_longitude = event["geometry"]["coordinates"][0]
        data.append({
            "title": event["properties"]["title"],
            "place": event["properties"]["place"],
            "time": event["properties"]["time"],
            "distance": dist_compare(latitude, longitude, event_latitude, event_longitude),
            "map": f"{event["properties"]["url"]}/map",
            "latitude": event_latitude,
            "longitude": event_longitude
            })

    return data


def find_recent_earthquakes(days_ago=1):
    # Получение всех данных и формирование сообщения для отправки
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