from datetime import datetime, timezone


def timestamp_to_isoformat(utctimestamp: datetime):
    """
    Returns timestamp in isoformat.
    As gbfs-validator currently can't handle numeric +00:00 timezone information, we replace +00:00 by Z
    It's validation expressio is ^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})([A-Z])$
    See also https://github.com/MobilityData/gbfs-json-schema/issues/95
    """
    return utctimestamp.isoformat().replace('+00:00', 'Z')
