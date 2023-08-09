import json
import logging
import os
from argparse import ArgumentParser

from decouple import config

from x2gbfs.gbfs import GbfsTransformer, GbfsWriter
from x2gbfs.providers import Deer, FleetsterAPI

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('x2gbfs')


def build_extractor(provider):
    if provider == 'deer':
        api_url = config('DEER_API_URL')
        api_user = config('DEER_USER')
        api_password = config('DEER_PASSWORD')

        fleetsterApi = FleetsterAPI(api_url, api_user, api_password)
        extractor = Deer(fleetsterApi)
    else:
        raise OSError(f'Unkown config {provider}')

    return extractor


def main(args) -> None:
    provider = args.provider
    with open(f'config/{provider}.json') as config_file:
        # TODO error handling
        feed_config = json.load(config_file)

    transformer = GbfsTransformer()
    extractor = build_extractor(provider)
    destFolder = args.outputDir

    (info, status, vehicle_types, vehicles) = transformer.load_stations_and_vehicles(extractor)
    GbfsWriter().write_gbfs_feed(feed_config, destFolder, info, status, vehicle_types, vehicles, args.baseUrl)
    logger.info(f'Updated feeds for {provider}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-o', '--outputDir', help='output directory the transformed files are written to', default='out'
    )
    parser.add_argument('-p', '--provider', required=True, help='service provider')
    parser.add_argument('-b', '--baseUrl', required=False, help='baseUrl this feed will be published under')

    args = parser.parse_args()

    main(args)
