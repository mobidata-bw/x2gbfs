import copy
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GbfsWriter:
    def __init__(self, feed_language: str = 'en'):
        self.feed_language = feed_language

    def gbfs_data(self, feed_language: str, base_url: str, feeds: List[str]) -> Dict:
        return {feed_language: {'feeds': [{'name': feed, 'url': f'{base_url}/{feed}.json'} for feed in feeds]}}

    def write_gbfs_file(self, filename: str, data, timestamp: int, ttl: int = 60) -> None:
        with open(filename, 'w') as dest:
            content = {'data': data, 'last_updated': timestamp, 'ttl': ttl, 'version': '2.3'}
            json.dump(content, dest, indent=2)

    def write_gbfs_feed(
        self,
        config: Dict,
        destFolder: str,
        station_information: Optional[List[Dict]],
        station_status: Optional[List[Dict]],
        vehicle_types: Optional[List[Dict]],
        vehicles: Optional[List[Dict]],
        base_url: str,
    ) -> None:
        base_url = base_url or config['publication_base_url']
        pricing_plans = config['feed_data'].get('pricing_plans')
        system_information = copy.deepcopy(config['feed_data']['system_information'])

        Path(destFolder).mkdir(parents=True, exist_ok=True)

        timestamp = int(datetime.timestamp(datetime.now()))
        feeds = ['system_information']
        self.write_gbfs_file(destFolder + '/system_information.json', system_information, timestamp)
        if station_information and station_status:
            feeds.extend(('station_information', 'station_status'))
            self.write_gbfs_file(destFolder + '/station_information.json', {'stations': station_information}, timestamp)
            self.write_gbfs_file(destFolder + '/station_status.json', {'stations': station_status}, timestamp)
        elif station_information or station_status:
            logger.error(
                f'For feed {system_information["system_id"]}, only one of station_information or station_status was returned. Skipping station generation.'
            )
        else:
            logger.debug(
                f'Got no station info for feed {system_information["system_id"]}, generating free floating infos only'
            )
        if vehicles:
            feeds.append('free_bike_status')
            self.write_gbfs_file(destFolder + '/free_bike_status.json', {'bikes': vehicles}, timestamp)
        if vehicle_types:
            feeds.append('vehicle_types')
            self.write_gbfs_file(destFolder + '/vehicle_types.json', {'vehicle_types': vehicle_types}, timestamp)
        if pricing_plans:
            feeds.append('system_pricing_plans')
            self.write_gbfs_file(destFolder + '/system_pricing_plans.json', {'plans': pricing_plans}, timestamp)
        self.write_gbfs_file(destFolder + '/gbfs.json', self.gbfs_data(self.feed_language, base_url, feeds), timestamp)
