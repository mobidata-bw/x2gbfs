import json
import logging
import os
from argparse import ArgumentParser
from random import random
from time import sleep
from typing import Any, Dict, List

from decouple import config
from requests.exceptions import HTTPError

from x2gbfs.gbfs import BaseProvider, GbfsTransformer, GbfsWriter
from x2gbfs.providers import Deer, ExampleProvider, FleetsterAPI

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('x2gbfs')


def build_extractor(provider: str) -> BaseProvider:
    if provider == 'example':
        return ExampleProvider()
    if provider == 'deer':
        api_url = config('DEER_API_URL')
        api_user = config('DEER_USER')
        api_password = config('DEER_PASSWORD')

        fleetsterApi = FleetsterAPI(api_url, api_user, api_password)
        return Deer(fleetsterApi)

    raise ValueError(f'Unkown config {provider}')


def main(providers: List[str], output_dir: str, base_url: str, interval: int = 0) -> None:
    should_loop_infinetly = interval > 0
    error_occured = False

    while True:
        for provider in providers:
            try:
                generate_feed_for(provider, output_dir, base_url)
            except HTTPError:
                logger.exception(f'Generating feed for {provider} failed!')
                error_occured = True

        if should_loop_infinetly:
            sleep(interval + random() * interval / 10)  # noqa: S311 (no cryptographic purpose)
        else:
            # In case an error occured, we terminate with exit code 1
            exit(error_occured)


def generate_feed_for(provider: str, output_dir: str, base_url: str) -> None:
    with open(f'config/{provider}.json') as config_file:
        feed_config = json.load(config_file)

    transformer = GbfsTransformer()
    extractor = build_extractor(provider)

    (info, status, vehicle_types, vehicles) = transformer.load_stations_and_vehicles(extractor)
    GbfsWriter().write_gbfs_feed(
        feed_config, f'{output_dir}/{provider}', info, status, vehicle_types, vehicles, f'{base_url}/{provider}'
    )
    logger.info(f'Updated feeds for {provider}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-o', '--outputDir', help='output directory the transformed files are written to', default='out'
    )
    parser.add_argument('-p', '--providers', required=True, help='service provider(s), comma-separated')
    parser.add_argument('-b', '--baseUrl', required=True, help='baseUrl this/these feed(s) will be published under')
    parser.add_argument(
        '-i',
        '--interval',
        required=False,
        help='if provided, feeds will be updated every interval seconds. 0 means feeds are only genereated once',
        default=0,
        type=int,
    )

    args = parser.parse_args()

    main(args.providers.split(','), args.outputDir, args.baseUrl, args.interval)
