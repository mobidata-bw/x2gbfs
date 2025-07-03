import logging
from typing import Any, Dict, Generator, Optional, Tuple

from x2gbfs.providers.fleetster import FleetsterProvider

logger = logging.getLogger(__name__)


class MikarProvider(FleetsterProvider):

    # Vehicles in Monheim have different pricing, so we create a specific vehicle type for them
    MONHEIM_STATION_IDS = ['5cc7ffad44fb25000546b74a', '5cd53d13cdfe4d0005e88423']

    # Vehicles in Monheim have different pricing, so we create a specific vehicle type for them
    VEHICLE_TYPE_TO_PRICING_PLAN_CATEGORY_MAPPING = {
        'renault_megane_e_tech_monheim': 'midsize',
        'renault_zoe_monheim': 'midsize',
    }

    # We reduce the different categories to three representive ones
    CATEGORY_TO_PRICING_PLAN_CATEGORY_MAPPING = {
        'city': 'midsize',
        'fullsize': 'midsize',
        'midsize': 'economy',
        'compact': 'economy',
    }

    # Some vehicles are assigned to categories which do not match pricing given at https://mikar.de/fahrzeuge-tarife/
    MODEL_TO_PRICING_PLAN_CATEGORY_MAPPING = {'Transit': 'transporter', 'Megane E Tech': 'economy'}

    def __init__(self, feed_config: dict[str, Any], api):
        super().__init__(feed_config, api)

    def _default_pricing_plan_id(self, vehicle: Dict) -> str:
        """
        Maps mikar's vehicle categories to pricing plans (provided via config).
        """

        if self._vehicle_type_id(vehicle) in self.VEHICLE_TYPE_TO_PRICING_PLAN_CATEGORY_MAPPING:
            category = self.VEHICLE_TYPE_TO_PRICING_PLAN_CATEGORY_MAPPING[self._vehicle_type_id(vehicle)]
        elif vehicle['model'] in self.MODEL_TO_PRICING_PLAN_CATEGORY_MAPPING:
            category = self.MODEL_TO_PRICING_PLAN_CATEGORY_MAPPING[vehicle['model']]
        elif vehicle['category'] in self.CATEGORY_TO_PRICING_PLAN_CATEGORY_MAPPING:
            category = self.CATEGORY_TO_PRICING_PLAN_CATEGORY_MAPPING[vehicle['category']]
        else:
            category = vehicle['category']

        pricing_plan_id = f'{category}_hour'

        if pricing_plan_id in [pricing_plan['plan_id'] for pricing_plan in self.load_pricing_plans()]:
            return pricing_plan_id

        raise OSError(f'No default_pricing_plan mapping for category {category}')

    def _vehicle_type_id(self, fleetster_vehicle: Dict[str, Any]):
        normalized_brand = self._normalize_brand(fleetster_vehicle['brand'])
        normalized_model = self._normalize_model(fleetster_vehicle['model'])

        vehicle_type_id = self._normalize_id(normalized_brand + '_' + normalized_model)
        if fleetster_vehicle['locationId'] in self.MONHEIM_STATION_IDS:
            return f'{vehicle_type_id}_monheim'
        return vehicle_type_id
