from requests import get
from datetime import date, datetime
from geopy import distance
from os import environ


def get_coords(place: str, apikey: str):
    # Получение координат по названию места
    url = "https://geocode-maps.yandex.ru/1.x"
    params = {
        "geocode": place,
        "apikey": apikey,
        "format": "json",
    }
    response = get(url=url, params=params)
    response.raise_for_status()
    most_relevant = response.json()['response']['GeoObjectCollection']['featureMember']
    if not len(most_relevant):
        return None, None
    lon, lat = most_relevant[0]['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def dist_compare(usr_lat: int, usr_lon: int, event_lat: int, event_lon: int):
    # Сравнение координат и получние дистанции между ними
    user_coords = (usr_lat, usr_lon)
    event_coords = (event_lat, event_lon)
    print(user_coords, "\n", event_coords)
    return round(distance.distance(user_coords, event_coords).km)


def get_earthquakes(starttime: str, endtime: str, latitude: int, longitude: int):
    # Получение данных о последних землетрясениях
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
        formatted_date = datetime.fromtimestamp(event["properties"]["time"]/1000).strftime("%Y-%m-%d %H:%M:%S") #event["properties"]["time"]
        data.append({
            "title": event["properties"]["title"],
            "place": event["properties"]["place"],
            "date": formatted_date,
            "distance": dist_compare(latitude, longitude, event_latitude, event_longitude),
            "map": f"{event["properties"]["url"]}/map",
            "latitude": event_latitude,
            "longitude": event_longitude
            })

    return data


def find_last_earthquakes(lat: float, lon: float, days_ago: int):
    # Получение всех данных и формирование сообщения для отправки
    last_earthquakes = get_earthquakes(f"{date.today().year}-{date.today().month}-{date.today().day-days_ago}", date.today(), lat, lon)
    return last_earthquakes

