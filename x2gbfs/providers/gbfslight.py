import json
import logging
from typing import Any, Tuple

from x2gbfs.gbfs.base_provider import BaseProvider
from x2gbfs.util import get

logger = logging.getLogger(__name__)


def fix_url(url: str) -> str:
    # Patch: Herrenberg currently uses Umlauts in their URL
    # For now, we patch this here, but Herrenberg should fix this
    # We explicitly do not urlencoding here, as this might break valid urls
    # in the future.
    return url.replace('ä', '%C3%A4')


class GbfsLightProvider(BaseProvider):

    DEFAULT_MAX_RANGE_METERS = 20000

    gbfslight_data: dict[str, Any] | None = None

    def __init__(self, feed_config: dict[str, Any]) -> None:
        self.config = feed_config
        self.url = feed_config['provider_data']['url']
        self.system_id = feed_config['provider_data']['system_id']

    def _load_system(self) -> dict[str, Any]:
        if self.gbfslight_data is None:
            self.gbfslight_data = get(self.url).json()
        return next(system for system in self.gbfslight_data['system'] if system['system_id'] == self.system_id)

    def load_system_information(self) -> dict[str, Any]:
        """
        Retrieves the system_information for this provider.
        It merges the provider config's
        feed_data/system_information section with information
        provided via gbfs-light system.
        """
        config_system_information = super().load_system_information()
        system = self._load_system()
        system_information = {
            # we use the configured, not the published system_id
            'system_id': self.system_id
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
            'email',
            'operator',
            'phone_number',
            'privacy_last_updated',
            'privacy_url',
            'purchase_url',
            'terms_last_updated',
            'terms_url',
            'timezone',
            'url',
        ]:
            if source_key in system:
                system_information[source_key] = system[source_key]
            elif self.gbfslight_data is not None and source_key in self.gbfslight_data:
                system_information[source_key] = self.gbfslight_data[source_key]

        # Patch: Herrenberg does not deliver dates in iso data format
        for date_field in ['privacy_last_updated', 'terms_last_updated']:
            if date_field in system_information and system_information[date_field].count('.') == 2:
                date_components = system_information[date_field].split('.')
                system_information[date_field] = f'{date_components[2]}-{date_components[1]}-{date_components[0]}'
        if 'url' in system_information:
            system_information['url'] = fix_url(system_information['url'])

        # Published system information get's higher priority than configured
        # Note: this requires savy publishers. In case this does not hold, we
        # might need to switch or make precedence configurable
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
                'address': elem.get('address'),
                'post_code': elem.get('post_code'),
                'city': elem.get('city'),
                'capacity': elem['capacity'],
                'vehicle_type_capacity': {
                    self._normalize_id(vt['name']): vt['available_count'] for vt in elem['vehicle_types']
                },
            }

            if 'url' in elem:
                station_info['rental_uris'] = {'web': fix_url(elem['url'])}

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
