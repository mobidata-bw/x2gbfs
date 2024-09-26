import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, Tuple

import xmltodict
from decouple import config

from x2gbfs.gbfs.base_provider import BaseProvider
from x2gbfs.util import timestamp_to_isoformat

from .api.ixsi import IxsiAPI

logger = logging.getLogger('x2gbfs.cantamen')


class CantamenIXSIProvider(BaseProvider):
    """
    Generic Stadtmobil provider to retrieve sharing data via IXSI an convert it to GBFS.
    It can be configured via ENV variables:
    * CANTAMEN_IXSI_API_URL (required): an IXSIv5 service endpoint url
    * CANTAMEN_IXSI_API_TIMEOUT (specified in seconds, optional, default 10)
    * CANTAMEN_IXSI_RESPONSE_MAX_SIZE (specified in bytes, optional, default 2**24)

    This Provider expects the config dict to provide the followig information:
    * provider_id: ID of the provider to be retrieved
    * url_templates: URL templates to generate rental_uris for stations and vehicles:
    ```
        "station": {
            "web": "https://<host>/#{lat}-{lon}-17-0/place/{placeId}"
        },
        "vehicle": {
            "web": "https://<host>/#{lat}-{lon}-17-0/place/{placeId}/{bookeeId}""
        }
    ```
    * feed_data: static provision of pricing_plans.json and system_information.json
    """

    # State of charge in case IXSI does not specify any (required by GBFS)
    DEFAULT_CURRENT_STATE_OF_CHARGE = 50
    # Default max range for cars, in case IXSI does not specify any (required by GBFS)
    DEFAULT_CAR_MAX_RANGE_METERS = 300000
    # Default max range for cargo_bike, in case IXSI does not specify any (required by GBFS)
    DEFAULT_CARGO_BIKE_MAX_RANGE_METERS = 30000

    # Maps lowercased IXSI attribute class names to gbfs equivalents
    ATTRIBUTE_MAPINGS = {
        'air_condition': 'air_conditioning',
        'manualgear': 'manual',
        'allseasontyres': 'winter_tires',  # map allseasontyres to winter_tyres, as allseasontyres is not supported in GBFS yet
        'winter_tyres': 'winter_tires',
        'snowchains': 'snow_chains',
        'doors2': 'doors_2',
        'doors3': 'doors_3',
        'doors4': 'doors_4',
        'doors5': 'doors_5',
        'childsafetyseat': 'child_seat_b',
        'childsafetyseat15to36': 'child_seat_c',
        # propulsion_type mappings (hybrid/electric are already GBFS conformant)
        'gasoline': 'combustion',
        'combustion_engine': 'combustion',
        'diesel': 'combustion_diesel',
        'dieselfromeuro6': 'combustion_diesel',
    }

    # attributes that map to GBFS `vehicle_accessories` entries
    ACCESSORIES_ATTRIBUTES = [
        'air_conditioning',
        'cruise_control',
        'automatic',
        'manual',
        'convertible',
        'navigation',
        'doors_2',
        'doors_3',
        'doors_4',
        'doors_5',
    ]
    # attributes that map to GBFS `vehicle_equipment` entries
    EQUIPMENT_ATTRIBUTES = ['winter_tires', 'snow_chains', 'child_seat_b', 'child_seat_c']
    # attributes that map to GBFS `propulsion_type` (naturalgas is no GBFS ppropulsion type yet)
    PROPULSION_ATTRIBUTES = ['hybrid', 'combustion', 'combustion_diesel', 'electric']

    cached_response: Optional[Dict[str, Any]] = None
    attributes: Dict[str, str] = {}
    # maps IXSI color attributes' IDs to their respective color names, e.g. "10648" (with Code COL_RED) -> "Rot"
    colors: Dict[str, str] = {}
    seats: Dict[str, int] = {}
    # Currently supported pricing plan IDs (These need to be configured in config/<provider>.json)
    pricing_plan_ids: List[str] = []

    def __init__(self, feed_config):
        self.api_url = config('CANTAMEN_IXSI_API_URL')
        self.api_timeout = int(config('CANTAMEN_IXSI_API_TIMEOUT', 10))
        self.api_response_max_size = config('CANTAMEN_IXSI_RESPONSE_MAX_SIZE', 2**24)
        self.config = feed_config
        self.pricing_plan_ids = [plan['plan_id'] for plan in feed_config['feed_data']['pricing_plans']]

    def _load_response(self) -> Dict[str, Any]:
        if not self.cached_response:
            provider_id = self.config['provider_id']
            data = IxsiAPI(
                self.config['system_id'], self.api_url, self.api_timeout, self.api_response_max_size
            ).result_for_provider(provider_id)
            base_data = xmltodict.parse(data)['Ixsi']['Response']['BaseData']
            self._parse_attributes(base_data['Attributes'])
            self.cached_response = base_data
            return base_data
        return self.cached_response

    def _parse_attributes(self, attributes):
        for attribute in attributes:
            attributeId = attribute['ID']
            lowercasedClass = attribute['Class'].lower()
            self.attributes[attributeId] = (
                lowercasedClass
                if lowercasedClass not in self.ATTRIBUTE_MAPINGS
                else self.ATTRIBUTE_MAPINGS[lowercasedClass]
            )
            if lowercasedClass.startswith('col'):
                self.colors[attributeId] = attribute['Text']['Text']
            if lowercasedClass.startswith('seats'):
                # seats are encoded differently per provider: SEATSX, seats_x
                seatsClass = lowercasedClass.replace('_', '')
                numberOfSeats_str = seatsClass[len('seats') :]
                numberOfSeats = 7 if numberOfSeats_str == '5plus2' else int(numberOfSeats_str)
                self.seats[attributeId] = numberOfSeats

    def _all_bookees(self) -> Generator[Dict[str, Any], None, None]:
        bookees = self._load_response()['Bookee']
        for bookee in bookees:
            if bookee.get('Class') is None:
                logger.info(f'Bookee {bookee["ID"]} has no Class and will be ignored')
                continue
            if bookee.get('PlaceID') is None:
                logger.info(f'Bookee {bookee["ID"]} has no PlaceID and will be ignored')
                continue
            yield bookee

    def _all_places(self) -> Generator[Dict[str, Any], None, None]:
        places = self._load_response()['Place']
        for place in places:
            yield place

    def _extract_station_info_and_state(self, place, default_last_reported) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        info = {
            'station_id': place['ID'],
            'name': place['Name']['Text'],
            'lon': float(place['GeoPosition']['Coord']['Longitude']),
            'lat': float(place['GeoPosition']['Coord']['Latitude']),
            'capacity': int(place['Capacity']),
        }
        state = {
            'station_id': place['ID'],
            'is_installed': True,
            'is_renting': True,
            'is_returning': True,
            'last_reported': default_last_reported,
        }
        return info, state

    def _color(self, attributes) -> Optional[str]:
        for attribute in attributes:
            if attribute in self.colors:
                return self.colors[attribute]
        return None

    def _seats(self, attributes: List[str]) -> Optional[int]:
        for attribute in attributes:
            if attribute in self.seats:
                return self.seats[attribute]
        return None

    def _filter_and_map_attributes(self, attributes: List[str], filter: List[str]) -> List[str]:
        filtered_attributes = []
        for attribute in attributes:
            if self.attributes.get(attribute) in filter:
                filtered_attributes.append(self.attributes[attribute])
        return filtered_attributes

    def _is_stationwagon(self, attributes: List[str]) -> bool:
        for attribute in attributes:
            if self.attributes.get(attribute) in ['stationwagon', 'stationwagonhighroof']:
                return True
        return False

    def _extract_attributes(self, place: Dict) -> List[str]:
        attributes = [place['AttributeID']] if isinstance(place.get('AttributeID'), str) else place.get('AttributeID')
        return [] if not attributes else attributes

    def _extract_propulsion_type_and_range(
        self, name: str, attributes: List[str], form_factor: str, bookee: Dict
    ) -> Tuple[str, int]:
        max_range_meters = self.DEFAULT_CAR_MAX_RANGE_METERS

        # first propulsion_type attribute ot None, if None declared for this bookee
        propulsion_type = next(iter(self._filter_and_map_attributes(attributes, self.PROPULSION_ATTRIBUTES)), None)
        is_hybrid = next(iter(self._filter_and_map_attributes(attributes, ['hybrid'])), None)

        if is_hybrid == 'hybrid':
            propulsion_type = 'hybrid'
        elif form_factor == 'cargo_bicycle':
            propulsion_type = 'electric_assist'
            max_range_meters = self.DEFAULT_CARGO_BIKE_MAX_RANGE_METERS
        elif propulsion_type == 'electric' or (
            propulsion_type is None and ('CurrentStateOfCharge' in bookee or 'km' in name)
        ):
            propulsion_type = 'electric'
            pattern = re.compile(r'.*\< ?(\d*) ?km')
            match = pattern.match(name)
            if match:
                max_range_meters = int(match.group(1)) * 1000
        elif propulsion_type is None:
            propulsion_type = 'combustion'  # if no combustion type can be derived, we assume combustion

        return propulsion_type, max_range_meters

    def _extract_pricing_plan_ids(self, bookee: Dict, attributes: List[str]) -> Tuple[str, List[str]]:
        # if this bookee is a stationwagen, pricing_plan_id `stationwagen` is returned.
        # Otherwise, the bookee's lowercased `Class`. This needs to be a supported pricing_plan_id
        vehicle_class = (
            'stationwagon'
            if self._is_stationwagon(attributes) and 'stationwagon' in self.pricing_plan_ids
            else bookee['Class'].lower()
        )
        default_pricing_plan_id = f'{vehicle_class}_hour_daytime'
        if default_pricing_plan_id not in self.pricing_plan_ids:
            raise ValueError(f'Unexpected bookee class {default_pricing_plan_id} is no pricing_plan_id')

        pricing_plan_ids = []
        for pricing_plan_id in self.pricing_plan_ids:
            if pricing_plan_id.startswith('all_') or pricing_plan_id.startswith(f'{vehicle_class}_'):
                pricing_plan_ids.append(pricing_plan_id)

        return default_pricing_plan_id, pricing_plan_ids

    def _extract_form_factor(self, bookee: Dict) -> str:
        return 'cargo_bicycle' if bookee['Class'] == 'bike' else 'car'

    def _as_vehicle_type_id(self, vehicle_name: str) -> str:
        # returns the vehicle name as lowercased string, filtered to alpha-numeric characters only.
        # (Restrictive filtering is required as consuming systems like lamassu do only support a subset
        # of characters allowed by the GBFS spec.)
        return re.sub('[^a-z0-9]+', '', vehicle_name.lower())

    def _extract_vehicle_name(self, bookee_name: str) -> str:
        # Vehicles usually have their license plate (in parentheses) appended in their name.
        # We cut this of by cutting of all text starting from the rightmost opening parenthesis.
        # A single license plate (X-XXX XXX (BÜ)) is handled explicitly here
        name = bookee_name.replace('(BÜ)', '')
        name = re.sub(r'\(\d+\)', '', name)
        name = name[0 : name.rfind('(')].strip() if name.rfind('(') > 0 else name.strip()
        # range is spelled in various ways (e.g. 'bis XXXkm', '< XXXkm', '<XXXkm'), we homogenize ot '<XXXkm'':
        return name.replace(' bis ', ' <').replace('< ', '<')

    def _extract_vehicle_type(self, bookee) -> Dict[str, Any]:
        name = self._extract_vehicle_name(bookee['Name']['Text'])
        attributes = self._extract_attributes(bookee)
        form_factor = self._extract_form_factor(bookee)
        vehicle_type_id = self._as_vehicle_type_id(name)
        propulsion_type, max_range_meters = self._extract_propulsion_type_and_range(
            name, attributes, form_factor, bookee
        )
        default_pricing_plan_id, pricing_plan_ids = self._extract_pricing_plan_ids(bookee, attributes)

        vehicle_type = {
            'vehicle_type_id': vehicle_type_id,
            'form_factor': form_factor,
            'wheel_count': 4 if form_factor == 'car' else 2,
            'return_constraint': 'roundtrip_station',
            'vehicle_accessories': self._filter_and_map_attributes(attributes, self.ACCESSORIES_ATTRIBUTES),
            'name': name,
            'make': name[0 : name.find(' ')],
            'model': name[name.find(' ') + 1 :],
            'default_pricing_plan_id': default_pricing_plan_id,
            'pricing_plan_ids': pricing_plan_ids,
            'propulsion_type': propulsion_type,
            'max_range_meters': max_range_meters,
        }

        if 'CO2Factor' in bookee:
            vehicle_type['g_CO2_km'] = int(bookee['CO2Factor'])

        color = self._color(attributes)
        if color:
            vehicle_type['color'] = color
        seats = self._seats(attributes)
        if seats:
            vehicle_type['rider_capacity'] = seats

        return vehicle_type

    def _extract_vehicle(self, bookee: Dict[str, Any], vehicle_type_id: str, max_range_meters: int) -> Dict[str, Any]:
        attributes = self._extract_attributes(bookee)

        current_charge_level = (
            int(bookee['CurrentStateOfCharge'])
            if 'CurrentStateOfCharge' in bookee
            else self.DEFAULT_CURRENT_STATE_OF_CHARGE
        )
        current_fuel_percent = current_charge_level / 100.0
        return {
            'bike_id': bookee['ID'],
            'is_reserved': False,  # No realtime information available, set to False
            'is_disabled': False,
            'station_id': bookee['PlaceID'],
            'vehicle_type_id': vehicle_type_id,
            'vehicle_equipment': self._filter_and_map_attributes(attributes, self.EQUIPMENT_ATTRIBUTES),
            'current_fuel_percent': current_fuel_percent,
            'current_range_meters': round(current_fuel_percent * max_range_meters),
        }

    def _rental_uri(self, gbfs_type: str, platform: str, bookee_or_place_id: str):
        if gbfs_type == 'vehicle':
            return self.config['url_templates']['vehicle'][platform].format(bookeeId=bookee_or_place_id)
        if gbfs_type == 'station':
            return self.config['url_templates']['station'][platform].format(placeId=bookee_or_place_id)

        raise ValueError('Unkown rental_uri gbfs_type {}'.format(gbfs_type))

    def _add_rental_uris(self, station_infos: Dict, vehicles: Dict) -> None:
        """
        Iterates over station_infos and vehicles and adds the uris
        accoring to uri templates defined in `config['url_templates']['station|vehicle']['web|android|ios']`
        """
        platforms = ['web', 'ios', 'android']
        for station in station_infos.values():
            station['rental_uris'] = {
                platform: self._rental_uri('station', platform, station['station_id']) for platform in platforms
            }

        for vehicle in vehicles.values():
            vehicle['rental_uris'] = {
                platform: self._rental_uri('vehicle', platform, vehicle['bike_id']) for platform in platforms
            }

    def load_vehicles(self, default_last_reported: int) -> Tuple[Dict, Dict]:
        vehicles = {}
        vehicle_types = {}

        for bookee in self._all_bookees():
            bookee_id = bookee.get('ID')
            try:
                name = bookee['Name']['Text']
                if 'Pool' in name:  # No make and model in name
                    logger.info(f'Bookee {bookee_id} has Pool name "{name}" and will be ignored')
                    continue
                vehicle_type = self._extract_vehicle_type(bookee)
                gbfs_vehicle = self._extract_vehicle(
                    bookee, vehicle_type['vehicle_type_id'], vehicle_type['max_range_meters']
                )
                vehicles[gbfs_vehicle['bike_id']] = gbfs_vehicle
                vehicle_types[vehicle_type['vehicle_type_id']] = vehicle_type
            except ValueError as ex:
                logger.warning(
                    f'Could not extract vehicle/vehicle_type for bookee {bookee_id} due to ValueError: {ex.args}'
                )
            except Exception:
                logger.warning(
                    f'Could not extract vehicle/vehicle_type for bookee {bookee_id} due to exception:', exc_info=True
                )

        return vehicle_types, vehicles

    def load_stations(self, default_last_reported: int) -> Tuple[Dict, Dict]:
        status = {}
        infos = {}

        for place in self._all_places():
            info, state = self._extract_station_info_and_state(place, default_last_reported)

            if info.get('lon') == 0.0 or info.get('lat') == 0.0:
                logger.info(f'Skip station {info.get("name")} ({info["station_id"]}) as it has coords (0,0)')
                continue
            status[state['station_id']] = state
            infos[info['station_id']] = info

        return infos, status

    def load_stations_and_vehicles(
        self, default_last_reported: int
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict], Optional[Dict]]:
        station_infos_map, station_status_map, vehicle_types_map, vehicles_map = super().load_stations_and_vehicles(
            default_last_reported
        )
        if station_infos_map and vehicles_map:
            self._add_rental_uris(station_infos_map, vehicles_map)

        return station_infos_map, station_status_map, vehicle_types_map, vehicles_map
