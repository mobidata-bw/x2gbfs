# EUROPEAN UNION PUBLIC LICENCE v. 1.2
# EUPL © the European Union 2007, 2016

from unittest.mock import MagicMock

from x2gbfs.gbfs.gbfs_writer import GbfsV3Writer

system_information_v2 = {
    'system_id': 'any_id',
    'language': 'de',
    'privacy_last_updated': '2025-01-01',
    'name': 'any_name',
    'phone_number': '+49 123 456',
    'license_url': 'any_url',
    'license_id': 'any_id',
}

system_information_v3 = {
    'system_id': 'any_id',
    'languages': ['de'],
    'name': [{'language': 'de', 'text': 'any_name'}],
    'license_id': 'any_id',
    'phone_number': '+49123456',
    'opening_hours': '24/7',
    'privacy_last_updated': '2025-01-01',
}


def test_system_information_v2_is_transformed_to_v3():
    writer = GbfsV3Writer()
    writer._dump_json = MagicMock(return_value=None)

    writer.write_gbfs_feed('none', system_information_v2, None, None, None, None, None, None, None, None, 0)

    writer._dump_json.assert_any_call(
        'none/gbfs.json',
        {
            'data': {'feeds': [{'name': 'system_information', 'url': 'None/system_information.json'}]},
            'last_updated': '1970-01-01T00:00:00+00:00',
            'ttl': 60,
            'version': '3.0',
        },
    )
    writer._dump_json.assert_any_call(
        'none/system_information.json',
        {
            'data': {
                'system_id': 'any_id',
                'languages': ['de'],
                'name': [{'language': 'de', 'text': 'any_name'}],
                'license_id': 'any_id',
                'phone_number': '+49123456',
                'opening_hours': '24/7',
                'privacy_last_updated': '2025-01-01',
            },
            'last_updated': '1970-01-01T00:00:00+00:00',
            'ttl': 60,
            'version': '3.0',
        },
    )


def test_system_information_v3_is_unchanged():
    writer = GbfsV3Writer()
    writer._dump_json = MagicMock(return_value=None)

    writer.write_gbfs_feed('none', system_information_v3, None, None, None, None, None, None, None, None, 0)

    writer._dump_json.assert_any_call(
        'none/gbfs.json',
        {
            'data': {'feeds': [{'name': 'system_information', 'url': 'None/system_information.json'}]},
            'last_updated': '1970-01-01T00:00:00+00:00',
            'ttl': 60,
            'version': '3.0',
        },
    )
    writer._dump_json.assert_any_call(
        'none/system_information.json',
        {
            'data': {
                'system_id': 'any_id',
                'languages': ['de'],
                'name': [{'language': 'de', 'text': 'any_name'}],
                'license_id': 'any_id',
                'phone_number': '+49123456',
                'opening_hours': '24/7',
                'privacy_last_updated': '2025-01-01',
            },
            'last_updated': '1970-01-01T00:00:00+00:00',
            'ttl': 60,
            'version': '3.0',
        },
    )


def test_station_status_v2_is_transformed_to_v3():
    writer = GbfsV3Writer()
    writer._dump_json = MagicMock(return_value=None)

    station_information_v2 = [
        {
            'station_id': 'any_station_id',
        }
    ]

    station_status_v2 = [{'station_id': 'any_station_id', 'last_reported': 1765108648}]
    writer.write_gbfs_feed(
        'none', system_information_v2, station_information_v2, station_status_v2, None, None, None, None, None, None, 0
    )

    writer._dump_json.assert_any_call(
        'none/station_status.json',
        {
            'data': {
                'stations': [
                    {'station_id': 'any_station_id', 'last_reported': '2025-12-07T11:57:28+00:00'},
                ]
            },
            'last_updated': '1970-01-01T00:00:00+00:00',
            'ttl': 60,
            'version': '3.0',
        },
    )


def test_station_status_v3_is_unchanged():
    writer = GbfsV3Writer()
    writer._dump_json = MagicMock(return_value=None)

    station_information_v3 = [
        {
            'station_id': 'any_station_id',
        }
    ]

    station_status_v3 = [{'station_id': 'any_station_id', 'last_reported': '2025-12-07T11:57:28+00:00'}]

    writer.write_gbfs_feed(
        'none', system_information_v3, station_information_v3, station_status_v3, None, None, None, None, None, None, 0
    )

    writer._dump_json.assert_any_call(
        'none/station_status.json',
        {
            'data': {
                'stations': [
                    {'station_id': 'any_station_id', 'last_reported': '2025-12-07T11:57:28+00:00'},
                ]
            },
            'last_updated': '1970-01-01T00:00:00+00:00',
            'ttl': 60,
            'version': '3.0',
        },
    )
