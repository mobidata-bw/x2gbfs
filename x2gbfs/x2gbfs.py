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
from x2gbfs.providers import (
    CantamenIXSIProvider,
    Deer,
    ExampleProvider,
    FleetsterAPI,
    FlinksterProvider,
    LastenVeloFreiburgProvider,
    MoqoProvider,
    NoiProvider,
    VoiRaumobil,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('x2gbfs')


def build_extractor(provider: str, feed_config: Dict[str, Any]) -> BaseProvider:
    if provider == 'example':
        return ExampleProvider()
    if provider == 'lastenvelo_fr':
        return LastenVeloFreiburgProvider()
    if provider == 'deer':
        api_url = config('DEER_API_URL')
        api_user = config('DEER_USER')
        api_password = config('DEER_PASSWORD')

        fleetsterApi = FleetsterAPI(api_url, api_user, api_password)
        return Deer(fleetsterApi)
    if provider == 'voi-raumobil':
        api_url = config('VOI_API_URL')
        api_user = config('VOI_USER')
        api_password = config('VOI_PASSWORD')

        return VoiRaumobil(api_url, api_user, api_password)
    if provider in ['my-e-car', 'oekostadt_renningen'] or provider.startswith('stadtmobil_') or provider.startswith('teilauto_'):
        return CantamenIXSIProvider(feed_config)
    if provider in ['stadtwerk_tauberfranken', 'zeag_energie']:
        return MoqoProvider(feed_config)
    if provider in ['noi']:
        return NoiProvider()
    if provider in ['flinkster']:
        return FlinksterProvider(feed_config)

    raise ValueError(f'Unknown config {provider}')


def main(providers: List[str], output_dir: str, base_url: str, interval: int = 0) -> None:
    should_loop_infinetly = interval > 0
    error_occured = False

    while True:
        for provider in providers:
            try:
                generate_feed_for(provider, output_dir, base_url)
            except TimeoutError:
                logger.error(f'Generating feed for {provider} failed due to timeout error!')
                error_occured = True
            except Exception:
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
    extractor = build_extractor(provider, feed_config)

    (info, status, vehicle_types, vehicles, last_reported) = transformer.load_stations_and_vehicles(extractor)
    GbfsWriter().write_gbfs_feed(
        feed_config,
        f'{output_dir}/{provider}',
        info,
        status,
        vehicle_types,
        vehicles,
        f'{base_url}/{provider}',
        last_reported,
        ttl=feed_config.get('ttl', 60),
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
