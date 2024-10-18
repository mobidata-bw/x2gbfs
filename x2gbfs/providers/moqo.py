import logging
import re
from datetime import datetime
from typing import Any, Dict, Generator, Optional, Tuple

from decouple import config

from x2gbfs.gbfs.base_provider import BaseProvider
from x2gbfs.util import get

logger = logging.getLogger('x2gbfs.moqo')


class MoqoProvider(BaseProvider):
    FUEL_TYPE_MAPPING = {
        'electric': 'electric',
        'super_petrol': 'combustion',
        'natural_gas': 'combustion',
        'liquid_gas': 'combustion',
        'bio_gas': 'combustion',
        'hybrid_electric_petrol': 'hybrid',
        'hybrid_electric_diesel': 'hybrid',
        'hydrogen': 'hydrogen_fuel_cell',
        'plugin_hybrid_petrol': 'plug_in_hybrid',
        'plugin_hybrid_diesel': 'plug_in_hybrid',
    }

    CARS_REQUEST_PARAMS = {
        'fields[cars]': 'id,license,fuel_type,vehicle_type,car_type,fuel_level',  # is cruising_range available?
        'extra_fields[cars]': 'car_model_name,available',
        'include': 'latest_parking',  # vehicle_categories is not helpful for stadtwerke-tauberfranken
        'fields[latest_parking]': 'id',
        'page[size]': '200',
    }

    DEFAULT_CURRENT_FUEL_PERCENT = 0.5
    DEFAULT_MAX_RANGE_METERS = 250000
    DEFAULT_PRICING_PLAN_ID = 'all_hour_daytime'
    DEFAULT_PRICING_PLAN_PATTERN = '{vehicle_type}_hour_daytime'
    MINIMUM_REQUIRED_AVAILABLE_TIMESPAN_IN_SECONDS = 60 * 60 * 3  # 3 hours

    def __init__(self, feed_config: dict[str, Any]):
        self.api_token = config('MOQO_API_TOKEN')
        self.config = feed_config
        self.team_id = feed_config['provider_data']['team_id']
        self.api_url = f'http://portal.moqo.de/d/{self.team_id}/api/graph/'

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

        for elem in self._get_paginated('parkings'):
            self._extract_from_parkings(elem, gbfs_station_infos_map, gbfs_station_status_map, default_last_reported)

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

        params = dict(self.CARS_REQUEST_PARAMS)
        params['filter[from]'] = self._format_timestamp(default_last_reported)
        params['filter[until]'] = self._format_timestamp(
            default_last_reported + self.MINIMUM_REQUIRED_AVAILABLE_TIMESPAN_IN_SECONDS
        )

        for elem in self._get_paginated('cars', params):
            self._extract_from_vehicles(elem, gbfs_vehicles_map, gbfs_vehicle_types_map)

        return gbfs_vehicle_types_map, gbfs_vehicles_map

    @staticmethod
    def _format_timestamp(timestamp: int) -> str:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M')

    def _get_paginated(self, element_type: str, params: Optional[dict[str, str]] = None):
        url = self.api_url + element_type
        headers = {'Authorization': f'Bearer {self.api_token}', 'accept': 'application/json'}
        page = 1
        while True:
            request_params = dict(params) if params is not None else {}
            request_params['page[number]'] = str(page)
            json_response = get(url, params=request_params, headers=headers).json()

            if 'data' in json_response:
                for elem in json_response['data']:
                    yield elem
            else:
                logger.warning(f'Response to {url} did not contain {element_type}')
                logger.warning(json_response)
                return

            if json_response.get('pagination', {}).get('next_page'):
                page += 1
            else:
                break

    def _extract_from_parkings(
        self,
        elem: dict[str, Any],
        gbfs_station_infos_map: dict[str, dict],
        gbfs_station_status_map: dict[str, dict],
        default_last_reported: int,
    ) -> None:
        station_id = elem['id']

        center = elem['center']
        station = {
            'lat': center['lat'],
            'lon': center['lng'],
            'name': elem['name'],
            'station_id': str(elem['id']),
            'address': elem['zipcode']
            + ' '
            + elem['town']
            + ', '
            + elem['street']
            + (' ' + elem['street_number'] if elem['street_number'] is not None else ''),
            'post_code': elem['zipcode'],
            'rental_methods': ['key'],
        }

        if elem['capacity_max']:
            station['capacity'] = elem['capacity_max']

        gbfs_station_infos_map[station_id] = station

        gbfs_station_status_map[station_id] = {
            'num_bikes_available': 0,
            'vehicle_types_available': {},
            'is_renting': True,
            'is_installed': True,
            'is_returning': True,
            'station_id': str(elem['id']),
            'last_reported': default_last_reported,
        }

    def _extract_from_vehicles(
        self,
        vehicle: dict[str, Any],
        vehicles: dict[str, Any],
        vehicle_types: dict[str, Any],
    ) -> None:
        vehicle_type_id = self._extract_vehicle_type(vehicle_types, vehicle)
        vehicle_id = vehicle['id']
        current_fuel_percent = (
            vehicle['fuel_level'] / 100.0 if 'fuel_level' in vehicle else self.DEFAULT_CURRENT_FUEL_PERCENT
        )
        current_range_meters = vehicle_types[vehicle_type_id]['max_range_meters'] * current_fuel_percent

        deeplink = f'https://go.moqo.de/deeplink/createBooking?teamId={self.team_id}&carId={vehicle_id}'

        gbfs_vehicle = {
            'bike_id': str(vehicle_id),
            'is_reserved': vehicle['available'] is not True,
            'is_disabled': False,
            'vehicle_type_id': vehicle_type_id,
            'license_plate': re.split(r'[(|]', vehicle['license'])[0].strip(),
            'current_range_meters': current_range_meters,
            'current_fuel_percent': current_fuel_percent,
            'rental_uris': {
                'web': deeplink,
                'ios': deeplink,
                'android': deeplink,
            },
        }

        if vehicle.get('latest_parking') is not None and vehicle.get('latest_parking', {}).get('id') is not None:
            gbfs_vehicle['station_id'] = vehicle.get('latest_parking', {}).get('id')
        else:
            logger.info('Vehicle %s has no station (is in use), will be removed from feed', vehicle_id)
            return  # ignore vehicle without station

        if vehicle.get('cruising_range') is not None and vehicle['cruising_range'].get('value'):
            gbfs_vehicle['current_range_meters'] = vehicle['cruising_range']['value']['cents'] * 1000

        # Links seems not to work currently, so we don't generate them
        # rental_uri = 'https://go.moqo.de/deeplink/createBooking?teamId={}&carId={}'.format(self.team_id, vehicle_id)
        # gbfs_vehicle['rental_uris'] = {
        #    'ios': rental_uri,
        #    'android': rental_uri,
        #    #'web': web_rental_uri
        # }

        vehicles[vehicle_id] = gbfs_vehicle

    def _extract_vehicle_type(self, vehicle_types: dict[str, Any], vehicle: dict[str, Any]) -> str:
        vehicle_model = vehicle['car_model_name']
        id = self._normalize_id(vehicle_model)
        gbfs_make, gbfs_model = vehicle_model.split(' ')[0], ' '.join(vehicle_model.split(' ')[1:])
        form_factor = self._map_car_type(vehicle['vehicle_type'])
        if not vehicle_types.get(id):
            vehicle_types[id] = {
                'vehicle_type_id': id,
                'form_factor': form_factor,
                'propulsion_type': self._map_fuel_type(vehicle['fuel_type']),
                'max_range_meters': self.DEFAULT_MAX_RANGE_METERS,
                'name': vehicle_model,
                'make': gbfs_make,
                'model': gbfs_model,
                'return_constraint': 'roundtrip_station',
                'default_pricing_plan_id': self._default_pricing_plan_id(vehicle['car_type']),
            }
            pricing_plan_ids = self._pricing_plan_ids(vehicle['car_type'])
            if pricing_plan_ids:
                vehicle_types[id]['pricing_plan_ids'] = pricing_plan_ids
        return id

    @staticmethod
    def _map_car_type(car_type: str) -> str:
        if car_type in {'bike'}:
            return 'bicycle'
        if car_type in {
            'car',
            'compact_car',
            'convertible',
            'demo_car',
            'limousine',
            'mini_car',
            'small_family_car',
            'sportscar',
            'vintage_car',
            'station_wagon',
            'suv',
            'transporter',
            'recreational_vehicle',
            'van',
        }:
            return 'car'
        if car_type in {'scooter'}:
            return 'moped'
        if car_type in {'kick_scooter'}:
            return 'scooter'
        if car_type in {'other'}:
            return 'other'

        logger.warning('Unknown car_type: %s', car_type)
        return 'other'

    @classmethod
    def _map_fuel_type(cls, fuel_type: str) -> str:
        if fuel_type in cls.FUEL_TYPE_MAPPING:
            return cls.FUEL_TYPE_MAPPING[fuel_type]

        logger.warning('Unknown fuel_type: %s, will use combustion', fuel_type)
        return 'combustion'

    @staticmethod
    def _defined_pricing_plan_ids(config) -> set[str]:
        return {pricing_plans['plan_id'] for pricing_plans in config.get('feed_data', {}).get('pricing_plans', [])}

    def _default_pricing_plan_id(self, vehicle_type: str) -> str:
        """
        Returns the default pricing plan defined in the providers config.
        If a pricing plan with plan_id matching the DEFAULT_PRICING_PLAN_PATTERN is defined,
        it is return, otherwise DEFAULT_PRICING_PLAN_ID. If neither of them is defined in the config,
        a ValueError is raised.
        """
        defined_pricing_plan_ids = self._defined_pricing_plan_ids(self.config)
        vehicle_type_default_pricing_plan_id = self.DEFAULT_PRICING_PLAN_PATTERN.format(vehicle_type=vehicle_type)
        if vehicle_type_default_pricing_plan_id in defined_pricing_plan_ids:
            return vehicle_type_default_pricing_plan_id
        if self.DEFAULT_PRICING_PLAN_ID in defined_pricing_plan_ids:
            return self.DEFAULT_PRICING_PLAN_ID

        raise ValueError(
            'Neither for "{vehicle_type_default_pricing_plan_id}" nor "{self.DEFAULT_PRICING_PLAN_ID}" a pricing plan was defined in config'
        )

    def _pricing_plan_ids(self, vehicle_type: str) -> list[str]:
        """
        Returns a list of all pricing plan defined in the providers config, if their plan_id
        start with the vehicle_type. If this set is empty, all pricing plans starting with `all_`
        are returned. This might be an empty list.
        """
        defined_pricing_plan_ids = self._defined_pricing_plan_ids(self.config)
        pricing_plan_ids = [plan_id for plan_id in defined_pricing_plan_ids if plan_id.startswith(vehicle_type)]
        if not pricing_plan_ids:
            pricing_plan_ids = [plan_id for plan_id in defined_pricing_plan_ids if plan_id.startswith('all_')]
        return pricing_plan_ids


class StadtwerkTauberfrankenProvider(MoqoProvider):
    pass


class ZeagEnergieProvider(MoqoProvider):
    pass
