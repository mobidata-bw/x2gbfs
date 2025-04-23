import json
import logging
import re
from datetime import datetime, timezone
from random import random
from time import sleep
from typing import Any, Dict, Generator, Optional, Tuple

import requests

from x2gbfs.gbfs.base_provider import BaseProvider

logger = logging.getLogger(__name__)

WATT_PER_PS = 736


class FleetsterAPI:
    """
    Returns locations and vehicles from fleetster endppoint.

    fleetster-API-Documentation is available here:
    https://my.fleetster.net/swagger/
    """

    #: Number of times a login is attempted before an error is thrown on 401 response
    MAX_LOGIN_ATTEMPTS = 5

    token: Optional[str] = None
    api_url: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

    def __init__(self, api_url: str, user: str, password: str) -> None:
        self.api_url = api_url
        self.user = user
        self.password = password

    def all_stations(self) -> Generator[Dict, None, None]:
        locations = self._get_with_authorization(f'{self.api_url}/locations')
        for location in locations:
            yield location

    def all_vehicles(self) -> Generator[Dict, None, None]:
        vehicles = self._get_with_authorization(f'{self.api_url}/vehicles')
        for vehicle in vehicles:
            yield vehicle

    def all_bookings_ending_after(self, utctimestamp: datetime):
        enddate = self._timestamp_to_isoformat(utctimestamp)
        return self._get_with_authorization(f'{self.api_url}/bookings?endDate%5B%24gte%5D={enddate}')

    def _timestamp_to_isoformat(self, utctimestamp: datetime):
        """
        Returns timestamp in isoformat.
        As fleetster currently can't handle numeric timezone information, we replace +00:00 by Z
        """
        return utctimestamp.isoformat().replace('+00:00', 'Z')

    def _login(self) -> str:
        if self.token is None:
            endpoint = f'{self.api_url}/users/auth'
            body = {'email': self.user, 'password': self.password}
            response = requests.post(endpoint, json=body, timeout=10)
            response.raise_for_status()

            self.token = response.json()['_id']

        return self.token

    def _get_with_authorization(self, url: str) -> Dict:
        """
        Gets the provided url and returns the response as (json) dict.

        The request is performed with an authentication token, aquired before the request.
        In case the API responds with an 401 response, a new login is attempted
        self.MAX_LOGIN_ATTEMPTS times.
        """

        no_of_login_attempts = 0
        while not no_of_login_attempts >= self.MAX_LOGIN_ATTEMPTS:
            no_of_login_attempts += 1
            token = self._login()
            response = requests.get(url, headers={'Authorization': token}, timeout=10)
            if response.status_code == 401:
                # Authentication issues will cause a retry attempt.
                # An authentication issue could be caused by a competing client requesting
                # a session token with the same credentials, invalidating our token

                # Give potentially competing clients some time to complete their requests
                # exponential back-offs plus some randomised "jitter" to prevent the https://en.wikipedia.org/wiki/Thundering_herd_problem
                seconds_to_sleep = (
                    0.5 * (1 + random() / 10) * no_of_login_attempts**2  # noqa: S311 (no cryptographic purpose)
                )
                logger.warning(
                    f'Requested token {self.token} was invalid, waiting for {seconds_to_sleep} seconds before retry'
                )
                sleep(seconds_to_sleep)

                # Reset authentication token, so it will be requested again
                self.token = None

            else:
                break

        response.raise_for_status()
        return response.json()


class FleetsterProvider(BaseProvider):
    """
    Extracts vehicle, vehicle_types, station_information, station_status from Fleetser-API.

    Constants:
        COLOR_NAMES              Color names map hex colors of vehicles to German color names.
                                 Note: RC-3.0 does not treat vehicle_types.color as localized string,
                                 so it is unclear, if they should be returned in English. Defining them
                                 as hex color string in GBFS would IMHO be the most appropriate.
        MAX_RANGE_METERS         Fleetster currently do not provide a max range per vehicle via the API. Use this value as default.
        CURRENT_RANGE_METERS     Fleetster currently do not provide a current range / fuel percent per vehicle via the API. Use this value as default.
        IGNORABLE_BOOKING_STATES These bookings states are ignored when evaluating existing bookings which reduce availabilty of vehicles.
        ENGINE_PROPULSION_TYPE_MAPPING              Maps vehicle engine value to propulsion_type
        CATEGORY_TO_PRICING_PLAN_CATEGORY_MAPPING   Maps vehicle categories (like city, compact etc) to pricing_plan categories.
                                                    All pricing_plans defined in feed_config, whose plan_id contains the
                                                    pricing_plan categoriy as substring are assigned to this vehicle as pricing plan.

    """

    COLOR_NAMES = {
        '#ffffff': 'weiß',
        '#b50d17': 'rot',
        '#b3020c': 'rot',
        '#000000': 'schwarz',
        '#f6f6f6': 'hellgrau',
        '#929292': 'mittelgrau',
        '#474747': 'dunkelgrau',
        '#6b6a6a': 'gedimmtes grau',
        '#bebbbb': 'silber',
        '#242424': 'dunkelgrau',
        '#4693b6': 'blau',
        '#025f8a': 'blau',
        '#4ba003': 'dunkelgrün',
        '#367303': 'dunkelgrün',
    }
    MAX_RANGE_METERS = 200000
    CURRENT_RANGE_METERS = 50000
    IGNORABLE_BOOKING_STATES = ['canceled', 'rejected', 'keyreturned']

    ENGINE_PROPULSION_TYPE_MAPPING = {
        'electric': 'electric',
        'diesel': 'combustion_diesel',
        'petrol': 'combustion',
    }

    # Default return constraint for vehicles
    DEFAULT_VEHICLE_RETURN_CONSTRAINT = 'roundtrip_station'

    # Vehicle category to pricing_plan category mapping.
    # Subclasses should redefine as needed.
    CATEGORY_TO_PRICING_PLAN_CATEGORY_MAPPING: dict[str, str] = {}

    def __init__(self, feed_config: dict[str, Any], api):
        self.config = feed_config
        self.api = api
        self.stationIdCache: set[str] = set()
        self.system_id = feed_config['feed_data']['system_information']['system_id']

    def all_stations(self) -> Generator[Dict, None, None]:
        """
        Returns all stations, which are
        * not deleted
        * declare extended.PublicCarsharing.hasPublicCarsharing == true
        """
        for location in self.api.all_stations():
            if not location.get('deleted', False) and location.get('extended', {}).get('PublicCarsharing', {}).get(
                'hasPublicCarsharing', False
            ):
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

    def _map_category_to_pricing_plan_category(self, category: str) -> str:
        return self.CATEGORY_TO_PRICING_PLAN_CATEGORY_MAPPING.get(category, category)

    def _pricing_plans_for_category(self, category: str) -> list[str]:
        return [
            pricing_plan['plan_id'] for pricing_plan in self.load_pricing_plans() if category in pricing_plan['plan_id']
        ]

    def _default_pricing_plan_id(self, vehicle: dict) -> str:
        """
        Maps fleetster's vehicle categories to pricing plans (provided via config).
        """
        category = self._map_category_to_pricing_plan_category(vehicle['category'])
        pricing_plan_id = f'{category}_hour'
        if pricing_plan_id in self._pricing_plans_for_category(category):
            return pricing_plan_id

        raise OSError(f'No default_pricing_plan mapping for category {category} ({self.system_id})')

    def _pricing_plan_ids(self, vehicle: dict) -> list[str]:
        category = self._map_category_to_pricing_plan_category(vehicle['category'])
        existing_pricing_plan_ids = self._pricing_plans_for_category(category)
        if len(existing_pricing_plan_ids) > 0:
            return existing_pricing_plan_ids

        raise OSError(f'No default_pricing_plan mapping for category {category} ({self.system_id})')

    def load_stations(self, default_last_reported: int) -> Tuple[Dict, Dict]:
        """
        Retrieves stations from fleetster API and converts them
        into gbfs station infos and station status.
        Note: station status does not reflect vehicle availabilty and needs
        to be updated when vehicle information was retrieved.
        """

        gbfs_station_infos_map = {}
        gbfs_station_status_map = {}

        for elem in self.all_stations():
            station_id = str(elem.get('_id'))

            geo_position = elem.get('extended', {}).get('GeoPosition', {})
            if (
                not geo_position
                or not isinstance(geo_position.get('latitude'), float)
                or not isinstance(geo_position.get('longitude'), float)
            ):
                logger.warning('Skipping {} ({}) which has no geo coordinates'.format(elem.get('name'), self.system_id))
                continue

            gbfs_station = {
                'lat': geo_position.get('latitude'),
                'lon': geo_position.get('longitude'),
                'name': elem.get('name'),
                'station_id': station_id,
                'address': f"{elem.get('streetName')} {elem.get('streetNumber')}",
                'post_code': elem.get('postcode'),
                'city': elem.get('city'),  # Non-standard
                'rental_methods': ['key'],
                'is_charging_station': True,  # TODO for deer, True was ok, for others, we can't assume this
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
            'propulsion_type': self.ENGINE_PROPULSION_TYPE_MAPPING[fleetster_vehicle['engine']],
            # TODO: pull this information from the Fleetster GBFS API as soon as available
            'max_range_meters': self.MAX_RANGE_METERS,
            'name': normalized_brand + ' ' + normalized_model,
            'make': normalized_brand,
            'model': normalized_model,
            'wheel_count': 4,
            'return_constraint': self.DEFAULT_VEHICLE_RETURN_CONSTRAINT,
            'default_pricing_plan_id': self._default_pricing_plan_id(fleetster_vehicle),
            'pricing_plan_ids': self._pricing_plan_ids(fleetster_vehicle),
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
        transmission = fleetster_vehicle.get('transmission')
        if transmission in ['automatic', 'manuel']:
            accessories.append(transmission)
        if len(accessories) > 0:
            gbfs_vehicle_type['vehicle_accessories'] = accessories

        if 'horsepower' in extended_properties and isinstance(extended_properties['horsepower'], int):
            gbfs_vehicle_type['rated_power'] = extended_properties['horsepower'] * WATT_PER_PS
        if 'vMax' in extended_properties and isinstance(extended_properties['vMax'], int):
            gbfs_vehicle_type['max_permitted_speed'] = extended_properties['vMax']
        if 'seats' in extended_properties and isinstance(extended_properties['seats'], int):
            gbfs_vehicle_type['rider_capacity'] = extended_properties['seats']
        if 'color' in extended_properties and isinstance(extended_properties['color'], str):
            color_hex = extended_properties['color'].lower()
            if color_hex in self.COLOR_NAMES:
                gbfs_vehicle_type['color'] = self.COLOR_NAMES[color_hex]
            elif color_hex is not None:  # ignore "color": null
                logger.warning(f'No color hex-to-name mapping for color {color_hex} ({self.system_id})')

        gbfs_vehicle = {
            'bike_id': vehicle_id,
            'vehicle_type_id': vehicle_type_id,
            'station_id': fleetster_vehicle['locationId'],
            'pricing_plan_id': self._default_pricing_plan_id(fleetster_vehicle),
            'is_reserved': False,  # Will possibly be updated later by self._update_booking_state
            'is_disabled': False,
            # TODO: pull this information from the Fleetster GBFS API as soon as available
            'current_range_meters': self.CURRENT_RANGE_METERS,
        }

        if 'winterTires' in extended_properties and extended_properties['winterTires']:
            gbfs_vehicle['vehicle_equipment'] = ['winter_tires']

        return gbfs_vehicle, gbfs_vehicle_type

    def load_vehicles(self, default_last_reported: int) -> Tuple[Dict, Dict]:
        """
        Retrieves vehicles from fleetster API and converts them
        into gbfs vehicles, vehicle_types.
        """
        gbfs_vehicles_map = {}
        gbfs_vehicle_types_map = {}

        for elem in self.all_vehicles():
            try:
                vehicle_id = str(elem.get('_id'))
                (gbfs_vehicle, gbfs_vehicle_type) = self._extract_vehicle_and_type(elem)

                gbfs_vehicles_map[gbfs_vehicle['bike_id']] = gbfs_vehicle
                gbfs_vehicle_types_map[gbfs_vehicle_type['vehicle_type_id']] = gbfs_vehicle_type
            except Exception:
                logger.warning(
                    f'Could not extract vehicle/vehicle_type for vehicle {vehicle_id} ({self.system_id}) due to exception:',
                    exc_info=True,
                )

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
