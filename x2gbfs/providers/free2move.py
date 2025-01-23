import base64
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Generator, Optional, Tuple
from urllib.error import HTTPError

from decouple import config

from x2gbfs.gbfs.base_provider import BaseProvider
from x2gbfs.util import get, post, reverse_multipolygon

logger = logging.getLogger(__name__)


class Free2moveAPI:
    # After REFRESH_AFTER_SECONDS, a full updates of vehicles is performed
    REFRESH_AFTER_SECONDS = 3600

    # URL to generate tokens
    TOKEN_GENERATION_URL = '{base_url}/api/rental/externalapi/login'  # noqa: S105 (this is no secret)
    # URL to retrieve vehicle information. Note: Access to this URL requires login and is rate limited.
    # (1/min per default, 1/s if only delta is requested (via additional globalVersion parameter))
    VEHICLES_URL_TEMPLATE = '{base_url}/api/rental/externalapi/v1/vehicles/{location_alias}'
    # URL to retrieve operation area.
    OPERATING_AREA_URL_TEMPLATE = '{base_url}/api/geo/geodata/v1/locations/{location_alias}/operating_area'
    # URL to retrieve parking spots
    PARKING_SPOT_URL_TEMPLATE = '{base_url}/api/geo/geodata/v1/locations/{location_alias}/parking_spots'
    # URL to retrieve charging stations
    CHARGING_POINT_URL_TEMPLATE = '{base_url}/api/geo/geodata/v1/locations/{location_alias}/charging_stations'

    def __init__(self):
        self.base_url = (
            config('FREE2MOVE_BASE_URL')[:-1]
            if config('FREE2MOVE_BASE_URL').endswith('/')
            else config('FREE2MOVE_BASE_URL')
        )
        self.user = config('FREE2MOVE_USER')
        self.password = config('FREE2MOVE_PASSWORD')
        self.token = None
        self.cachedir = Path(config('CACHE_DIR'))
        self.cachedir.mkdir(parents=True, exist_ok=True)

    def _login(self) -> None:
        """
        Submits a login request and stores the retrieved token
        """
        login_response = post(
            self.TOKEN_GENERATION_URL.format(base_url=self.base_url),
            json={'username': self.user, 'password': self.password},
            timeout=10,
        )
        self.token = login_response.json().get('token')

    def _get_with_authorization(self, url: str, params: Optional[dict] = None) -> dict:
        """
        Gets the data from the provider Platform using the provider's credentials,
        and returns the response as (json) dict.

        The request is performed with the API credentials of the provider.
        """
        if not self.token:
            self._login()

        headers = {'Authorization': f'Bearer {self.token}'}
        try:
            response = get(url, headers=headers, params=params, timeout=10)
            return response.json()
        except HTTPError as err:
            if err.code == 401:
                # Unauthorized, e.g. due to token expiry, we try to login again
                self._login()
                response = get(url, headers=headers, params=params, timeout=10)
                return response.json()
            raise

    def _fresher_than_seconds(self, path, seconds):
        """
        Return true, if file's last modfied timestamp is fresher than `seconds` before now.
        """
        return time.time() - os.path.getmtime(path) < seconds

    def operating_area(self, location_alias) -> dict:
        # Retrieves the operation area, a single geojson feature.
        return get(
            self.OPERATING_AREA_URL_TEMPLATE.format(base_url=self.base_url, location_alias=location_alias)
        ).json()

    def parking_spots(self, location_alias) -> Generator[dict, None, None]:
        feature_collection = get(
            self.PARKING_SPOT_URL_TEMPLATE.format(base_url=self.base_url, location_alias=location_alias)
        ).json()
        for feature in feature_collection.get('features', {}):
            yield feature

    def charging_stations(self, location_alias) -> Generator[dict, None, None]:
        feature_collection = get(
            self.CHARGING_POINT_URL_TEMPLATE.format(base_url=self.base_url, location_alias=location_alias)
        ).json()
        for feature in feature_collection.get('features', {}):
            yield feature

    def all_vehicles(self, location_alias) -> Generator[dict, None, None]:
        """
        Requests all vehicles and returns a Generator to iterate over.
        """
        cachedir_for_location = self.cachedir / f'free2move_{location_alias}'
        if not cachedir_for_location.is_dir():
            cachedir_for_location.mkdir(parents=True, exist_ok=True)

        # if cached_file exists and newer than, load delta and merge
        vehicles_base_file_path = cachedir_for_location / f'vehicles_{location_alias}_base.json'
        vehicles_latest_file_path = cachedir_for_location / f'vehicles_{location_alias}_latest.json'

        refresh_base_file = False
        if (
            vehicles_base_file_path.is_file()
            and self._fresher_than_seconds(vehicles_base_file_path, self.REFRESH_AFTER_SECONDS)
            and vehicles_latest_file_path.is_file()
        ):
            with open(vehicles_latest_file_path, 'r') as f:
                cached_vehicles_response = json.load(f)
                maxGlobalVersion = cached_vehicles_response['maxGlobalVersion']
                parameters = {'globalVersion': maxGlobalVersion}
        else:
            cached_vehicles_response = {}
            parameters = None
            refresh_base_file = True

        vehicles_response = self._get_with_authorization(
            self.VEHICLES_URL_TEMPLATE.format(base_url=self.base_url, location_alias=location_alias), params=parameters
        )
        vehicles_delta_file_path = cachedir_for_location / f'vehicles_{location_alias}_delta.json'
        vehicles_delta_file_path.write_text(json.dumps(vehicles_response))
        if refresh_base_file:
            vehicles_base_file_path.write_text(json.dumps(vehicles_response))

        merged_vehicles_response = self._merge_vehicles_response(cached_vehicles_response, vehicles_response)
        vehicles_latest_file_path.write_text(json.dumps(merged_vehicles_response))

        vehicles = merged_vehicles_response['vehicles']
        for vehicle in vehicles:
            yield vehicle

    def _merge_vehicles_response(self, cached_response: dict, delta_response: dict) -> dict:
        """
        Merge cached responses with delta responses. Merge is performed on VIN (vehicle ID number):
        If delta information is available for a vehicle, it is used, otherwise the cached information.
        Note: that way, vehicles which are no longer available and not contained in delta updates
        might never receive an update. As consequence a full update should be performed every N hours...
        """
        # We build dicts with VINs as key to merge on them
        cached_vehicles_map = {v['vin']: v for v in cached_response.get('vehicles', {})}
        delta_vehicles_map = {v['vin']: v for v in delta_response.get('vehicles', {})}
        merged_vehicles_map = cached_vehicles_map | delta_vehicles_map
        # As meta information, we use the delta response' values
        return {
            'maxGlobalVersion': delta_response['maxGlobalVersion'],
            'locationId': delta_response['locationId'],
            'locationName': delta_response['locationName'],
            'vehicles': list(merged_vehicles_map.values()),
        }


class Free2moveProvider(BaseProvider):
    """
    This is an implementation of free-floating Free2move carsharing data retrieved from
    Free2move's API endpoints.

    As it is not station based, only vehicles and their types are extracted
    from the base system.

    System information and pricing information are read from config/free2move_*.json's.

    Note: to be able to run this via x2gbfs, this Free2move class needs to be added
    to x2gbfs.py's build_extractor method.

    Note: The originating API currently publishes persistant vehicle IDs / liccense plate
      information, which is generated into the GBFS' free_bike_status as bike_id and used
      in the rental_uri. As consequence, this feed does not comply with GBFS GDPR recommendation
      to rotate vehicle_ids after rental of free floating vehicles and should not be
      published openly. Users of the generated GBFS should be made aware of this issue
      and take precautions, so third parties can't acess these ids. For further details,
      see https://github.com/MobilityData/gbfs/issues/346
    """

    # Templates for rental URIs. Note: not GDPR compliant, as they leak the vehicle id.
    RENTAL_URI_TEMPLATES = {
        'android': 'https://www.share-now.com/vehicle/{VIN}?location={locationId}',
        'ios': 'share-now://vehicle/{VIN}?location={locationId}',
    }

    # Assumed max range of vehicles with combustion engine, as API does not provide it
    DEFAULT_COMBUSTION_MAX_RANGE_METERS = 400000

    # Assumed max range of vehicles with electric engine, as API does not provide it
    DEFAULT_ELECTRIC_MAX_RANGE_METERS = 200000

    # Free2move fueltypes to GBFS mapping
    FUELTYPE_TO_PROPULSION_MAPPING = {
        'ELECTRIC': 'electric',
        'SUPER_95': 'combustion',
        'GASOLINE': 'combustion',
        'DIESEL': 'combustion_diesel',
    }

    # vehicle_id to pricing_plan mapping.
    # See config for pricing_plans.
    # Note: these are deduced from https://www.free2move.com/de/de/car-sharing/stuttgart/
    # and may change from time to time and should be regularly checked.
    BUILD_SERIES_PRICING_PLAN_MAPPING = {
        'FIAT_500_BEV': 'mini',
        'OPEL_ASTRA': 'standard',
        'OPEL_CORSA': 'standard',
        'OPEL_CROSSLAND': 'standard',
    }

    # Mappings of buildSeries values to brand / model.
    # Note: the values are extracted from API documentation and
    # may require updates.
    BUILD_SERIES_TO_MAKE_MODEL_MAPPING = {
        'A453': ['smart', 'smart'],
        'A4539': ['smart', 'fortwo cabrio electric'],
        'C453': ['smart', 'fortwo'],
        'C4539': ['smart', 'fortwo electric'],
        'H243': ['Mercedes-Benz', 'Mercedes-Benz'],
        'W177': ['Mercedes-Benz', 'A 180'],
        'bmw_1er_f40': ['BMW', '118i 5-Türer'],
        'bmw_2er_active_tourer': ['BMW', 'BMW Active Tourer'],
        'bmw_2er_cabrio': ['BMW', 'BMW Convertible'],
        'bmw_i3': ['BMW', 'i3'],
        'bmw_x1': ['BMW', 'X1'],
        'bmw_x2': ['BMW', 'X2'],
        'mini_bev': ['MINI', 'Cooper SE'],
        'mini_3-tuerer': ['MINI', '3-Door'],
        'mini_5-tuerer': ['MINI', '5-Door'],
        'mini_cabrio': ['MINI', 'Convertible'],
        'mini_clubman': ['MINI', 'Clubman'],
        'mini_countryman': ['MINI', 'Countryman'],
        'FIAT_500': ['Fiat', '500'],
        'FIAT_500_BEV': ['Fiat', '500e'],
        'FIAT_500_X': ['Fiat', '500X'],
        'CITROEN_C3': ['Citroen', 'C3'],
        'JEEP_RENEGADE_HYBRID': ['JEEP', ''],
        'PEUGEOT_208': ['Peugeot', '208'],
        'PEUGEOT_208_EV': ['Peugeot', '208 EV'],
        'PEUGEOT_2008': ['Peugeot', '2008'],
        'PEUGEOT_308': ['Peugeot', '308'],
        'PEUGEOT_3008': ['Peugeot', '3008'],
        'RENAULT_ZOE': ['Renault', 'ZOE'],
        'OPEL_ASTRA': ['Opel', 'Astra'],
        'OPEL_CORSA': ['Opel', 'Corsa'],
        'OPEL_CROSSLAND': ['Opel', 'Crossland'],
    }

    COLOR_MAPPING = {
        # colors listed in documentation
        'EN3': 'weiß',
        '650': 'weiß',
        'EAZ': 'weiß',
        'EN2': 'silber',
        'EB2': 'silber',
        '761': 'silber',
        'EDA': 'silber',
        'EAD': 'silber',
        '191': 'schwarz',
        '696': 'schwarz',
        '787': 'grau',
        # colors currently used in Stuttgart
        '268U': 'weiß',
        'P0WP': 'weiß',
        '601U': 'schwarz',
        '205U': 'grau',  # mineralgrey
        'M0V9': 'schwarz',  # carbon black
        '278U': 'blau',  # celestialblue,
        '230U': 'grün',  # oceangreen
        '237U': 'rose gold',
    }

    def __init__(self, feed_config: dict, api: Free2moveAPI):
        self.config = feed_config
        self.location_alias = feed_config['provider_data']['location_alias']
        self.location_id = feed_config['provider_data']['location_id']
        self.api = api

    def load_vehicles(self, default_last_reported: int) -> Tuple[Optional[dict], Optional[dict]]:
        """
        Retrieves vehicles and vehicle types from provider's API and converts them
        into gbfs vehicles, vehicle_types.
        Returns dicts where the key is the vehicle_id/vehicle_type_id and values
        are vehicle/vehicle_type.
        """
        gbfs_vehicle_types_map: dict[str, dict] = {}
        gbfs_vehicles_map: dict[str, dict] = {}

        for elem in self.api.all_vehicles(self.location_alias):
            self._extract_from_vehicle(elem, gbfs_vehicles_map, gbfs_vehicle_types_map)

        return gbfs_vehicle_types_map, gbfs_vehicles_map

    def load_stations(self, default_last_reported: int) -> Tuple[Optional[dict], Optional[dict]]:
        """
        Retrieves stations from the providers API and converts them
        into gbfs station infos and station status.
        Returns dicts where the key is the station_id and values
        are station_info/station_status.

        Note: station status' vehicle availabilty currently will be calculated
        using vehicle information's station_id, in case it is defined by this
        provider.
        """

        gbfs_station_infos_map: dict[str, dict] = {}
        gbfs_station_status_map: dict[str, dict] = {}

        for elem in self.api.parking_spots(self.location_alias):
            self._extract_from_parkings(elem, gbfs_station_infos_map, gbfs_station_status_map, default_last_reported)
        for elem in self.api.charging_stations(self.location_alias):
            self._extract_from_parkings(elem, gbfs_station_infos_map, gbfs_station_status_map, default_last_reported)

        return gbfs_station_infos_map, gbfs_station_status_map

    def _extract_from_parkings(
        self,
        elem: dict[str, Any],
        gbfs_station_infos_map: dict[str, dict],
        gbfs_station_status_map: dict[str, dict],
        default_last_reported: int,
    ) -> None:
        try:
            station_id = elem['id']
            center = elem['geometry']['coordinates']
            properties = elem['properties']

            station = {
                'station_id': station_id,
                'name': properties['name'],
                'lat': center[1],
                'lon': center[0],
                'capacity': properties['capacity'],
                'is_charging_station': properties['type'] == 'charging_station',
                'rental_methods': ['key'],
            }

            gbfs_station_infos_map[station_id] = station

            gbfs_station_status_map[station_id] = {
                'num_bikes_available': 0,
                'vehicle_types_available': {},
                'is_renting': True,
                'is_installed': True,
                'is_returning': True,
                'station_id': station_id,
                'last_reported': default_last_reported,
            }
        except Exception:
            logger.exception('Error extracting parking.')

    def _extract_from_vehicle(self, elem: dict, gbfs_vehicles_map: dict, gbfs_vehicle_types_map: dict) -> None:
        """
        Extract `vehicle` and `vehicle_type` from elem and add it to `gbfs_vehicles_map` and `gbfs_vehicle_types_map`
        """
        try:
            if not elem.get('freeForRental'):
                return

            # WARNING: this is a free floating operator.
            # For publicly available feeds (or apps that publish vehicle_ids),
            # IDs should change between rentals...
            vehicle_id = elem['vin']

            gbfs_vehicle_type = self._extract_vehicle_type(elem)
            vehicle_type_id = gbfs_vehicle_type['vehicle_type_id']

            current_fuel_percent = elem['fuelLevel'] / 100.0
            current_range_meters = int(gbfs_vehicle_type['max_range_meters'] * current_fuel_percent)

            gbfs_vehicle = {
                'bike_id': vehicle_id,
                'is_reserved': not elem.get('freeForRental', False),
                'is_disabled': False,
                'vehicle_type_id': vehicle_type_id,
                'current_fuel_percent': current_fuel_percent,
                'current_range_meters': current_range_meters,
                'lat': elem.get('geoCoordinate', {}).get('latitude'),
                'lon': elem.get('geoCoordinate', {}).get('longitude'),
                'rental_uris': {
                    key: uri.format(VIN=vehicle_id, locationId=self.location_id)
                    for key, uri in self.RENTAL_URI_TEMPLATES.items()
                },
            }

            if 'parkingId' in elem and len(elem['parkingId']) > 0:
                gbfs_vehicle['station_id'] = elem['parkingId']

            gbfs_vehicles_map[vehicle_id] = gbfs_vehicle
            gbfs_vehicle_types_map[vehicle_type_id] = gbfs_vehicle_type

        except KeyError:
            logger.exception(f'Vehicle extraction for {vehicle_id} failed!')

    def _extract_make_model(self, build_series):
        """
        Return make and model for build_series
        """
        if build_series in self.BUILD_SERIES_TO_MAKE_MODEL_MAPPING:
            return self.BUILD_SERIES_TO_MAKE_MODEL_MAPPING[build_series]
        splitted_build_series = build_series.split('_', 1)
        return splitted_build_series[0], splitted_build_series[-1]

    def _extract_color(self, elem: dict) -> str:
        """
        Extracts color from primaryColor and maps it to the color name defined in COLOR_MAPPING.
        If no mapping is defined / no primaryColor is set, the last part of the imageUrl
        splitted at underscores is used as color name. If there is no image url,
        an empty string is returned,
        """
        primary_color = elem.get('primaryColor')
        if primary_color in self.COLOR_MAPPING:
            return self.COLOR_MAPPING[primary_color]
        if 'imageUrl' not in elem:
            logger.info(f'No mapping defined for primaryColor {primary_color} and no image url to deduce it from')
            return ''

        # No color mapping, so we try to deduce from image url which apparently end with color name.
        url_suffix = elem['imageUrl'].split('_')[-1].split('.')[0]
        # To not return complete urls in case this changes one day,
        # we only return a maximum of 20 chars
        url_suffix = url_suffix[-20] if len(url_suffix) > 20 else url_suffix
        logger.info(f'No mapping defined for primaryColor {elem["primaryColor"]}, image url ends on {url_suffix}')
        return url_suffix

    def _extract_vehicle_type(self, elem: dict) -> dict:
        """
        Returns a gbfs vehicle_type dict extracted from elem
        """
        propulsion_type = self.FUELTYPE_TO_PROPULSION_MAPPING[elem['fuelType']] if 'fuelType' in elem else 'combustion'
        max_range_meters = (
            self.DEFAULT_ELECTRIC_MAX_RANGE_METERS
            if propulsion_type == 'electric'
            else self.DEFAULT_COMBUSTION_MAX_RANGE_METERS
        )

        build_series = str(elem['buildSeries'])
        color = self._extract_color(elem)
        vehicle_type_id = self._normalize_id(f'{build_series}_{color}')

        make, model = self.BUILD_SERIES_TO_MAKE_MODEL_MAPPING.get(build_series, ('', ''))
        default_pricing_plan_id, pricing_plan_ids = self._extract_pricing_plan_ids(build_series)

        gbfs_vehicle_type = {
            'vehicle_type_id': vehicle_type_id,
            'form_factor': 'car',
            'propulsion_type': propulsion_type,
            'max_range_meters': max_range_meters,
            'name': f'{make} {model}'.strip(),
            'default_pricing_plan_id': default_pricing_plan_id,
            'pricing_plan_ids': pricing_plan_ids,
            'wheel_count': 4,
            'make': make,
            'model': model,
            'return_constraint': 'free_floating',
            'vehicle_image': elem['imageUrl'].format(density='2x'),
        }

        if color:
            gbfs_vehicle_type['color'] = color

        if elem.get('seats'):
            gbfs_vehicle_type['seats'] = elem.get('seats')

        vehicle_accessories = elem.get('attributes')
        if isinstance(vehicle_accessories, list) and len(vehicle_accessories) > 0:
            logger.warning(
                'Vehicle type {vehicle_type_id} got accessories {vehicle_accessories}, which are currently not handled.'
            )

        return gbfs_vehicle_type

    def _extract_pricing_plan_ids(self, buildSeries: str) -> Tuple[str, list[str]]:
        """
        Returns the default_pricing_plan_id and a list of all pricing plans applying to this buildSeries.
        """
        pricing_plan_prefix = self.BUILD_SERIES_PRICING_PLAN_MAPPING.get(buildSeries)
        if not pricing_plan_prefix:
            logger.warn(f'No pricing_plan_prefix for buildSeries {buildSeries}, using "standard"')
            pricing_plan_prefix = 'standard'

        defined_pricing_plan_ids = self._defined_pricing_plan_ids(self.config)
        default_pricing_plan_id = f'{pricing_plan_prefix}_minute'
        all_pricing_plan_ids = [
            plan_id for plan_id in defined_pricing_plan_ids if plan_id.startswith(pricing_plan_prefix)
        ]

        # Log potentially missing pricing_plan definitions
        if default_pricing_plan_id not in defined_pricing_plan_ids:
            logger.warn(f'default_pricing_plan_id {default_pricing_plan_id} not defined in config')

        return default_pricing_plan_id, all_pricing_plan_ids

    def load_geofencing_zones(self):
        """
        Return (Multi)Polygon features that represent geofencing zones according to v2.3 spec.
        """
        operating_area = self.api.operating_area(self.location_alias)

        # We reverse polygon coords, as GBFSv2.3 spec says:
        # By default, no restrictions apply everywhere. Geofencing zones SHOULD be modeled according to restrictions rather
        # than allowance. An operational area (outside of which vehicles cannot be used)
        # SHOULD be defined with a counterclockwise polygon, and a limitation area
        # (in which vehicles can be used under certain restrictions) SHOULD
        # be defined with a clockwise polygon.
        # Note: GBFSv3 introduces global_rules which could be used to return standard GeoJSON with clockwise polygons.
        reverse_multipolygon(operating_area.get('geometry'))

        operating_area['properties'] = {
            'name': self.location_alias,
            'rules': [
                {
                    'ride_allowed': False,
                    'ride_through_allowed': True,
                    'station_parking': True,
                }
            ],
        }

        return [operating_area]
