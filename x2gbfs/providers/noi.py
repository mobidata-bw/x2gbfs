import logging
import requests
import re
from typing import Dict, Optional, Tuple
from x2gbfs.gbfs.base_provider import BaseProvider

logger = logging.getLogger(__name__)

class NoiProvider(BaseProvider):
    STATION_URL = 'https://mobility.api.opendatahub.com/v2/flat%2Cnode/CarsharingStation?limit=500&offset=0&shownull=false&distinct=true'
    CAR_URL = 'https://mobility.api.opendatahub.com/v2/flat%2Cnode/CarsharingCar?limit=500&offset=0&shownull=false&distinct=true'

    def __init__(self):
        pass

    def load_vehicles(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        response = requests.get(self.CAR_URL, timeout=20)
        raw_cars = response.json()['data']
        types = {}
        vehicles = {}
        for i in raw_cars:

            type_id = self.extract_type_id(i)
            types[type_id] = {
                # See https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md#vehicle_typesjson
                'vehicle_type_id': type_id,
                'form_factor': 'car',
                'propulsion_type': self.extract_propulsion(i),
                'max_range_meters': 500000,
                'name': i['smetadata']['brand'].strip(),
                'wheel_count': 4
            }

            if i.get('pcode') is not None:
                id = self.slugify(i['smetadata']['licensePlate'])
                vehicles[id] = {
                    "bike_id": id,
                    "station_id": i['pcode'],
                    "vehicle_type_id": type_id,
                    "is_reserved": False,
                    "is_disabled": False,
                    "current_range_meters": 500000
                }

        return types, vehicles

    def extract_type_id(self, i):
        return self.slugify(i['smetadata']['brand'])

    def slugify(self, input):
        output = input.lower().strip().replace('!', '')
        output = re.sub(r'[^a-z0-9]+', '-', output)
        return re.sub(r'-$', '', output)

    def extract_propulsion(self, i):
        if(self.extract_type_id(i).__contains__('elektro')):
            return 'electric'
        return 'combustion'


    def load_stations(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:

        response = requests.get(self.STATION_URL, timeout=20)
        raw_stations = response.json()['data']

        info = {}
        for i in raw_stations:
            id = i['scode']
            coord = i['scoordinate']
            info[id] = {
                'station_id': id,
                'name': i['sname'],
                'lon': coord['x'],
                'lat': coord['y'],
            }

        status = self.load_status(default_last_reported)
        return info, status

    def load_status(self, last_reported: int) -> Optional[Dict]:
        response = requests.get(self.CAR_URL, timeout=20)
        raw_cars = response.json()['data']
        statuses = {}

        for i in raw_cars:

            if i.get('pcode') is not None:

                station_id = i['pcode']
                statuses[station_id] = {
                    'station_id': station_id,
                    'is_installed': True,
                    'is_renting': True,
                    'is_returning': True,
                    'last_reported': last_reported
                }
        return statuses
