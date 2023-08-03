from collections import Counter
from datetime import datetime


class GbfsTransformer:
    def load_stations_and_vehicles(self, provider):
        """
        Load stations and vehicles from provider, updates vehicle availabilities at stations
        and returns gbfs collections station_infos, station_status, vehicle_types, vehicles.
        """
        default_last_reported = int(datetime.timestamp(datetime.now()))

        station_infos_map, station_status_map = provider.load_stations(default_last_reported)
        vehicle_types_map, vehicles_map = provider.load_vehicles(default_last_reported)
        self._update_stations_availability_status(station_status_map, vehicles_map)
        return (
            list(station_infos_map.values()),
            list(station_status_map.values()),
            list(vehicle_types_map.values()),
            list(vehicles_map.values()),
        )

    def _update_stations_availability_status(self, status_map, vehicles_map):
        """
        Updates station_status' vehicle_types_available and num_bikes_available.
        A vehicle is available at a station, when it's station_id matches and it
        is not reserved and not disabled.

        """

        filtered_vehicle_map = {k: v for k, v in vehicles_map.items() if not v['is_reserved'] and not v['is_disabled']}
        station_vehicle_type_arr = [(v['station_id'], v['vehicle_type_id']) for v in filtered_vehicle_map.values()]
        station_vehicle_type_cnt = Counter(station_vehicle_type_arr)

        vehicle_types_per_station = {}
        for station_vehicle_type in station_vehicle_type_cnt:
            station_id = station_vehicle_type[0]

            if station_id not in vehicle_types_per_station:
                vehicle_types_per_station[station_id] = []

            vehicle_types_per_station[station_id].append(
                {'vehicle_type_id': station_vehicle_type[1], 'count': station_vehicle_type_cnt[station_vehicle_type]}
            )

        for station_id in vehicle_types_per_station.keys():
            if station_id in status_map:
                self._update_station_availability_status(vehicle_types_per_station[station_id], status_map[station_id])

    def _update_station_availability_status(self, vt_available, station_status):
        num_bikes_available = sum([vt['count'] for vt in vt_available])
        station_status['num_bikes_available'] = num_bikes_available
        if num_bikes_available > 0:
            station_status['vehicle_types_available'] = vt_available
