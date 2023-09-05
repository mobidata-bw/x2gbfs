import logging
import re
from datetime import datetime
from typing import Any, Dict, Generator, Optional, Tuple

from x2gbfs.gbfs.base_provider import BaseProvider

logger = logging.getLogger('x2gbfs.deer')

WATT_PER_PS = 736

class Deer(BaseProvider):

    COLOR_NAMES = {
        '#ffffff': 'weiß',
        '#b50d17': 'rot',
        '#000000': 'schwarz',
        '#f6f6f6': 'hellgrau',
        '#929292': 'mittelgrau',
        '#474747': 'dunkelgrau',
        '#6b6a6a': 'gedimmtes grau',
        '#bebbbb': 'silber',
        '#242424': 'dunkelgrau',
    }

    def __init__(self, api):
        self.api = api
        self.stationIdCache = set()

    def all_stations(self) -> Generator[Dict, None, None]:
        """
        Returns all stations, which are
        * not deleted
        * declare extended.PublicCarsharing.hasPublicCarsharing == true
        """
        for location in self.api.all_stations():
            if not location['deleted'] and location['extended']['PublicCarsharing']['hasPublicCarsharing']:
                self.stationIdCache.add(location['_id'])
                yield location

    def all_vehicles(self) -> Generator[Dict, None, None]:
        """
        Returns all vehicles, which are
        * not deleted
        * have typeOfUsage == carsharing
        * have a locationId which is a valid carsharing station

        Note: all_stations needs to be iterated before all_vehicles so station ids are cached.
        """
        for vehicle in self.api.all_vehicles():
            if (
                vehicle['active']
                and not vehicle['deleted']
                and vehicle['typeOfUsage'] == 'carsharing'
                and vehicle.get('locationId') in self.stationIdCache
            ):
                yield vehicle

    def _next_booking_per_vehicle(self, timestamp: datetime) -> Dict[str, Dict[str, str]]:
        """
        Returns a map which for each vehicle contains the currently ongoing
        or the next upcoming fleetster booking.
        """
        bookings = self.api.all_bookings_ending_after(timestamp)
        next_booking_per_vehicle = {}
        for booking in bookings:
            vehicle_id = booking['vehicleId']
            if vehicle_id not in next_booking_per_vehicle:
                next_booking_per_vehicle[vehicle_id] = booking
            else:
                former_booking = next_booking_per_vehicle[vehicle_id]
                if booking['startDate'] < former_booking['startDate']:
                    next_booking_per_vehicle[vehicle_id] = booking

        return next_booking_per_vehicle

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
                'address': elem.get('streetName') + ' ' + elem.get('streetNumber'),
                'post_code': elem.get('postcode'),
                '_city': elem.get('city'),  # Non-standard
                'rental_methods': ['key'],
                'is_charging_station': True,
            }

            gbfs_station_infos_map[station_id] = gbfs_station

            gbfs_station_status_map[station_id] = self.create_station_status(station_id, default_last_reported)

        return gbfs_station_infos_map, gbfs_station_status_map

    def load_vehicles(self, default_last_reported: int) -> Tuple[Dict, Dict]:
        """
        Retrieves vehicles from deer's fleetster API and converts them
        into gbfs vehicles, vehicle_types.

        TODO: booking status is not taken into account yet
        TODO: labels are not taken into account yet
        """
        gbfs_vehicles_map = {}
        gbfs_vehicle_types_map = {}

        for elem in self.all_vehicles():
            vehicle_id = str(elem['_id'])
            vehicle_type_id = self.normalize_id(elem['brand'] + '_' + elem['model'])

            extended_properties = elem['extended']['Properties']
            accessories = []
            if 'doors' in extended_properties and isinstance(extended_properties['doors'], int):
                doors = extended_properties['doors']
                accessories.append(f'doors_{doors}')
            if 'aircondition' in extended_properties and extended_properties['aircondition'] == True:
                accessories.append('air_conditioning')
            if 'navigation' in extended_properties and extended_properties['navigation'] == True:
                accessories.append('navigation')

            gbfs_vehicle_type = {
                'vehicle_type_id': vehicle_type_id,
                'form_factor': 'car',
                'propulsion_type': elem['engine'],
                'max_range_meters': 100000,
                'name': elem['brand'] + ' ' + elem['model'],
                'make': elem['brand'],
                'model': elem['model'],
                'wheel_count': 4,
                'return_type': 'roundtrip',
                'default_pricing_plan_id': self.pricing_plan_id(elem),
                'vehicle_accessories': accessories,
            }

            if 'horsepower' in extended_properties and isinstance(extended_properties['horsepower'], int):
                gbfs_vehicle_type['rated_power'] = extended_properties['horsepower'] * WATT_PER_PS
            if 'vMax' in extended_properties and isinstance(extended_properties['vMax'], int):
                gbfs_vehicle_type['max_permitted_speed'] = extended_properties['vMax']
            if 'seats' in extended_properties and isinstance(extended_properties['seats'], int):
                gbfs_vehicle_type['rider_capacity'] = extended_properties['seats']
            if 'color' in extended_properties:
                color_hex = extended_properties['color']
                if color_hex in self.COLOR_NAMES:
                    gbfs_vehicle_type['color'] =  self.COLOR_NAMES[color_hex]
                else:
                    logger.warning(f'No color hex-to-name mapping for color {color_hex}')
            
            gbfs_vehicle = {
                'bike_id': vehicle_id,
                'vehicle_type_id': vehicle_type_id,
                'station_id': elem['locationId'],
                'pricing_plan_id': self.pricing_plan_id(elem),
                'is_reserved': False,  # TODO
                'is_disabled': False,  # TODO
                'current_range_meters': 0,  # TODO
            }

            if 'winterTires' in extended_properties and extended_properties['winterTires']:
                gbfs_vehicle['vehicle_equipment'] = ['winter_tires']

            gbfs_vehicles_map[vehicle_id] = gbfs_vehicle
            gbfs_vehicle_types_map[vehicle_type_id] = gbfs_vehicle_type

        gbfs_vehicles_map = self._update_booking_state(gbfs_vehicles_map)

        return gbfs_vehicle_types_map, gbfs_vehicles_map

    def _update_booking_state(self, gbfs_vehicles_map: Dict) -> Dict:
        """
        For every vehicle in gbfs_vehicles_map, this function
        sets is_reserved to true, if there is an ongoing booking (startDate < now < endDate),
        or, if not, available_until to the startDate of the earliest booking in the future.
        If no booking for a vehicle id exists, is_reserved is false and no available_until
        information.
        """
        timestamp = datetime.now()
        timestamp_iso = timestamp.isoformat()

        next_bookings = self._next_booking_per_vehicle(timestamp)
        for vehicle_id, vehicle in gbfs_vehicles_map.items():
            if vehicle_id not in next_bookings:
                # No booking => available forever and not reserved
                continue
            next_booking_start = next_bookings[vehicle_id]['startDate']
            if next_booking_start > timestamp_iso:
                # Next booking starts in the future, set available_until, currently not reserved
                # Note: fleetsters timestamp has ms information which would be flagged by GBFS validator, so we parse and reformat in isoformat
                gbfs_formatted_start_time = (
                    datetime.fromisoformat(next_booking_start).isoformat().replace('+00:00', 'Z')
                )
                vehicle['available_until'] = gbfs_formatted_start_time
            else:
                vehicle['is_reserved'] = True

        return gbfs_vehicles_map
