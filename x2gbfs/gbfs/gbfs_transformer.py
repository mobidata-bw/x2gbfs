from collections import Counter
from datetime import datetime
from typing import Any, Collection, Dict, List, Optional, Tuple

from .base_provider import BaseProvider


class GbfsTransformer:

    # Max coordinate precision is used to round coordinates of vehicles and stations.
    # Six decimal places correspond, depending on the position, roughly to 0.1m
    # see https://wiki.openstreetmap.org/wiki/Precision_of_coordinates
    MAX_COORDINATE_PRECISION = 6

    def load_system_information(self, provider: BaseProvider) -> Dict[str, Any]:
        """
        Loads system_information information from the provider.
        """
        return provider.load_system_information()

    def load_pricing_plans(self, provider: BaseProvider) -> Optional[List[Dict[str, Any]]]:
        """
        Loads pricing plans information from the provider.
        """
        return provider.load_pricing_plans()

    def load_alerts(self, provider: BaseProvider) -> Optional[List[Dict[str, Any]]]:
        """
        Loads alerts information from the provider.
        """
        return provider.load_alerts()

    def load_stations_and_vehicles(
        self, provider: BaseProvider
    ) -> Tuple[Optional[List], Optional[List], Optional[List], Optional[List], Optional[List], int]:
        """
        Load stations and vehicles from provider, updates vehicle availabilities at stations
        and returns gbfs collections station_infos, station_status, vehicle_types, vehicles.

        Note, that all these collections are conditionally required, and hence may be missing
        (see e.g. https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md#files)

        """
        default_last_reported = int(datetime.timestamp(datetime.now()))

        station_infos_map, station_status_map, vehicle_types_map, vehicles_map = provider.load_stations_and_vehicles(
            default_last_reported
        )

        geofencing_zones = (
            provider.load_geofencing_zones() if callable(getattr(provider, 'load_geofencing_zones', None)) else None
        )

        if station_status_map and vehicles_map:
            # if feed has stations and vehicles, we deduce vehicle_types_available
            # information from vehicle.station_id information
            self._update_stations_availability_status(station_status_map, vehicles_map)

        if vehicles_map:
            self._round_coordinates(vehicles_map.values())
        if station_infos_map:
            self._round_coordinates(station_infos_map.values())

        return (
            list(station_infos_map.values()) if station_infos_map else None,
            list(station_status_map.values()) if station_status_map else None,
            # Note: if vehicle_types are not provided, all vehicles are assumed to be non motorized bikes https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md#files
            list(vehicle_types_map.values()) if vehicle_types_map else None,
            list(vehicles_map.values()) if vehicles_map else None,
            list(geofencing_zones) if geofencing_zones else None,
            default_last_reported,
        )

    @staticmethod
    def _round_coordinates(vehicles_or_stations: Collection[dict[str, Any]]) -> None:
        """
        Rounds lat/lon properties of the given list of vehicles or station dicts.
        """
        for vehicle_or_station in vehicles_or_stations:
            if isinstance(vehicle_or_station.get('lat'), float):
                vehicle_or_station['lat'] = round(vehicle_or_station['lat'], GbfsTransformer.MAX_COORDINATE_PRECISION)
            if isinstance(vehicle_or_station.get('lon'), float):
                vehicle_or_station['lon'] = round(vehicle_or_station['lon'], GbfsTransformer.MAX_COORDINATE_PRECISION)

    def _count_vehicle_types_at_station(self, vehicles_map, filter) -> Counter:
        filtered_vehicle_map = {k: v for k, v in vehicles_map.items() if filter(v)}
        station_vehicle_type_arr = [(v['station_id'], v['vehicle_type_id']) for v in filtered_vehicle_map.values()]

        return Counter(station_vehicle_type_arr)

    def _update_stations_availability_status(self, status_map: Dict[str, Dict], vehicles_map: Dict[str, Dict]) -> None:
        """
        Updates station_status' vehicle_types_available and num_bikes_available.
        A vehicle_type is available at a station, when any vehicle of it's type
        is assigned to this station. However, for the availabilty count,
        only those vehicles not reserved and not disabled are taken into account.
        """

        station_vehicle_type_free_cnt = self._count_vehicle_types_at_station(
            vehicles_map, lambda v: not v['is_reserved'] and not v['is_disabled'] and 'station_id' in v
        )
        station_vehicle_type_cnt = self._count_vehicle_types_at_station(vehicles_map, lambda v: 'station_id' in v)

        vehicle_types_per_station: Dict[str, list] = {}
        for station_vehicle_type in station_vehicle_type_cnt:
            station_id = station_vehicle_type[0]

            if station_id not in vehicle_types_per_station:
                vehicle_types_per_station[station_id] = []

            vehicle_types_per_station[station_id].append(
                {
                    'vehicle_type_id': station_vehicle_type[1],
                    'count': station_vehicle_type_free_cnt.get(station_vehicle_type, 0),
                }
            )

        for station_id in status_map.keys():
            if station_id in vehicle_types_per_station:
                self._update_station_availability_status(vehicle_types_per_station[station_id], status_map[station_id])
            else:
                status_map[station_id]['vehicle_types_available'] = []
                if 'num_bikes_available' not in status_map[station_id]:
                    # num_bikes_available might have been set by provider,
                    # so we only redefine if this is not the case
                    status_map[station_id]['num_bikes_available'] = 0

    def _update_station_availability_status(
        self, vt_available: List[Dict[str, Any]], station_status: Dict[str, Any]
    ) -> None:
        """
        Sets station_status.vehicle_types_available and
        calculates num_bikes_available as the sum of all vehicle_types_available.
        Retains pre-existing vehicle_types_available (usually having count 0)
        for vehicle_type_ids without available vehicles,
        as this is the only way to find out, if vehicles are for rent at this station.
        """
        num_bikes_available = sum([vt['count'] for vt in vt_available])
        station_status['num_bikes_available'] = num_bikes_available
        station_status['vehicle_types_available'] = self._merge_vehicle_types_available(
            vt_available, station_status.get('vehicle_types_available')
        )

    def _merge_vehicle_types_available(
        self, vt_available: List[Dict[str, Any]], pre_existing_vt: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Merges vehicle_types_available lists.
        """
        if not pre_existing_vt:
            return vt_available

        # convert both to map, merge, reconvert to list
        vt_map = {vt['vehicle_type_id']: vt for vt in vt_available}
        vt_map_fallback = {vt['vehicle_type_id']: vt for vt in pre_existing_vt}
        vt_merged = {**vt_map_fallback, **vt_map}
        return list(vt_merged.values())
