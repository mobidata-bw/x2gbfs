from typing import Any, Dict, Generator, Optional, Tuple


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
