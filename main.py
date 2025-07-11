from requests import get
from datetime import date
from argparse import ArgumentParser
from os import environ
from dotenv import load_dotenv, find_dotenv
from time import sleep


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

def get_data(starttime: str, endtime: str, latitude: int, longitude: int, maxradius: int):
    data = []
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format":"geojson",
        "eventtype": "earthquake",
        "starttime":starttime,
        "endtime":endtime,
        "latitude": latitude,
        "longitude": longitude,
        "maxradius": maxradius
    }
    response = get(url=url, params=params)
    response.raise_for_status()
    for event in response.json()["features"]:
        data.append({
            "place": event["properties"]["place"],
            "coords": event["geometry"]["coordinates"]
        })
    return data



def main():
    # Получение данных для запроса
    load_dotenv(find_dotenv())
    yandex_api_key = environ["YANDEX_API"]
    parser = ArgumentParser()
    parser.add_argument("place", type=str, help="Место, в радиусе которого будут найдены землетрясения")
    parser.add_argument("--maxradius", type=str, help="Максимальный радиус в котором будут найдены землетрясения", default=50)
    args = parser.parse_args()
    longitude, latitude = get_coords(args.place, apikey=yandex_api_key)
    data = get_data(date.today(), date.today(), latitude, longitude, args.maxradius)
    events_count = len(data)
    # Основной цикл
    while 1:
        new_data = get_data(args.starttime, date.today(), latitude, longitude, args.maxradius)
        new_events = len(new_data)
        print(f"Кол-во землятресений - {events_count}")
        print(f"Кол-во землятресений (new) - {new_events}")
        if new_events > events_count:
            print("Новое землетрясение!")
            print(new_data[len(new_data)-1])
            data = new_data
            events_count = new_events
        sleep(3)


    
if __name__ == "__main__":
    main()