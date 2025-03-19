import logging
from typing import Any, Dict, Optional, Tuple

from x2gbfs.gbfs.base_provider import BaseProvider

logger = logging.getLogger(__name__)


class ExampleProvider(BaseProvider):
    """
    This is an ExampleProvider which demonstrates how to implement a free-floatig only, e.g. scooter,
    provider.

    As it is not station based, only vehicles and one sigle vehicle type need to e extracted
    from the base system. This demo just returns some fake objects.

    System information and pricing information is read from config/example.json.

    Note: to be able to run this via x2gbfs, this ExampleProvider needs to
    is added to x2gbfs.py's build_extractor method.

    """

    VEHICLE_TYPES = {
        'scooter': {
            # See https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md#vehicle_typesjson
            'vehicle_type_id': 'scooter',
            'form_factor': 'scooter',
            'propulsion_type': 'electric',
            'max_range_meters': 10000,
            'name': 'Scooter',
            'wheel_count': 2,
            'return_constraint': 'free_floating',
            'default_pricing_plan_id': 'basic',  # refers to a pricing plan specified in config/example.json
        }
    }

    def __init__(self, feed_config: dict[str, Any]):
        self.config = feed_config

    def load_vehicles(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Returns vehicle_types_map (with a single vehicle type)
        and vehicles_map, both keyed by the vehicle's/vehicle type's ID.
        It's values must be dicts conforming to GBFS Spec v2.3 vehicles / vehicle types.
        For details, see https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md
        """

        gbfs_vehicles_map = {}
        for i in range(1, 10):
            # Note: usually you would iterate over a data source retrieve from a proprietary
            # system and convert it to vehicles, reflectig theit real-time properties.
            vehicle_id = f'vehicle_{i}'

            gbfs_vehicle = {
                'bike_id': vehicle_id,
                'vehicle_type_id': 'scooter',
                'is_reserved': False,
                'is_disabled': False,
                'current_range_meters': 10000,
                'lat': 49,
                'lon': 9,
            }

            gbfs_vehicles_map[vehicle_id] = gbfs_vehicle

        return self.VEHICLE_TYPES, gbfs_vehicles_map
