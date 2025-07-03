import logging
from typing import Any, Dict, Generator, Optional, Tuple

from x2gbfs.providers.fleetster import FleetsterProvider

logger = logging.getLogger('x2gbfs.deer')


class Deer(FleetsterProvider):
    """
    Maps deer's vehicle categories to pricing plan category basic_line.
    All pricing_plans for basic_line are defined in feed_config.
    """

    CATEGORY_TO_PRICING_PLAN_CATEGORY_MAPPING = {
        'compact': 'basic_line',
        'midsize': 'basic_line',
        'city': 'basic_line',
        'fullsize': 'basic_line',
        'premium': 'basic_line',
        'economy': 'basic_line',
    }

    DEFAULT_VEHICLE_RETURN_CONSTRAINT = 'any_station'

    def __init__(self, feed_config: dict[str, Any], api):
        super().__init__(feed_config, api)
