import copy
import json
import logging
import os
import warnings
from argparse import ArgumentParser
from random import random
from time import sleep
from typing import Any, Dict, List

from decouple import config
from requests.exceptions import HTTPError

from x2gbfs.gbfs import BaseProvider, GbfsTransformer, GbfsWriter
from x2gbfs.providers import (
    CambioProvider,
    CantamenIXSIProvider,
    Deer,
    ExampleProvider,
    FleetsterAPI,
    Free2moveAPI,
    Free2moveProvider,
    GbfsLightProvider,
    LaraToGoProvider,
    LastenVeloFreiburgProvider,
    MoqoProvider,
    OpenDataHubProvider,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('x2gbfs')

X2GBFS_DEFAULT_CONFIG = {
    # Default ttl for every gbfs file.
    # Might be overriden for static feeds that are expected to change less frequently.
    'ttl': 60,
    # Should this feed's gbfs.json use a custom base URL? If true, param `customBaseUrl`
    # must be provided on startup and will be used as feed base url instead of `baseUrl`
    'useCustomBaseUrl': False,
}


def build_extractor(provider: str, feed_config: Dict[str, Any]) -> BaseProvider:
    if provider == 'example':
        return ExampleProvider(feed_config)
    if provider == 'lastenvelo_fr':
        return LastenVeloFreiburgProvider(feed_config)
    if provider == 'deer':
        api_url = config('DEER_API_URL')
        api_user = config('DEER_USER')
        api_password = config('DEER_PASSWORD')

        fleetsterApi = FleetsterAPI(api_url, api_user, api_password)
        return Deer(feed_config, fleetsterApi)
    if provider.startswith('cambio_'):
        return CambioProvider(feed_config)
    if (
        provider in ['naturenergie_sharing', 'oekostadt_renningen', 'gruene-flotte_freiburg', 'swu2go']
        or provider.startswith('stadtmobil_')
        or provider.startswith('teilauto_')
    ):
        return CantamenIXSIProvider(feed_config)
    if provider in [
        'stadtwerk_tauberfranken',
        'flinkster_carsharing',
        'oberschwabenmobil',
        'gmuend_bewegt',
        'coono',
    ]:
        return MoqoProvider(feed_config)
    if provider == 'lara_to_go':
        return LaraToGoProvider(feed_config)
    if provider in ['opendatahub']:
        return OpenDataHubProvider(feed_config)
    if provider.startswith('free2move_'):
        return Free2moveProvider(feed_config, Free2moveAPI())
    if feed_config.get('x2gbfs', {}).get('provider') == 'gbfs-light':
        return GbfsLightProvider(feed_config)

    raise ValueError(f'Unknown config {provider}')


def main(providers: List[str], output_dir: str, base_url: str, custom_base_url: str | None, interval: int = 0) -> None:
    should_loop_infinetly = interval > 0
    error_occured = False

    while True:
        for provider in providers:
            try:
                generate_feed_for(provider, output_dir, base_url, custom_base_url)
            except HTTPError as err:
                logger.error(
                    f'Generating feed for {provider} failed due to HTTP error {err.response.status_code} for url {err.request.url}'
                )
                error_occured = True
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


def get_x2gbfs_config_value(feed_config, key):
    """
    Returns x2gbfs config value, which can be overritten per feed via a x2gbfs section
    in feed config.
    """
    if key in feed_config:
        warnings.warn(
            'Defining x2gbfs config parametes at top level is deprecated. Define them in section "x2gbfs" instead ',
            category=DeprecationWarning,
            stacklevel=2,
        )
        return feed_config.get(key)
    return feed_config.get('x2gbfs', {}).get(key, X2GBFS_DEFAULT_CONFIG.get(key))


def generate_feed_for(provider: str, output_dir: str, base_url: str, custom_base_url: str | None) -> None:
    with open(f'config/{provider}.json') as config_file:
        feed_config = json.load(config_file)

    transformer = GbfsTransformer()
    extractor = build_extractor(provider, feed_config)

    (info, status, vehicle_types, vehicles, geofencing_zones, last_reported) = transformer.load_stations_and_vehicles(
        extractor
    )

    is_feed_protected = get_x2gbfs_config_value(feed_config, 'useCustomBaseUrl')
    if is_feed_protected:
        if custom_base_url is None:
            raise ValueError(f'Config {provider} declared useCustomBaseUrl=true, but customBaseUrl is undefined')
        feed_base_url = f'{custom_base_url}/{provider}'
    else:
        feed_base_url = f'{base_url}/{provider}'

    system_information = transformer.load_system_information(extractor)
    pricing_plans = transformer.load_pricing_plans(extractor)
    alerts = transformer.load_alerts(extractor)

    GbfsWriter().write_gbfs_feed(
        f'{output_dir}/{provider}',
        system_information,
        info,
        status,
        vehicle_types,
        vehicles,
        geofencing_zones,
        pricing_plans,
        alerts,
        feed_base_url,
        last_reported,
        ttl=get_x2gbfs_config_value(feed_config, 'ttl'),
    )
    logger.info(f'Updated feeds for {provider}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-o', '--outputDir', help='output directory the transformed files are written to', default='out'
    )
    parser.add_argument('-p', '--providers', required=True, help='service provider(s), comma-separated')
    parser.add_argument(
        '-b',
        '--baseUrl',
        required=True,
        help='baseUrl this/these feed(s) will be published under (if not flagged protected in config)',
    )
    parser.add_argument(
        '-c',
        '--customBaseUrl',
        required=False,
        help='custom baseUrl this/these feed(s) will be published under, if config declares `x2gbfs/useCustomBaseUrl: true`',
    )
    parser.add_argument(
        '-i',
        '--interval',
        required=False,
        help='if provided, feeds will be updated every interval seconds. 0 means feeds are only genereated once',
        default=0,
        type=int,
    )

    args = parser.parse_args()

    main(args.providers.split(','), args.outputDir, args.baseUrl, args.customBaseUrl, args.interval)
