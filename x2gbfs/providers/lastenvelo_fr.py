import csv
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional, Tuple

import requests

from x2gbfs.gbfs.base_provider import BaseProvider
from x2gbfs.util import timestamp_to_isoformat


class LastenVeloFreiburgProvider(BaseProvider):
    LASTENVELO_API_URL = 'https://www.lastenvelofreiburg.de/LVF_usage.csv'

    BIKE_ID_COL_NAME = 'BikeID'
    TIMESTAMP_COL_NAME = 'UTC Timestamp'
    LAT_COL_NAME = 'lattitude of station'
    LON_COL_NAME = 'longitude of station'
    RENTAL_STATE_COL_NAME = 'rental state (available, rented or defect)'
    DEEPLINK_COL_NAME = 'link to booking calender'
    BIKE_NAME_COL_NAME = 'name of bike'
    FURTHER_INFO_COL_NAME = 'further information'
    AVAILABLE_UNTIL_COL_NAME = 'latest time bike needs to be returned'

    DEFAULT_MAX_RANGE = 60000
    DEFAULT_CURRENT_RANGE = 30000

    VEHICLE_NAMES_FOR_TYPE = {
        'three_wheeled_bike_for_load_and_child': 'Lastenrad, 3-rädrig - Kindertransport möglich',
        'three_wheeled_bike_for_load_only': 'Lastenrad, 3-rädrig - Kein Kindertransport',
        'three_wheeled_trailer': 'Fahrrad mit Anhänger -  Kein Kindertransport',
        'two_wheeled_bike_for_child_only': 'Lastenrad, 2-rädrig - Nur Kindertransport',
        'two_wheeled_bike_for_load_and_child': 'Lastenrad, 2-rädrig - Kindertransport möglich',
        'two_wheeled_bike_for_load_only': 'Lastenrad, 2-rädrig - Kein Kindertransport',
    }

    lastenvelo_csv: str = ''

    def _load_lastenvelo_csv(self) -> None:
        response = requests.get(
            self.LASTENVELO_API_URL, headers={'User-Agent': 'x2gbfs +https://github.com/mobidata-bw/'}, timeout=5
        )
        response.raise_for_status()

        # API returns Content-Type: text/csv, though it should Content-Type: text/csv; charset=utf-8
        response.encoding = response.apparent_encoding

        content = response.text
        self.lastenvelo_csv = content

    def _all_lastenvelo_rows(self) -> Generator[Dict, None, None]:
        if not self.lastenvelo_csv:
            self._load_lastenvelo_csv()

        reader = csv.DictReader(self.lastenvelo_csv.splitlines(), delimiter=',')
        for row in reader:
            yield row

    def _extract_vehicle_and_type(self, row: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        last_reported = int(float(row[self.TIMESTAMP_COL_NAME]))
        further_information = row[self.FURTHER_INFO_COL_NAME]
        has_engine = 'mit Motor' in further_information
        vehicle_type_id = self._vehicle_type_id(row)

        gbfs_vehicle_type = {
            'vehicle_type_id': vehicle_type_id,
            'form_factor': 'cargo_bicycle',
            'propulsion_type': 'electric_assist' if has_engine else 'human',
            'name': self._vehicle_name_for_type(vehicle_type_id),
            'return_type': 'roundtrip',
            'default_pricing_plan_id': 'kostenfrei',
            'wheel_count': 3 if '3-rädrig' in further_information or 'hänger' in further_information else 2,
            'rider_capacity': 2 if 'Kindertransport' in further_information else 1,
        }

        if has_engine:
            gbfs_vehicle_type['max_range_meters'] = self.DEFAULT_MAX_RANGE

        gbfs_vehicle = {
            'bike_id': row[self.BIKE_ID_COL_NAME],
            'vehicle_type_id': vehicle_type_id,
            'station_id': self._station_id(row),
            'is_reserved': 'rented' in row[self.RENTAL_STATE_COL_NAME],
            'is_disabled': 'defect' in row[self.RENTAL_STATE_COL_NAME],
            'current_range_meters': self.DEFAULT_CURRENT_RANGE,
            'rental_uris': {
                'web': row[self.DEEPLINK_COL_NAME],
            },
            'last_reported': last_reported,
        }

        available_until_value = row[self.AVAILABLE_UNTIL_COL_NAME]
        if len(available_until_value) > 0:
            available_until = datetime.fromtimestamp(int(float(available_until_value)), tz=timezone.utc)
            gbfs_vehicle['available_until'] = timestamp_to_isoformat(available_until)

        return gbfs_vehicle, gbfs_vehicle_type

    def _station_id(self, row: Dict[str, str]) -> str:
        return '{:.6f}_{:.6f}'.format(float(row[self.LAT_COL_NAME]), float(row[self.LON_COL_NAME])).replace('.', '-')

    def _vehicle_name_for_type(self, vehicle_type_id: str) -> str:
        return self.VEHICLE_NAMES_FOR_TYPE[vehicle_type_id]

    def _vehicle_type_id(self, row: Dict[str, str]) -> str:
        """
        Returns vehicle_type_id depending on property `further information`.
        """

        further_information = row[self.FURTHER_INFO_COL_NAME]
        if '2-rädrig' in further_information:
            wheel_type = 'two_wheeled'
        elif '3-rädrig' in further_information or 'Fahrrad mit Anhänger' in further_information:
            wheel_type = 'three_wheeled'
        else:
            raise Exception(f'Unexpected wheel type "{further_information}"')

        if 'Nur Kindertransport' in further_information:
            bike_type = 'bike_for_child_only'
        elif 'Kindertransport möglich' in further_information:
            bike_type = 'bike_for_load_and_child'
        elif 'Fahrrad mit Anhänger' in further_information:
            bike_type = 'trailer'
        else:
            bike_type = 'bike_for_load_only'

        return f'{wheel_type}_{bike_type}'

    def _extract_station_info_and_state(self, row: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        last_reported = int(float(row[self.TIMESTAMP_COL_NAME]))
        station_id = self._station_id(row)

        info = {
            'lat': float(row[self.LAT_COL_NAME]),
            'lon': float(row[self.LON_COL_NAME]),
            'name': row[self.BIKE_NAME_COL_NAME],
            'station_id': station_id,
            'home_station_id': station_id,
            # 'addresss': Not provided
            # 'post_code': Not provided
            'rental_methods': ['key'],
            'is_charging_station': 'ohne Ladestation' not in row[self.FURTHER_INFO_COL_NAME],
            'rental_uris': {
                'web': row[self.DEEPLINK_COL_NAME],
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
