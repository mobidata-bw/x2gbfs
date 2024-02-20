import logging
from typing import Dict, Optional, Tuple

from x2gbfs.gbfs.base_provider import BaseProvider
import requests, re

logger = logging.getLogger(__name__)

class Counter:
    """
    A utiltiy class to group certain cars by their station id.
    """
    cars = {}
    def __init__(self):
        pass

    def count_car(self, station_id, type):
        if self.cars.get(station_id) is None:
            self.cars[station_id] = { type: 1 }
        elif self.cars[station_id].get(type) is None:
            self.cars[station_id][type] = 1
        else:
            count = self.cars[station_id][type]
            self.cars[station_id][type] = count + 1

class NoiProvider(BaseProvider):
    """
    This is an ExampleProvider which demonstrates how to implement a free-floatig only, e.g. scooter,
    provider.

    As it is not station based, only vehicles and one sigle vehicle type need to e extracted
    from the base system. This demo just returns some fake objects.

    System information and pricing information is read from config/example.json.

    Note: to be able to run this via x2gbfs, this ExampleProvider needs to
    is added to x2gbfs.py's build_extractor method.

    """

    STATION_URL = "https://mobility.api.opendatahub.com/v2/flat%2Cnode/CarsharingStation?limit=500&offset=0&shownull=false&distinct=true"
    CAR_URL = "https://mobility.api.opendatahub.com/v2/flat%2Cnode/CarsharingCar?limit=500&offset=0&shownull=false&distinct=true"

    def __init__(self):
        pass

    def load_vehicles(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        response = requests.get(self.CAR_URL, timeout=20)
        raw_cars = response.json()["data"]
        types = {}
        for i in raw_cars:

                id = self.extract_type_id(i)
                types[id] = {
                    # See https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md#vehicle_typesjson
                    'vehicle_type_id': id,
                    'form_factor': 'car',
                    'propulsion_type': self.extract_propulsion(i),
                    'max_range_meters': 500000,
                    'name': i["smetadata"]["brand"].strip(),
                    'wheel_count': 4
                }
        return types, {}

    def extract_type_id(self, i):
        stripped = i["smetadata"]["brand"].lower().strip().replace("!", "")
        return re.sub(r'[^a-z0-9]+', '-', stripped)

    def extract_propulsion(self, i):
        if(self.extract_type_id(i).__contains__("elektro")):
            return "electric"
        else:
            return "combustion"


    def load_stations(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:

        response = requests.get(self.STATION_URL, timeout=20)
        raw_stations = response.json()["data"]

        info = {}
        for i in raw_stations:
            id = i["scode"]
            coord = i["scoordinate"]
            info[id] = {
                "station_id": id,
                "name": i["sname"],
                "lon": coord["x"],
                "lat": coord["y"],
            }

        status = self.load_status(default_last_reported)
        return info, status,

    def load_status(self, last_reported: int) -> Optional[Dict]:
        response = requests.get(self.CAR_URL, timeout=20)
        raw_cars = response.json()["data"]
        infos = {}
        counter = Counter()
        for i in raw_cars:

            if i.get("pcode") is not None:
                id = i["pcode"]
                type_id = self.extract_type_id(i)
                counter.count_car(id, type_id)

        for station_id, counts in counter.cars.items():

            avail = []

            for type_id in counts:
                avail.append({
                    "vehicle_type_id": type_id,
                    "count": counts[type_id]
                })

            infos[station_id] = {
                "station_id": station_id,
                "num_bikes_available" : 1,
                "is_installed": True,
                "is_renting": True,
                "is_returning": True,
                "last_reported": last_reported,
                "vehicle_types_available": avail
        }
        return infos




