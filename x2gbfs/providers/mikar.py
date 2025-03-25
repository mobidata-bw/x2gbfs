import logging
from typing import Any, Dict, Generator, Optional, Tuple

from x2gbfs.providers.fleetster import FleetsterProvider

logger = logging.getLogger(__name__)


class MikarProvider(FleetsterProvider):

    CATEGORY_TO_PRICING_PLAN_CATEGORY_MAPPING = {'city': 'economy', 'midsize': 'economy', 'compact': 'economy'}

    def __init__(self, feed_config: dict[str, Any], api):
        super().__init__(feed_config, api)

    def default_pricing_plan_id(self, vehicle: Dict) -> Optional[str]:
        """
        Maps mikar's vehicle categories to pricing plans (provided via config).
        """
        pricing_plan_mapping = {'city': 'economy', 'midsize': 'economy', 'compact': 'economy'}

        category = (
            pricing_plan_mapping[vehicle['category']]
            if vehicle['category'] in pricing_plan_mapping
            else vehicle['category']
        )

        pricing_plan_id = f'{category}_hour'

        if pricing_plan_id in [pricing_plan['plan_id'] for pricing_plan in self.load_pricing_plans()]:
            return pricing_plan_id

        raise OSError(f'No default_pricing_plan mapping for category {category}')
