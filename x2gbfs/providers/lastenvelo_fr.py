import csv
from typing import Any, Dict, Generator, Optional, Tuple

import requests

from x2gbfs.gbfs.base_provider import BaseProvider


class LastenVeloFreiburgProvider(BaseProvider):
    lastenvelo_csv: str = ''

    LASTENVELO_API_URL = 'https://www.lastenvelofreiburg.de/LVF_usage.html'

    REPLACEMENTS = {
        'UTC Timestamp,Human readable Timestamp,BikeID,lattitude of station,longitude of station,rental state (available, rented or defect),name of bike,further information': 'UTC Timestamp,Human readable Timestamp,BikeID,lat,lon,rental_state,bike_name,further information,url',
        '<br>': '\n',
    }

    def _load_lastenvelo_csv(self) -> None:
        response = requests.get(
            self.LASTENVELO_API_URL, headers={'User-Agent': 'x2gbfs +https://github.com/mobidata-bw/'}, timeout=5
        )
        response.raise_for_status()

        content = response.text
        # Need to fix header (fieldnames contain commata) and linebreaks
        for key, value in self.REPLACEMENTS.items():
            content = content.replace(key, value)

        self.lastenvelo_csv = content

    def _all_lastenvelo_rows(self) -> Generator[Dict, None, None]:
        if not self.lastenvelo_csv:
            self._load_lastenvelo_csv()

        reader = csv.DictReader(self.lastenvelo_csv.splitlines(), delimiter=',')
        for row in reader:
            yield row

    def _extract_vehicle_and_type(self, row: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        last_reported = int(float(row['UTC Timestamp']))
        further_information = row['further information']
        has_engine = 'mit Motor' in further_information
        vehicle_type_id = self._vehicle_type_id(row)

        gbfs_vehicle_type = {
            'vehicle_type_id': vehicle_type_id,
            'form_factor': 'cargo_bicycle',
            'propulsion_type': 'electric_assist' if has_engine else 'human',
            'name': self._bike_name_without_number(row),
            'return_type': 'roundtrip',
            'default_pricing_plan_id': 'kostenfrei',
            'wheel_count': 3 if '3-rädrig' in further_information else 2,
            'rider_capacity': 2 if 'Kindertransport' in further_information else 1,
        }

        if has_engine:
            gbfs_vehicle_type['max_range_meters'] = 20000

        gbfs_vehicle = {
            'bike_id': row['BikeID'],
            'vehicle_type_id': vehicle_type_id,
            'station_id': self._station_id(row),
            'is_reserved': 'rented' in row['rental_state'],
            'is_disabled': 'defect' in row['rental_state'],
            'current_range_meters': 20000,
            'rental_uris': {
                'web': row['url'],
            },
            'last_reported': last_reported,
        }

        return gbfs_vehicle, gbfs_vehicle_type

    def _station_id(self, row: Dict[str, str]) -> str:
        return f'{row["lat"]}_{row["lon"]}'

    def _bike_name_without_number(self, row: Dict[str, str]) -> str:
        name = row['bike_name']

        if ' - ' in name:
            return name[name.index(' - ') + 3 :]
        return name

    def _vehicle_type_id(self, row: Dict[str, str]) -> str:
        name = self._bike_name_without_number(row).lower()

        if 'carla' in name:
            return 'carla'

        return name.replace(' - ', '_').replace(' ', '_')

    def _extract_station_info_and_state(self, row: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        last_reported = int(float(row['UTC Timestamp']))
        station_id = self._station_id(row)

        info = {
            'lat': float(row['lat']),
            'lon': float(row['lon']),
            'name': row['bike_name'],
            'station_id': station_id,
            'home_station_id': station_id,
            # 'addresss': Not provided
            # 'post_code': Not provided
            'rental_methods': ['key'],
            'is_charging_station': 'ohne Ladestation' not in row['further information'],
            'rental_uris': {
                'web': row['url'],
            },
        }

        return info, self._create_station_status(station_id, last_reported)

    def load_vehicles(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        vehicles = {}
        vehicle_types = {}

        for vehicle in self._all_lastenvelo_rows():
            gbfs_vehicle, vehicle_type = self._extract_vehicle_and_type(vehicle)
            vehicles[gbfs_vehicle['bike_id']] = gbfs_vehicle
            vehicle_types[vehicle_type['vehicle_type_id']] = vehicle_type

        return vehicle_types, vehicles

    def load_stations(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        status = {}
        infos = {}

        for row in self._all_lastenvelo_rows():
            info, state = self._extract_station_info_and_state(row)
            status[state['station_id']] = state
            infos[info['station_id']] = info

        return infos, status
