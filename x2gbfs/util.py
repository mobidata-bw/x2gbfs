from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional, Tuple

import logging
import requests
from unidecode import unidecode

logger = logging.getLogger(__name__)

GERMAN_UMLAUTS_TRANSLATIONS = str.maketrans({'ä': 'ae', 'Ä': 'Ae', 'ö': 'oe', 'Ö': 'Oe', 'ü': 'ue', 'Ü': 'Ue'})


def unidecode_with_german_umlauts(string: str) -> str:
    """
    Represents non-ascii Unicode string as their closest matching ascii variants.
    As unidecode transliters German umlauts incorrectly (see the FAQ section of https://pypi.org/project/Unidecode/),
    unidecode_with_german_umlauts first replaces them explicitly.
    """
    return unidecode(string.translate(GERMAN_UMLAUTS_TRANSLATIONS))


def timestamp_to_isoformat(utctimestamp: datetime):
    """
    Returns timestamp in isoformat.
    As gbfs-validator currently can't handle numeric +00:00 timezone information, we replace +00:00 by Z
    It's validation expressio is ^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})([A-Z])$
    See also https://github.com/MobilityData/gbfs-json-schema/issues/95
    """
    return utctimestamp.isoformat().replace('+00:00', 'Z')


def get(
    url: str,
    params: Optional[dict[str, str]] = None,
    headers: Optional[dict[str, str]] = None,
    timeout: int = 5,
    user_agent: str = 'x2gbfs +https://github.com/mobidata-bw/',
):
    request_headers = dict(headers) if headers is not None else {}
    request_headers['User-Agent'] = user_agent
    response = requests.get(url, headers=request_headers, timeout=timeout, params=params)
    response.raise_for_status()
    return response

def reverse_multipolygon(geometry):
    if geometry and geometry.get('type')=='MultiPolygon':
        for single_polygon in geometry.get('coordinates',[]):
            for inner_polygon in single_polygon:
                inner_polygon.reverse()
    else:
        logger.exception(f'Geometry is of type {geometry.get("type")}, not MultiPolygon, did not reverse!')
