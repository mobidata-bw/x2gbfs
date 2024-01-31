from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional, Tuple

import requests


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
    return requests.get(url, headers=request_headers, timeout=timeout, params=params)
