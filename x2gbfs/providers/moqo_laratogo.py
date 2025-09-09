from typing import Any

from .moqo import MoqoProvider


class LaraToGoProvider(MoqoProvider):

    def _extract_from_vehicles(
        self,
        vehicle: dict[str, Any],
        vehicles: dict[str, Any],
        vehicle_types: dict[str, Any],
    ) -> None:
        if vehicle.get('license'):  # misused for description
            del vehicle['license']
        super()._extract_from_vehicles(vehicle, vehicles, vehicle_types)

    def _extract_vehicle_type(self, vehicle_types: dict[str, Any], vehicle: dict[str, Any]) -> str:
        id = super()._extract_vehicle_type(vehicle_types, vehicle)
        if vehicle_types[id]['form_factor'] == 'bicycle':
            vehicle_types[id]['form_factor'] = 'cargo_bicycle'
            vehicle_types[id]['max_range_meters'] = 50000
            vehicle_types[id]['make'] = 'Urban Arrow'
            vehicle_types[id]['model'] = 'Cargo'
            vehicle_types[id]['cargo_load_capacity'] = 125
        return id
