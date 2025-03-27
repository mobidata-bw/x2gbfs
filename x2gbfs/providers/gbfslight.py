import json
import logging
from typing import Any, Tuple

from x2gbfs.gbfs.base_provider import BaseProvider
from x2gbfs.util import get

logger = logging.getLogger(__name__)


class GbfsLightProvider(BaseProvider):

    DEFAULT_MAX_RANGE_METERS = 20000

    gbfslight = None

    def __init__(self, feed_config):
        self.config = feed_config
        self.url = feed_config['provider_data']['url']
        # TODO gbfs-light should publish a system_id which can be used to match system
        self.system_index = feed_config['provider_data']['index']

    def _load_system(self):
        if self.gbfslight is None:
            self.gbfslight = get(self.url).json()
        return self.gbfslight['system'][self.system_index]

    def load_system_information(self) -> dict[str, Any]:
        """
        Retrieves the system_information for this provider.
        It merges the provider config's
        feed_data/system_information section with information
        provided via gbfs-light system.
        """
        system = self._load_system()

        config_system_information = super().load_system_information()

        system_information = {
            'email': system.get('email') or system.get('mail'),  # Herrenberg should rename mail to email
        }
        # todo for now skip terms and privacy last updated (see https://github.com/MobilityData/gbfs/pull/693)
        for source_key in [
            'attribution_organization_name',
            'attribution_url',
            'feed_contact_email',
            'opening_hours',
            'language',
            'license_id',
            'license_url',
            'name',
            'operator',
            'phone_number',
            'privacy_url',
            'purchase_url',
            'terms_url',
            'url',
        ]:
            if source_key in system:
                system_information[source_key] = system[source_key]

        return system_information | config_system_information

    def load_vehicles(self, default_last_reported: int) -> Tuple[dict | None, dict | None]:
        system = self._load_system()

        gbfs_vehicle_types_map = {}

        gbfs_vehicles_map: dict[str, Any] = {}

        for vt in system['vehicle_types']:
            vehicle_type_id = self._normalize_id(vt['name'])

            gbfs_vehicle_type = {
                'vehicle_type_id': vehicle_type_id,
                'form_factor': vt['form_factor'],
                'propulsion_type': vt['propulsion_type'],
                'max_range_meters': vt.get('max_range_meters') or self.DEFAULT_MAX_RANGE_METERS,
                'name': vt['name'],
                'return_constraint': 'roundtrip_station',
            }

            gbfs_vehicle_types_map[vehicle_type_id] = gbfs_vehicle_type

        return gbfs_vehicle_types_map, gbfs_vehicles_map

    def load_stations(self, default_last_reported: int) -> Tuple[dict | None, dict | None]:
        gbfs_station_infos_map: dict[str, dict] = {}
        gbfs_station_status_map: dict[str, dict] = {}

        system = self._load_system()

        for elem in system['stations']:
            station_info = {
                'station_id': elem['id'],
                'lat': elem['lat'],
                'lon': elem['lon'],
                'name': elem['name'],
                'addresss': ' '.join([elem['address'].get('street'), elem['address'].get('houseNo')]),
                'post_code': elem['address'].get('post_code') or elem['address'].get('plz'),
                'city': elem['address'].get('city'),
                'capacity': elem['capacity'],
                'vehicle_type_capacity': [
                    {self._normalize_id(vt['name']): vt['available_count']} for vt in elem['vehicle_types']
                ],
            }

            if 'url' in elem:
                station_info['rental_uris'] = {'web': elem['url']}

            station_status = {
                'station_id': elem['id'],
                'is_installed': True,
                'is_renting': True,
                'is_returning': True,
                'last_reported': default_last_reported,
                'num_bikes_available': sum([vt['available_count'] for vt in elem['vehicle_types']]),
                'vehicle_types_available': [
                    {'vehicle_type_id': self._normalize_id(vt['name']), 'count': vt['available_count']}
                    for vt in elem['vehicle_types']
                ],
            }

            gbfs_station_infos_map[elem['id']] = station_info
            gbfs_station_status_map[elem['id']] = station_status

        return gbfs_station_infos_map, gbfs_station_status_map
