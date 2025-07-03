import json
import logging
from typing import Any

from x2gbfs.gbfs.base_provider import BaseProvider
from x2gbfs.util import get, unidecode_with_german_umlauts

logger = logging.getLogger(__name__)


class CambioProvider(BaseProvider):
    """
    The CambioProvider retrieves (static) stations and vehicleClasses from Cambio API.

    """

    DEFAULT_MAX_RANGE_ELECTRIC = 200000
    DEFAULT_MAX_RANGE_COMBUSTION = 600000
    STATIONS_URL = 'https://cwapi.cambio-carsharing.com/opendata/v1/mandator/{city_id}/stations'
    VEHICLE_TYPES_URL = 'https://cwapi.cambio-carsharing.com/opendata/v1/mandator/{city_id}/vehicles'

    def __init__(self, feed_config: dict[str, Any]):
        self.city_id = feed_config['provider-info']['city_id']
        self.config = feed_config

    def _all_stations(self) -> list[dict[str, Any]]:
        response = get(self.STATIONS_URL.format(city_id=self.city_id))
        response.raise_for_status()
        ret: list[dict[str, Any]] = response.json()
        return ret

    def _all_vehicle_types(self) -> list[dict[str, Any]]:
        response = get(self.VEHICLE_TYPES_URL.format(city_id=self.city_id))
        response.raise_for_status()
        ret: list[dict[str, Any]] = response.json()
        return ret

    def load_stations(self, default_last_reported: int) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        """
        Retrieves stations from cambio API and converts them
        into gbfs station infos and station status.
        Note: station status does not reflect vehicle availabilty and needs
        to be updated when vehicle information was retrieved.
        """

        result = self._all_stations()

        gbfs_station_infos_map: dict[str, dict[str, Any]] = {}
        gbfs_station_status_map: dict[str, dict[str, Any]] = {}

        for elem in result:
            geo_position = elem['geoposition']
            station_id = elem['id']
            address = elem['address']
            vehicle_types_available = self._extract_vehicle_types_available(elem)
            rental_uris = self._extract_station_rental_uris(elem)
            gbfs_station = {
                'lat': geo_position.get('latitude'),
                'lon': geo_position.get('longitude'),
                'name': elem.get('displayName', elem.get('name')),
                'station_id': station_id,
                'address': f"{address.get('streetAddress')} {address.get('streetNumber')}",
                'post_code': address.get('postalCode'),
                'city': address.get('addressLocation'),  # Non-standard
                'rental_uris': rental_uris,
            }

            gbfs_station_status = self._create_station_status(station_id, default_last_reported)
            gbfs_station_status.update(
                {
                    'vehicle_types_available': vehicle_types_available,
                    'num_bikes_available': len(vehicle_types_available),
                }
            )

            gbfs_station_infos_map[station_id] = gbfs_station
            gbfs_station_status_map[station_id] = gbfs_station_status

        return gbfs_station_infos_map, gbfs_station_status_map

    def load_vehicles(
        self, default_last_reported: int
    ) -> tuple[dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
        """
        Returns vehicle_types_map and vehicles_map, both keyed by the vehicle's/vehicle type's ID.
        It's values must be dicts conforming to GBFS Spec v2.3 vehicles / vehicle types.
        For details, see https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md
        """

        result = self._all_vehicle_types()

        gbfs_vehicle_types_map: dict[str, dict[str, Any]] = {}
        gbfs_vehicles_map: dict[str, dict[str, Any]] = {}
        for elem in result:
            # Note: usually you would iterate over a data source retrieve from a proprietary
            # system and convert it to vehicles, reflectig theit real-time properties.
            vehicle_type_id = elem['id']
            propulsion_type = self._extract_propulsion_type(elem)

            gbfs_vehicle_type = {
                'vehicle_type_id': vehicle_type_id,
                'name': elem['displayName'],
                'form_factor': 'car',
                'default_pricing_plan': elem['priceClass']['id'],
                'propulsion_type': propulsion_type,
                'max_range_meters': (
                    self.DEFAULT_MAX_RANGE_ELECTRIC
                    if propulsion_type == 'electric'
                    else self.DEFAULT_MAX_RANGE_COMBUSTION
                ),
                'wheel_count': 4,
                'return_constraint': 'roundtrip_station',
            }
            gbfs_vehicle_types_map[vehicle_type_id] = gbfs_vehicle_type

        return gbfs_vehicle_types_map, gbfs_vehicles_map

    def _extract_vehicle_types_available(self, elem: dict[str, Any]) -> list[dict[str, str | int]]:
        """
        Extracts a list of vehicle_types_available from station. As it is static,
        we declare an availability of 1 per vehicle_type, though this incorrect.
        """
        vehicle_classes_at_station = elem.get('vehicleClasses', [])
        return [{'vehicle_type_id': vehicle_class['id'], 'count': 1} for vehicle_class in vehicle_classes_at_station]

    def _extract_propulsion_type(self, elem: dict[str, str]) -> str:
        """
        Guesses the propulsion type from vehicle name.
        """
        lowercase_name = elem['displayName'].lower()

        if 'e-auto' in lowercase_name or 'smart ed' in lowercase_name:
            return 'electric'
        if 'transporter' in lowercase_name:
            return 'combustion_diesel'

        return 'combustion'

    def _extract_station_rental_uris(self, elem: dict[str, str]) -> dict[str, str]:
        """
        Guesses the propulsion type from vehicle name.
        """
        station_name = unidecode_with_german_umlauts(elem['name'].lower())
        station_url = f"https://www.cambio-carsharing.de/stationen/station/{station_name}-{elem['id']}"

        return {
            'web': station_url,
        }
