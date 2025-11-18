import copy
import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

OPENING_HOURS_DEFAULT = '24/7'
PHONE_NUMBER_GBFS_V3_PATTERN = re.compile(r'^\+\d+$')


class GbfsV2Writer:

    VEHICLE_STATUS_FEED_NAME = 'free_bike_status'
    VEHICLE_STATUS_KEY = 'bikes'

    def __init__(self):
        pass

    def _dump_json(self, filename: str, content: dict):
        with open(filename, 'w') as dest:
            json.dump(content, dest, indent=2)

    def gbfs_data(self, base_url: str, feeds: List[str], feed_language: str) -> Dict:
        return {feed_language: {'feeds': [{'name': feed, 'url': f'{base_url}/{feed}.json'} for feed in feeds]}}

    def write_gbfs_file(self, filename: str, data, timestamp: int, ttl: int = 60) -> None:
        content = {'data': data, 'last_updated': timestamp, 'ttl': ttl, 'version': '2.3'}
        self._dump_json(filename, content)

    def write_gbfs_feed(
        self,
        destFolder: str,
        system_information: Dict,
        station_information: Optional[List[Dict]],
        station_status: Optional[List[Dict]],
        vehicle_types: Optional[List[Dict]],
        vehicles: Optional[List[Dict]],
        geofencing_zones: Optional[List[Dict]],
        pricing_plans: Optional[List[Dict]],
        alerts: Optional[List[Dict]],
        base_url: str,
        timestamp: int,
        ttl: int = 60,
    ) -> None:
        Path(destFolder).mkdir(parents=True, exist_ok=True)

        feeds = ['system_information']
        self.write_gbfs_file(destFolder + '/system_information.json', system_information, timestamp, ttl)
        if station_information and station_status:
            feeds.extend(('station_information', 'station_status'))
            self.write_gbfs_file(
                destFolder + '/station_information.json', {'stations': station_information}, timestamp, ttl
            )
            self.write_gbfs_file(destFolder + '/station_status.json', {'stations': station_status}, timestamp, ttl)
        elif station_information or station_status:
            logger.error(
                f'For feed {system_information["system_id"]}, only one of station_information or station_status was returned. Skipping station generation.'
            )
        else:
            logger.debug(
                f'Got no station info for feed {system_information["system_id"]}, generating free floating infos only'
            )
        if vehicles:
            feeds.append(self.VEHICLE_STATUS_FEED_NAME)
            self.write_gbfs_file(
                f'{destFolder}/{self.VEHICLE_STATUS_FEED_NAME}.json',
                {self.VEHICLE_STATUS_KEY: vehicles},
                timestamp,
                ttl,
            )
        if vehicle_types:
            feeds.append('vehicle_types')
            self.write_gbfs_file(destFolder + '/vehicle_types.json', {'vehicle_types': vehicle_types}, timestamp, ttl)
        if pricing_plans:
            feeds.append('system_pricing_plans')
            self.write_gbfs_file(destFolder + '/system_pricing_plans.json', {'plans': pricing_plans}, timestamp, ttl)
        if geofencing_zones:
            feeds.append('geofencing_zones')
            self.write_gbfs_file(
                destFolder + '/geofencing_zones.json',
                {'geofencing_zones': {'type': 'FeatureCollection', 'features': geofencing_zones}},
                timestamp,
                ttl,
            )

        if alerts:
            feeds.append('system_alerts')
            self.write_gbfs_file(destFolder + '/system_alerts.json', {'alerts': alerts}, timestamp, ttl)

        if 'languages' in system_information:
            feed_language = system_information['languages'][0]
        elif 'language' in system_information:
            feed_language = system_information['language']
        else:
            raise Exception('Config neither provides language nor languages to deduce feed language')

        self.write_gbfs_file(destFolder + '/gbfs.json', self.gbfs_data(base_url, feeds, feed_language), timestamp, ttl)


class GbfsV3Writer(GbfsV2Writer):

    VEHICLE_STATUS_FEED_NAME = 'vehicle_status'
    VEHICLE_STATUS_KEY = 'vehicles'

    def write_gbfs_file(self, filename: str, data, timestamp: int, ttl: int = 60) -> None:
        content = {
            'data': data,
            'last_updated': datetime.fromtimestamp(timestamp, UTC).strftime('%Y-%m-%dT%H:%M:%S%z'),
            'ttl': ttl,
            'version': '3.0',
        }
        self._dump_json(filename, content)

    def gbfs_data(self, base_url: str, feeds: List[str], feed_language: str) -> Dict:
        return {'feeds': [{'name': feed, 'url': f'{base_url}/{feed}.json'} for feed in feeds]}

    def _convert_system_information_to_v3(self, system_information):
        # This function converts a (possibly) v2 system_information into
        # a v3 compliant system_information.
        # If it's already a valid v3 config, it will be unchanged.

        new_system_information = copy.deepcopy(system_information)
        system_id = system_information['system_id']

        if 'language' in new_system_information:
            feed_language = new_system_information.pop('language')
            new_system_information['languages'] = [feed_language]

        for key in [
            'name',
            'attribution_organization_name',
            'terms_url',
            'privacy_url',
            'operator',
        ]:
            if key in new_system_information and isinstance(new_system_information[key], str):
                new_system_information[key] = [{'language': feed_language, 'text': new_system_information[key]}]

        if 'phone_number' in new_system_information:
            configured_phone_number = new_system_information['phone_number']
            if not PHONE_NUMBER_GBFS_V3_PATTERN.match(configured_phone_number):
                new_system_information['phone_number'] = ''.join(
                    [c for c in configured_phone_number if c.isdigit() or c == '+']
                )
                logger.warning(
                    f"phone_number {configured_phone_number} defined in system_information config for feed {system_id} does not match pattern '^\\d+$'. Replaced by '{new_system_information['phone_number']}. Please check!'"
                )

        if 'opening_hours' not in new_system_information:
            logger.warning(
                f'No opening_hours defined in system_information config for feed {system_id}, using 24/7 as default'
            )
            new_system_information['opening_hours'] = OPENING_HOURS_DEFAULT

        if 'privacy_last_updated' not in new_system_information:
            logger.warning(
                f'No privacy_last_updated defined in system_information config for feed {system_id}, using current date'
            )
            new_system_information['privacy_last_updated'] = datetime.utcnow().date().strftime('%Y-%m-%d')

        if 'license_url' in new_system_information and 'license_id' in new_system_information:
            # in case both, license_url and license_id are declared, we keep license_id
            logger.warning(
                f'license_url and license_id provided for feed {system_id}. GBFSv3 allows one of them. Dropping license_url.'
            )
            new_system_information.pop('license_url')

        return new_system_information

    def _convert_to_v3(self, feed_language, elements):
        if not elements:
            return None

        for element in elements:
            for key in ['name', 'description', 'make', 'model', 'summary']:
                if key in element and isinstance(element[key], str):
                    element[key] = [{'language': feed_language, 'text': element[key]}]

            for replacement in [
                {'former': 'bike_id', 'new': 'vehicle_id'},
                {'former': 'num_bikes_available', 'new': 'num_vehicles_available'},
            ]:
                if replacement['former'] in element:
                    element[replacement['new']] = element.pop(replacement['former'])

            if not isinstance(element, dict):
                logger.warning(f'Unexpected additional element: {element}')
            elif isinstance(element.get('last_reported'), int):
                element['last_reported'] = datetime.utcfromtimestamp(element['last_reported']).isoformat()

        return elements

    def write_gbfs_feed(
        self,
        destFolder: str,
        system_information: Dict,
        station_information: Optional[List[Dict]],
        station_status: Optional[List[Dict]],
        vehicle_types: Optional[List[Dict]],
        vehicles: Optional[List[Dict]],
        geofencing_zones: Optional[List[Dict]],
        pricing_plans: Optional[List[Dict]],
        alerts: Optional[List[Dict]],
        base_url: str,
        timestamp: int,
        ttl: int = 60,
    ) -> None:
        system_information_v3 = self._convert_system_information_to_v3(system_information)
        feed_language = system_information_v3['languages'][0]

        super().write_gbfs_feed(
            destFolder,
            system_information_v3,
            self._convert_to_v3(feed_language, station_information),
            self._convert_to_v3(feed_language, station_status),
            self._convert_to_v3(feed_language, vehicle_types),
            self._convert_to_v3(feed_language, vehicles),
            self._convert_to_v3(feed_language, geofencing_zones),
            self._convert_to_v3(feed_language, pricing_plans),
            self._convert_to_v3(feed_language, alerts),
            base_url,
            timestamp,
            ttl,
        )
