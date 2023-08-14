import json
import logging
import os
from argparse import ArgumentParser
from time import sleep

from decouple import config

from x2gbfs.gbfs import BaseProvider, GbfsTransformer, GbfsWriter
from x2gbfs.providers import Deer, FleetsterAPI

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('x2gbfs')


def build_extractor(provider: str) -> BaseProvider:
    if provider == 'deer':
        api_url = config('DEER_API_URL')
        api_user = config('DEER_USER')
        api_password = config('DEER_PASSWORD')

        fleetsterApi = FleetsterAPI(api_url, api_user, api_password)
        extractor = Deer(fleetsterApi)
    else:
        raise ValueError(f'Unkown config {provider}')

    return extractor


def main(providers: list[str], output_dir: str, base_url: str, interval: int = 0) -> None:
    while True:
        for provider in providers:
            generate_feed_for(provider, output_dir, base_url)
        if interval > 0:
            sleep(interval)
        else:
            return


def generate_feed_for(provider: str, output_dir: str, base_url: str) -> None:
    with open(f'config/{provider}.json') as config_file:
        # TODO error handling
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
