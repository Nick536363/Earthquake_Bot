from requests import get
from datetime import date
from argparse import ArgumentParser


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
    parser = ArgumentParser()
    parser.add_argument("latitude", type=str, help="Географическая широта, в радиусе которой будут найдены землетрясения")
    parser.add_argument("longitude", type=str, help="Географическая долгота, в радиусе которой будут найдены землетрясения")
    parser.add_argument("--maxradius", type=str, help="Максимальный радиус в котором будут найдены землетрясения", default=180)
    parser.add_argument("--starttime", type=str, help="Дата (YYYY-MM-DD), от которой будут найдены землетрясения", default=date.today())
    parser.add_argument("--endtime", type=str, help="Дата (YYYY-MM-DD), до которой будут найдены землетрясения", default=date.today())
    args = parser.parse_args()
    get_data(args.starttime, args.endtime, args.latitude, args.longitude, args.maxradius)

    
if __name__ == "__main__":
    main()