import logging
import re
from typing import Any, Dict, Generator, Optional, Tuple

from x2gbfs.gbfs.base_provider import BaseProvider

logger = logging.getLogger('x2gbfs.deer')


class Deer(BaseProvider):
    def __init__(self, api):
        self.api = api

    def all_stations(self) -> Generator[Dict, None, None]:
        for location in self.api.all_stations():
            if location['extended']['PublicCarsharing']['hasPublicCarsharing']:
                yield location

    def all_vehicles(self) -> Generator[Dict, None, None]:
        for vehicle in self.api.all_vehicles():
            if vehicle['active'] and not vehicle['deleted'] and vehicle['typeOfUsage'] == 'carsharing':
                yield vehicle

    def normalize_id(self, id: str) -> str:
        """
        Normalizes the ID by restricting chars to A-Za-z_0-9. Whitespaces are converted to _.
        """
        return re.sub('[^A-Za-z_0-9]', '', id.lower().replace(' ', '_')).replace('__', '_')

    def create_station_status(self, station_id: str, last_reported: int) -> Dict[str, Any]:
        """
        Return a default station status, which needs to be updated later on.
        """
        return {
            'num_bikes_available': 0,
            'is_renting': True,
            'is_installed': True,
            'is_returning': True,
            'station_id': station_id,
            'vehicle_types_available': [],
            'last_reported': last_reported,
        }

    def pricing_plan_id(self, vehicle: Dict) -> Optional[str]:
        """
        Maps deer's vehicle categories to pricing plans (provided viaa config).
        Note: category seems not to match exactly to the pricing plans, as Tesla
        is caategorized premium, but only Porsche is listed as exclusive line product.
        """
        category = vehicle['category']
        if category in {'compact', 'midsize', 'city', 'economy', 'fullsize'}:
            return 'basic_line'
        if vehicle['brand'] in {'Porsche'}:
            return 'exclusive_line'
        if category in {'business', 'premium'}:
            return 'business_line'

        raise OSError(f'No default_pricing_plan mapping for category {category}')

    def load_stations(self, default_last_reported: int) -> Tuple[Dict, Dict]:
        """
        Retrieves stations from deer's fleetster API and converts them
        into gbfs station infos and station status.
        Note: station status does not reflect vehicle availabilty and needs
        to be updated when vehicle information was retrieved.
        """

        gbfs_station_infos_map = {}
        gbfs_station_status_map = {}

        for elem in self.all_stations():
            station_id = str(elem.get('_id'))

            geo_position = elem.get('extended', {}).get('GeoPosition', {})
            if not geo_position:
                logger.warning('Skipping {} which has no geo coordinates'.format(elem.get('name')))
                continue

            gbfs_station = {
                'lat': geo_position.get('latitude'),
                'lon': geo_position.get('longitude'),
                'name': elem.get('name'),
                'station_id': station_id,
                'addresss': elem.get('streetName'),
                'post_code': elem.get('postcode'),
                'city': elem.get('city'),  # Non-standard
                'rental_methods': ['key'],
            }

            gbfs_station_infos_map[station_id] = gbfs_station

            gbfs_station_status_map[station_id] = self.create_station_status(station_id, default_last_reported)

        return gbfs_station_infos_map, gbfs_station_status_map

    def load_vehicles(self, default_last_reported: int) -> Tuple[Dict, Dict]:
        """
        Retrieves vehicles from deer's fleetster API and converts them
        into gbfs vehicles, vehicle_types.

        TODO: booking status is not taken into account yet
        TODO: labels and accessories are not taken into account yet
        """
        gbfs_vehicles_map = {}
        gbfs_vehicle_types_map = {}

        for elem in self.all_vehicles():
            vehicle_id = str(elem['_id'])
            vehicle_type_id = self.normalize_id(elem['brand'] + '_' + elem['model'])

            gbfs_vehicle_type = {
                'vehicle_type_id': vehicle_type_id,
                'form_factor': 'car',
                'propulsion_type': elem['engine'],
                'max_range_meters': 100000,
                'name': elem['brand'] + ' ' + elem['model'],
                'return_type': 'roundtrip',
                'default_pricing_plan_id': self.pricing_plan_id(elem),
            }

            gbfs_vehicle = {
                'bike_id': vehicle_id,
                'vehicle_type_id': vehicle_type_id,
                'station_id': elem['locationId'],
                'pricing_plan_id': self.pricing_plan_id(elem),
                'is_reserved': False,  # TODO
                'is_disabled': False,  # TODO
                'current_range_meters': 0,  # TODO
            }

            gbfs_vehicles_map[vehicle_id] = gbfs_vehicle
            gbfs_vehicle_types_map[vehicle_type_id] = gbfs_vehicle_type

        return gbfs_vehicle_types_map, gbfs_vehicles_map
