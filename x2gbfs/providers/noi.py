import logging
from typing import Dict, Optional, Tuple

from x2gbfs.gbfs.base_provider import BaseProvider
import requests, re

logger = logging.getLogger(__name__)


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

    VEHICLE_TYPES = {
        'scooter': {
            # See https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md#vehicle_typesjson
            'vehicle_type_id': 'vw-golf',
            'form_factor': 'car',
            'propulsion_type': 'combustion',
            'max_range_meters': 500000,
            'name': 'VW Golf',
            'wheel_count': 4
        }
    }

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
                    'propulsion_type': 'combustion',
                    'max_range_meters': 500000,
                    'name': i["smetadata"]["brand"].strip(),
                    'wheel_count': 4
                }
        return types, {}

    def extract_type_id(self, i):
        stripped = i["smetadata"]["brand"].lower().strip().replace("!", "")
        return re.sub(r'[^a-z0-9]+', '-', stripped)

    def load_stations(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Retrieves stations from the providers API and converts them
        into gbfs station infos and station status.
        Returns dicts where the key is the station_id and values
        are station_info/station_status.

        For free floating only providers, this method needs not to be overwritten.

        Note: station status' vehicle availabilty currently will be calculated
        using vehicle information's station_id, in case it is defined by this
        provider.
        """

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
        for i in raw_cars:

            if i.get("pcode") is not None:
                id = i["pcode"]
                infos[id] = {
                    "station_id": id,
                    "num_bikes_available" : 1,
                    "is_installed": True,
                    "is_renting": True,
                    "is_returning": True,
                    "last_reported": last_reported,
                    "vehicle_types_available": [{
                        "vehicle_type_id": self.extract_type_id(i),
                        "count": 1
                    }]
                }
        return infos




