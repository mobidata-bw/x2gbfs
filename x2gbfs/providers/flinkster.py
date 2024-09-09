import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, Generator, Optional, Tuple

from decouple import config

from x2gbfs.gbfs.base_provider import BaseProvider
from x2gbfs.util import get

logger = logging.getLogger('x2gbfs.flinkster')


class FlinksterProvider(BaseProvider):

    profileUid = 'Flinkster'
    api_url = 'https://apis.deutschebahn.com/db/apis/dbconnect-b2b-direct/v2'

    DEFAULT_MAX_RANGE_METERS = 200000

    FUELTYPE_TO_PROPULSION_MAPPING = {
        'electric': 'electric',
        'petrol': 'combustion',
        'multifuel': 'combustion',
        'diesel': 'combustion_diesel',
        'hybrid': 'hybrid',
    }

    CATEGORY_PRICING_PLAN_MAPPING = {
        '1000': 'mini',
        '1001': 'small',
        '1002': 'compact',
        '1003': 'medium',
        '1004': 'transporter',
    }

    def __init__(self, feed_config: dict):
        self.client_id = config('FLINKSTER_CLIENT_ID')
        self.secret = config('FLINKSTER_SECRET')
        self.config = feed_config
        self.pricing_plan_ids = [plan['plan_id'] for plan in feed_config['feed_data']['pricing_plans']]

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

        gbfs_station_infos_map: dict[str, dict] = {}
        gbfs_station_status_map: dict[str, dict] = {}

        for elem in self._all_areas():
            self._extract_from_area(elem, gbfs_station_infos_map, gbfs_station_status_map, default_last_reported)

        return gbfs_station_infos_map, gbfs_station_status_map

    def load_vehicles(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Retrieves vehicles and vehicle types from provider's API and converts them
        into gbfs vehicles, vehicle_types.
        Returns dicts where the key is the vehicle_id/vehicle_type_id and values
        are vehicle/vehicle_type.
        """
        gbfs_vehicle_types_map: dict[str, dict] = {}
        gbfs_vehicles_map: dict[str, dict] = {}

        for elem in self._all_vehicles():
            self._extract_from_vehicle(elem, gbfs_vehicles_map, gbfs_vehicle_types_map)

        return gbfs_vehicle_types_map, gbfs_vehicles_map

    def _all_elements(self, url: str, element_name: str, filter) -> Generator[Dict, None, None]:
        while True:
            response = self._get_with_authorization(url)
            for elem in response['_embedded'][element_name]:
                if filter(elem):
                    yield elem
            if response['_links'].get('next'):
                url = response['_links'].get('next')['href']
            else:
                break

    def _all_areas(self) -> Generator[Dict, None, None]:
        areas_url = f'{self.api_url}/areas?size=2000&profileUid={self.profileUid}'
        return self._all_elements(areas_url, 'areas', lambda e: e['areaType'] not in ['noparkingarea', 'operationarea'])

    def _all_vehicles(self) -> Generator[Dict, None, None]:
        vehicles_url = f'{self.api_url}/availableRentalObjects?expands=name,type,fillLevel,fuelType,position,category,licensePlate&size=2000&profileUid={self.profileUid}'
        return self._all_elements(
            vehicles_url, 'rentalObjects', lambda e: e['type'] in ['vehicle', 'vehicle_electric', 'vehiclepool']
        )

    def _get_with_authorization(self, url: str) -> dict:
        headers = {'db-client-id': self.client_id, 'db-api-key': self.secret}
        return get(url, headers=headers).json()

    def _extract_from_area(
        self, elem: dict, gbfs_station_infos_map: dict, gbfs_station_status_map: dict, default_last_reported: int
    ) -> None:
        '''
        Extract station from area. Example of an area JSON object:
            "address": {
                    "city": "Stuttgart",
                    "district": "Hedelfingen",
                    "number": "2",
                    "street": "Friedrichshafener Str.",
                    "zip": "70329"
                },
                "areaType": "station",
                "attributes": {},
                "geometry": {
                    "position": {
                        "coordinates": [
                            9.255481,
                            48.758384
                        ],
                        "type": "Point"
                    }
                },
                "name": "Hedelfingen Volksbank",
                "provider": {
                    "name": "Ford Carsharing",
                    "uid": "fcs_krautter"
                },
                "providerAreaId": "408332",
                "rentalObjectTypes": [
                    "vehicle"
                ],
                "uid": "97c98671-9dbb-4a9e-a4b9-64ae47ff832c"
            },
        '''
        station_id = elem['uid']
        try:
            if elem['geometry']['position']['type'] == 'Point':
                pos = elem['geometry']['position']['coordinates']
            else:
                pos = elem['geometry']['centroid']['coordinates']

            station = {
                'lat': float(pos[1]),
                'lon': float(pos[0]),
                'name': elem['name'],
                'station_id': station_id,
                'is_virtual_station': True,
                'rental_methods': ['key'],
                'address': f"{elem['address']['city']}, {elem['address'].get('street')} {elem['address'].get('number')}",
            }

            if 'zip' in elem.get('address', {}):
                station['post_code'] = elem['address']['zip']

            gbfs_station_infos_map[station_id] = station

            gbfs_station_status_map[station_id] = {
                'is_renting': True,
                'is_installed': True,
                'is_returning': True,
                'station_id': station_id,
                'num_bikes_available': 0,
                'last_reported': default_last_reported,
            }
        except (KeyError, IndexError, TypeError):
            logger.exception(f'Station extraction for {station_id} failed!')

    def _extract_pricing_plan_ids(self, categoryId: str):
        pricing_plan_prefix = self.CATEGORY_PRICING_PLAN_MAPPING.get(categoryId)
        default_pricing_plan_id = f'{pricing_plan_prefix}_hour'
        alternative_pricing_plan_id = f'{pricing_plan_prefix}_day'
        if default_pricing_plan_id not in self.pricing_plan_ids:
            logger.warn(f'default_pricing_plan_id {default_pricing_plan_id} not defined in config')
        if alternative_pricing_plan_id not in self.pricing_plan_ids:
            logger.warn(f'alternative_pricing_plan_id {alternative_pricing_plan_id} not defined in config')

        return default_pricing_plan_id, [default_pricing_plan_id, alternative_pricing_plan_id]

    def _extract_vehicle_type(self, elem: dict) -> dict:
        vehicle_type_id = FlinksterProvider._normalize_id(elem['name'])

        splitted_name = elem['name'].split(' ')
        make = splitted_name[0]
        type = splitted_name[1] if len(splitted_name) > 1 else ''

        propulsion_type = self.FUELTYPE_TO_PROPULSION_MAPPING[elem['fuelType']] if 'fuelType' in elem else 'combustion'
        max_range_meters = self.DEFAULT_MAX_RANGE_METERS

        default_pricing_plan_id, pricing_plan_ids = self._extract_pricing_plan_ids(elem['categoryId'])

        gbfs_vehicle_type = {
            'vehicle_type_id': vehicle_type_id,
            'form_factor': 'car',
            'propulsion_type': propulsion_type,
            'max_range_meters': max_range_meters,
            'name': f'{make} {type}'.strip(),
            'make': make,
            'type': type,
            'default_pricing_plan_id': default_pricing_plan_id,
            'pricing_plan_ids': pricing_plan_ids,
            'wheel_count': 4,
            'return_constraint': 'roundtrip_station',
        }
        rider_capacity_match = re.search(r'(\d)-?sitze', elem['name'].lower())
        if rider_capacity_match:
            gbfs_vehicle_type['rider_capacity'] = int(rider_capacity_match.group(1))

        vehicle_accessories = ['navigation'] if 'ohne Navi' not in elem['categoryName'] else []
        doors_match = re.search(r'(\d)-?tür', elem['name'].lower())
        if doors_match:
            vehicle_accessories.append(f'doors_{doors_match.group(1)}')

        if len(vehicle_accessories) > 0:
            gbfs_vehicle_type['vehicle_accessories'] = vehicle_accessories

        return gbfs_vehicle_type

    def _extract_from_vehicle(self, elem: dict, gbfs_vehicles_map: dict, gbfs_vehicle_types_map: dict) -> None:
        try:
            gbfs_vehicle_type = self._extract_vehicle_type(elem)
            vehicle_type_id = gbfs_vehicle_type['vehicle_type_id']
            vehicle_id = elem['uid']

            current_fuel_percent = elem.get('fillLevel', 25.0) / 100.0
            current_range_meters = gbfs_vehicle_type['max_range_meters'] * current_fuel_percent

            gbfs_vehicle = {
                'bike_id': vehicle_id,
                'is_reserved': False,
                'is_disabled': False,
                'vehicle_type_id': vehicle_type_id,
                'station_id': elem['areaUid'],
                'current_range_meters': current_range_meters,
                'current_fuel_percent': current_fuel_percent,
            }

            # vehiclepools are anonymous vehicles without licensePlate
            if 'licensePlate' in elem:
                gbfs_vehicle['license_plate'] = elem['licensePlate']

            gbfs_vehicles_map[vehicle_id] = gbfs_vehicle
            gbfs_vehicle_types_map[vehicle_type_id] = gbfs_vehicle_type

        except KeyError:
            logger.exception(f'Vehicle extraction for {vehicle_id} failed!')
