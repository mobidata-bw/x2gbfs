import copy
import json
from datetime import datetime
from pathlib import Path


class GbfsWriter:
    def __init__(self, feed_language='en'):
        self.feed_language = feed_language

    def gbfs_data(self, feed_language, base_url, include_pricing_plans=True):
        feeds = ['system_information', 'station_information', 'station_status', 'free_bike_status', 'vehicle_types']
        if include_pricing_plans:
            feeds.append('system_pricing_plans')

        return {feed_language: {'feeds': [{'name': feed, 'url': f'{base_url}/{feed}.json'} for feed in feeds]}}

    def write_gbfs_file(self, filename, data, timestamp, ttl=60):
        with open(filename, 'w') as dest:
            content = {'data': data, 'last_updated': timestamp, 'ttl': ttl, 'version': '2.3'}
            json.dump(content, dest, indent=2)

    def write_gbfs_feed(self, config, destFolder, info, status, vehicle_types, vehicles, base_url):
        base_url = base_url or config['publication_base_url']
        pricing_plans = config['feed_data'].get('pricing_plans')
        system_information = copy.deepcopy(config['feed_data']['system_information'])

        Path(destFolder).mkdir(parents=True, exist_ok=True)

        timestamp = int(datetime.timestamp(datetime.now()))
        self.write_gbfs_file(destFolder + '/gbfs.json', self.gbfs_data(self.feed_language, base_url), timestamp)
        self.write_gbfs_file(destFolder + '/station_information.json', {'stations': info}, timestamp)
        self.write_gbfs_file(destFolder + '/station_status.json', {'stations': status}, timestamp)
        self.write_gbfs_file(destFolder + '/free_bike_status.json', {'bikes': vehicles}, timestamp)
        self.write_gbfs_file(destFolder + '/system_information.json', system_information, timestamp)
        self.write_gbfs_file(destFolder + '/vehicle_types.json', {'vehicle_types': vehicle_types}, timestamp)
        if pricing_plans:
            self.write_gbfs_file(destFolder + '/system_pricing_plans.json', {'plans': pricing_plans}, timestamp)
