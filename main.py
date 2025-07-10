from requests import get
from datetime import date
from argparse import ArgumentParser
from os import environ
from dotenv import load_dotenv, find_dotenv


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
        print(event["properties"]["type"])
        print(event["properties"]["place"])
        print(event["geometry"]["coordinates"])
        print("\n\n")


def main():
    load_dotenv(find_dotenv())
    yandex_api_key = environ["YANDEX_API"]
    parser = ArgumentParser()
    parser.add_argument("place", type=str, help="Место, в радиусе которого будут найдены землетрясения")
    parser.add_argument("--maxradius", type=str, help="Максимальный радиус в котором будут найдены землетрясения", default=180)
    parser.add_argument("--starttime", type=str, help="Дата (YYYY-MM-DD), от которой будут найдены землетрясения", default=date.today())
    parser.add_argument("--endtime", type=str, help="Дата (YYYY-MM-DD), до которой будут найдены землетрясения", default=date.today())
    args = parser.parse_args()
    longitude, latitude = get_coords(args.place, apikey=yandex_api_key)
    get_data(args.starttime, args.endtime, latitude, longitude, args.maxradius)

    
if __name__ == "__main__":
    main()