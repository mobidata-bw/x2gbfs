import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional, Tuple

from x2gbfs.gbfs.base_provider import BaseProvider

logger = logging.getLogger('x2gbfs.deer')

WATT_PER_PS = 736


class Deer(BaseProvider):
    """
    Extracts vehicle, vehicle_types, station_information, station_status from deer's Fleetser-API.

    Constants:
        COLOR_NAMES             Color names map deer's hex colors of vehicles to German color names.
                                Note: RC-3.0 does not treat vehicle_types.color as localized string,
                                so it is unclear, if they should be returned in English. Defining them
                                as hex color string in GBFS would IMHO be the most appropriate.
        MAX_RANGE_METERS        Fleetster/Deer currently do not provide a max range per vehicle via the API. Use this value as default.
        CURRENT_RANGE_METERS    Fleetster/Deer currently do not provide a current range / fuel percent per vehicle via the API. Use this value as default.

    """

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
    MAX_RANGE_METERS = 200000
    CURRENT_RANGE_METERS = 50000
    IGNORABLE_BOOKING_STATES = ['canceled', 'rejected', 'keyreturned']

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
            if booking.get('state') in self.IGNORABLE_BOOKING_STATES:
                continue

            vehicle_id = booking['vehicleId']
            if vehicle_id not in next_booking_per_vehicle:
                next_booking_per_vehicle[vehicle_id] = booking
            else:
                former_booking = next_booking_per_vehicle[vehicle_id]
                if booking['startDate'] < former_booking['startDate']:
                    next_booking_per_vehicle[vehicle_id] = booking

        return next_booking_per_vehicle

    def _normalize_brand(self, brand: str) -> str:
        """
        Normalizes the brand by stripping whitespaces at begin/end,
        and by avoiding ambiguous names.
        """

        brand_strip = brand.strip()
        brand_lower = brand_strip.lower()

        if brand_lower == 'vw' or brand_lower == 'volkswagen':
            return 'VW'
        if brand_lower == 'cupra':
            return 'Seat'

        return brand_strip

    def _normalize_model(self, model: str) -> str:
        """
        Normalizes the model by stripping whitespaces at begin/end and
        fixing some common spelling differences.
        """
        normalized_model = model.strip()

        normalized_model = re.sub(r'(?i)id\.? ?', 'ID.', normalized_model)
        normalized_model = re.sub(r'(?i)(cupra )?born', 'CUPRA Born', normalized_model)
        normalized_model = re.sub(r'(?i)(renault )?zoe', 'ZOE', normalized_model)
        normalized_model = re.sub(r'(?i)e[ -]up!?', 'e-up!', normalized_model)
        return re.sub(r'(?i)e[ -]golf', 'e-Golf', normalized_model)

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
                'address': f"{elem.get('streetName')} {elem.get('streetNumber')}",
                'post_code': elem.get('postcode'),
                '_city': elem.get('city'),  # Non-standard
                'rental_methods': ['key'],
                'is_charging_station': True,
            }

            gbfs_station_infos_map[station_id] = gbfs_station

            gbfs_station_status_map[station_id] = self._create_station_status(station_id, default_last_reported)

        return gbfs_station_infos_map, gbfs_station_status_map

    def _extract_vehicle_and_type(self, fleetster_vehicle: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """
        Extracts vehicle and vehicle_type from the given fleetster vehicle dict.

        Returns (vehicle, vehicle_type)
        """
        vehicle_id = str(fleetster_vehicle['_id'])
        normalized_brand = self._normalize_brand(fleetster_vehicle['brand'])
        normalized_model = self._normalize_model(fleetster_vehicle['model'])
        vehicle_type_id = self._normalize_id(normalized_brand + '_' + normalized_model)

        gbfs_vehicle_type = {
            'vehicle_type_id': vehicle_type_id,
            'form_factor': 'car',
            'propulsion_type': fleetster_vehicle['engine'],
            # TODO: pull this information from the Deer GBFS API as soon as available
            'max_range_meters': self.MAX_RANGE_METERS,
            'name': normalized_brand + ' ' + normalized_model,
            'make': normalized_brand,
            'model': normalized_model,
            'wheel_count': 4,
            'return_type': 'roundtrip',
            'default_pricing_plan_id': self.pricing_plan_id(fleetster_vehicle),
        }

        extended_properties = fleetster_vehicle.get('extended', {}).get('Properties', {})

        accessories = []
        if 'doors' in extended_properties and isinstance(extended_properties['doors'], int):
            doors = extended_properties['doors']
            accessories.append(f'doors_{doors}')
        if 'aircondition' in extended_properties and extended_properties['aircondition'] is True:
            accessories.append('air_conditioning')
        if 'navigation' in extended_properties and extended_properties['navigation'] is True:
            accessories.append('navigation')
        if len(accessories) > 0:
            gbfs_vehicle_type['vehicle_accessories'] = accessories

        if 'horsepower' in extended_properties and isinstance(extended_properties['horsepower'], int):
            gbfs_vehicle_type['rated_power'] = extended_properties['horsepower'] * WATT_PER_PS
        if 'vMax' in extended_properties and isinstance(extended_properties['vMax'], int):
            gbfs_vehicle_type['max_permitted_speed'] = extended_properties['vMax']
        if 'seats' in extended_properties and isinstance(extended_properties['seats'], int):
            gbfs_vehicle_type['rider_capacity'] = extended_properties['seats']
        if 'color' in extended_properties:
            color_hex = extended_properties['color']
            if color_hex in self.COLOR_NAMES:
                gbfs_vehicle_type['color'] = self.COLOR_NAMES[color_hex]
            else:
                logger.warning(f'No color hex-to-name mapping for color {color_hex}')

        gbfs_vehicle = {
            'bike_id': vehicle_id,
            'vehicle_type_id': vehicle_type_id,
            'station_id': fleetster_vehicle['locationId'],
            'pricing_plan_id': self.pricing_plan_id(fleetster_vehicle),
            'is_reserved': False,  # Will possibly be updated later by self._update_booking_state
            'is_disabled': False,
            # TODO: pull this information from the Deer GBFS API as soon as available
            'current_range_meters': self.CURRENT_RANGE_METERS,
        }

        if 'winterTires' in extended_properties and extended_properties['winterTires']:
            gbfs_vehicle['vehicle_equipment'] = ['winter_tires']

        return gbfs_vehicle, gbfs_vehicle_type

    def load_vehicles(self, default_last_reported: int) -> Tuple[Dict, Dict]:
        """
        Retrieves vehicles from deer's fleetster API and converts them
        into gbfs vehicles, vehicle_types.
        """
        gbfs_vehicles_map = {}
        gbfs_vehicle_types_map = {}

        for elem in self.all_vehicles():
            (gbfs_vehicle, gbfs_vehicle_type) = self._extract_vehicle_and_type(elem)

            gbfs_vehicles_map[gbfs_vehicle['bike_id']] = gbfs_vehicle
            gbfs_vehicle_types_map[gbfs_vehicle_type['vehicle_type_id']] = gbfs_vehicle_type

        gbfs_vehicles_map = self._update_booking_state(gbfs_vehicles_map)

        return gbfs_vehicle_types_map, gbfs_vehicles_map

    def _utcnow(self):
        return datetime.now(timezone.utc)

    def _timestamp_to_isoformat(self, timestamp):
        """
        Returns timestamp in isoformat.
        As gbfs-validator currently can't handle numeric +00:00 timezone information, we replace +00:00 by Z
        It's validation expressio is ^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})([A-Z])$
        See also https://github.com/MobilityData/gbfs-json-schema/issues/95
        """
        return timestamp.isoformat().replace('+00:00', 'Z')

    def _datetime_from_isoformat(self, isoformatted_datetime: str) -> datetime:
        """
        Fleetster API returns datetimes with Z timezone, which can't be handled by python <= 3.10.
        """
        # In Python >= v3.11, fromisoformat supports Z timezone, for now, we need to work around
        # datetime.fromisoformat(reformatted_datetime)
        return datetime.strptime(isoformatted_datetime, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)

    def _update_booking_state(self, gbfs_vehicles_map: Dict) -> Dict:
        """
        For every vehicle in gbfs_vehicles_map, this function
        sets is_reserved to true, if there is an active, ongoing booking (startDate < now < endDate),
        or, if not, available_until to the startDate of the earliest booking in the future.
        If no booking for a vehicle id exists, is_reserved is false and no available_until
        information. A booking is considered active, if it's not in any of the following states:
        canceled, rejected, keyreturned.
        """
        timestamp = self._utcnow()

        next_bookings = self._next_booking_per_vehicle(timestamp)
        for vehicle_id, vehicle in gbfs_vehicles_map.items():
            if vehicle_id not in next_bookings:
                # No booking => available forever and not reserved
                continue
            next_booking_start = self._datetime_from_isoformat(next_bookings[vehicle_id]['startDate'])
            if next_booking_start > timestamp:
                # Next booking starts in the future, set available_until, currently not reserved
                gbfs_formatted_start_time = self._timestamp_to_isoformat(next_booking_start)

                vehicle['available_until'] = gbfs_formatted_start_time
            else:
                vehicle['is_reserved'] = True

        return gbfs_vehicles_map
