from abc import ABC, abstractmethod
from typing import Tuple, Union


class BaseProvider(ABC):
    @abstractmethod
    def load_stations(self, default_last_reported: int) -> Tuple[dict, dict]:
        """
        Retrieves stations from the providers API and converts them
        into gbfs station infos and station status.
        Returns dicts where the key is the station_id and values
        are station_info/station_status.

        Note: station status' vehicle availabilty currently will be calculated
        using vehicle information's station_id, in case it is defined by this
        provider.
        """
        pass

    @abstractmethod
    def load_vehicles(self, default_last_reported: int) -> Tuple[dict, dict]:
        """
        Retrieves vehicles and vehicle types from provider's API and converts them
        into gbfs vehicles, vehicle_types.
        Returns dicts where the key is the vehicle_id=vehicle and values
        are station_info/station_status.
        """
        pass
