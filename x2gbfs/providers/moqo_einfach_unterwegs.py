from typing import Any

from .moqo import MoqoProvider


class EinfachUnterwegsProvider(MoqoProvider):

    def _extract_vehicle_type(self, vehicle_types: dict[str, Any], vehicle: dict[str, Any]) -> str:
        id = super()._extract_vehicle_type(vehicle_types, vehicle)
        if vehicle_types[id]['name'] == 'Urban Arrow Family':
            vehicle_types[id]['form_factor'] = 'cargo_bicycle'
            vehicle_types[id]['max_range_meters'] = 100000
            vehicle_types[id]['make'] = 'Urban Arrow'
            vehicle_types[id]['model'] = 'Family'
            vehicle_types[id]['cargo_load_capacity'] = 125
        return id
