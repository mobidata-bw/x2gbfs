import logging
import re
from typing import Any, Dict, Generator, Optional, Tuple

logger = logging.getLogger('x2gbfs.base_provider')


class BaseProvider:
    def load_stations(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Retrieves stations from the providers API and converts them
        into gbfs station infos and station status.
        Returns dicts where the key is the station_id and values
        are station_info/station_status.

        For free floating only providers, this method needs not to be overwritten.

        Note: station status' vehicle availabilty currently will be calculated
        using vehicle information's station_id, in case it is defined by this
        provider.
        """
        return None, None

    def load_vehicles(self, default_last_reported: int) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Retrieves vehicles and vehicle types from provider's API and converts them
        into gbfs vehicles, vehicle_types.
        Returns dicts where the key is the vehicle_id/vehicle_type_id and values
        are vehicle/vehicle_type.
        """
        return None, None

    def load_geofencing_zones(self) -> Optional[Dict]:
        """
        Retrieves geofencing_zones.
        Returns a list of features complying with the GBFS 2.3 geofencing zone feature spec
        https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md#geofencing_zonesjson or None.
        """
        return None

    def _filter_vehicles_at_inexistant_stations(self, vehicles_map, station_infos_map):
        """
        Filters vehicles which have a station assigned that is not contained in station_info_map
        """
        if vehicles_map and station_infos_map:
            for vehicle_id in list(vehicles_map.keys()):
                station_id = vehicles_map[vehicle_id].get('station_id')

                if station_id not in station_infos_map:
                    logger.info(
                        f'Vehicle {vehicle_id} is assigned to inexistant station {station_id}, it will be removed from feed'
                    )
                    vehicles_map.pop(vehicle_id)

    def load_stations_and_vehicles(
        self, default_last_reported: int
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict], Optional[Dict]]:
        """
        Retrieves stations vehicles and vehicle types from provider's API and converts them
        into gbfs station infos, gbfs station status, gbfs vehicles and  vehicle_types.
        Returns dicts where the key is the station_id/vehicle_id/vehicle_type_id and values
        are station_info/station_status/vehicle/vehicle_type.

        Note: subclasses may choose to implement this method or load_vehicles / load_stations.
        """
        station_infos_map, station_status_map = self.load_stations(default_last_reported)
        vehicle_types_map, vehicles_map = self.load_vehicles(default_last_reported)

        self._filter_vehicles_at_inexistant_stations(vehicles_map, station_infos_map)

        return station_infos_map, station_status_map, vehicle_types_map, vehicles_map

    def _create_station_status(self, station_id: str, last_reported: int) -> Dict[str, Any]:
        """
        Return a new default station status, which needs to be updated later on.
        """
        return {
            'num_bikes_available': 0,
            'is_renting': True,
            'is_installed': True,
            'is_returning': True,
            'station_id': station_id,
            'vehicle_types_available': [],
            'last_reported': last_reported,
        }

    @staticmethod
    def _normalize_id(id: str) -> str:
        """
        Normalizes the ID by restricting chars to A-Za-z_0-9. Whitespaces are converted to _.
        """
        return re.sub('[^A-Za-z_0-9]', '', id.lower().replace(' ', '_')).replace('__', '_')
