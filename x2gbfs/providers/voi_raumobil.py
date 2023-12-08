import base64
import logging
from typing import Dict, Generator, Optional, Tuple

import requests

from x2gbfs.gbfs.base_provider import BaseProvider

logger = logging.getLogger(__name__)


class VoiRaumobil(BaseProvider):
    """

    This is an implementation of free-floating voi scooter data retrieved from
    raumobil API platform's endpoint.

    As it is not station based, only vehicles and one single vehicle type are extracted
    from the base system.

    System information and pricing information are read from config/voi-raumobil.json.

    Note: to be able to run this via x2gbfs, this VoiRaumobil class needs to be added
    to x2gbfs.py's build_extractor method.

    Raumobil API/Platform is available here:
    https://lsd.raumobil.net/

    Note: The implementation of this provider is currently maintained by
    Nahverkehrsgesellschaft Baden-Wuerttemberg mbH (NVBW), Germany.
    """

    api_url: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

    VEHICLE_TYPES = {
        'scooter': {
            # See https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md#vehicle_typesjson
            'vehicle_type_id': 'scooter',
            'form_factor': 'scooter',
            'propulsion_type': 'electric',
            'max_range_meters': 10000,
            'name': 'Scooter',
            'wheel_count': 2,
            'return_type': 'free_floating',
            'default_pricing_plan_id': 'basic',  # refers to a pricing plan specified in config/voi-raumobil.json
        }
    }

    def __init__(self, api_url: str, user: str, password: str) -> None:
        self.api_url = api_url
        self.user = user
        self.password = password

    def all_vehicles(self) -> Generator[Dict, None, None]:
        results = self._get_with_authorization(f'{self.api_url}')
        features = results['result']['u0ty']['features']
        vehicles = [feature for feature in features if feature['properties']['featureType'] == 'Vehicle']
        for vehicle in vehicles:
            yield vehicle

    def _get_with_authorization(self, url: str) -> Dict:
        """
        Gets the data from the provider Platform using the provider's credentials,
        and returns the response as (json) dict.

        The request is performed with the API credentials of the provider.
        """
        user_pass = f'{self.user}:{self.password}'
        user_auth = base64.b64encode(user_pass.encode()).decode()
        response = requests.post(url, headers={'Authorization': 'Basic %s' % user_auth}, timeout=10)

        response.raise_for_status()
        return response.json()

    def load_vehicles(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Returns vehicle_types_map (with a single vehicle type)
        and vehicles_map, both keyed by the vehicle's/vehicle type's ID.

        Note: current_fuel_percent is expressed from 0 to 1 (i.e 0 to 100 percent).

        It's values must be dicts conforming to GBFS Spec v2.3 vehicles / vehicle types.
        For details, see https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md
        """

        gbfs_vehicles_map = {}
        for elem in self.all_vehicles():
            # Note: usually you would iterate over a data source retrieve from a proprietary
            # system and convert it to vehicles, reflecting their real-time properties.
            vehicle_id = elem['properties']['id']
            # The provider/type  prefixwill be introduced by lamassu, so we chop it off here
            if vehicle_id.startswith('VOI:VEHICLE:'):
                vehicle_id = vehicle_id[len('VOI:VEHICLE:') :]

            gbfs_vehicle = {
                'bike_id': vehicle_id,
                'vehicle_type_id': 'scooter',
                'is_reserved': False,
                'is_disabled': False,
                'current_range_meters': 10000,
                'current_fuel_percent': round((int(elem['properties']['extended']['batteryStatus']) * 0.01), 2),
                'lat': elem['geometry']['coordinates'][1],
                'lon': elem['geometry']['coordinates'][0],
            }

            gbfs_vehicles_map[vehicle_id] = gbfs_vehicle

        return self.VEHICLE_TYPES, gbfs_vehicles_map
