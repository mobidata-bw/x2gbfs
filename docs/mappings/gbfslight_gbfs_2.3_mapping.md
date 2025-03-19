# GBFS-Light to GBFS Mapping

This document maps "[GBFS-Light](https://oda-8059lnsdc-jens-ochsenmeiers-projects.vercel.app/schema/gbfs-light)" format intended for simple static feeds to GBFS.
Credits to Jens Ochsenmeier for suggesting this simplyfied version, which can be
generated from a simple CSV table easily maintainable by responsible parties.


# Reference version

This documentation refers to **[v2.3](https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md)**.

## Table of Contents

* [Introduction](#introduction)
* [General Information](#general-information)
* [Open Issues or Questions](#open-issues-or-questions)
* [Files](#files)
    * [gbfs.json](#gbfsjson)
    * [gbfs_versions.json](#gbfs_versionsjson) *(added in v1.1)*
    * [system_information.json](#system_informationjson)
    * [vehicle_types.json](#vehicle_typesjson) *(added in v2.1)*
    * [station_information.json](#station_informationjson)
    * [station_status.json](#station_statusjson)
    * [free_bike_status.json](#free_bike_statusjson)
    * [system_hours.json](#system_hoursjson)
    * [system_calendar.json](#system_calendarjson)
    * [system_regions.json](#system_regionsjson)
    * [system_pricing_plans.json](#system_pricing_plansjson)
    * [system_alerts.json](#system_alertsjson)
    * [geofencing_zones.json](#geofencing_zonesjson) *(added in v2.1)*

## Introduction

This specification describes the mapping of "GBFS-Light" format to GBFS.


## General Information

This section gives a high level overview of the "GBFS-Light" format and the defined mapping to GBFS.

The GBFS-Light endpoint returns a JSON file. It provides a `system` property which lists all available systems. For a single system entry, this mapping describes how it is mapped to a complete GBFS feed.

## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFS v2.3 supported.

### system_information.json

System information is provided via GBFS-Light and augmented by statically defined defaults from the feed_config (e.g. [config/herrenberg_stadtrad.json](../../config/herrenberg_stadtrad.json).
The following properties are copied from the gbfs light system, if provided:

* attribution_organization_name
* attribution_url
* feed_contact_email
* opening_hours
* language
* license_id
* license_url
* name
* email
* operator
* phone_number
* privacy_last_updated
* privacy_url
* purchase_url
* terms_last_updated
* terms_url
* timezone
* url


### vehicle_types.json

Vehicle Types are extracted from the `system/vehicle_types` section:


#### Field Mappings

GBFS Field | Mapping
--- | ---
`vehicle_type_id` |  Normalized vehicle_type name.
`form_factor` | `vehicle_type['form_factor']`
`rider_capacity`| -
`cargo_volume_capacity` | -
`cargo_load_capacity` | -
`propulsion_type` | `vehicle_type['propulsion_type']`.
`eco_label` | -
`max_range_meters` | `vehicle_type['max_range_meters']`, or `20000` if unset.
`name` | `vehicle_type['name']`
`g_CO2_km` | -
`vehicle_image` | -
`make` | -
`model` | -
`wheel_count` | -
`max_permitted_speed` | -
`rated_power` | -
`default_reserve_time` | -
`return_constraint`| `roundtrip_station`
`vehicle_assets`| -
`default_pricing_plan_id`| -
`pricing_plan_ids`| -


### station_information.json

Station information is extracted from `system/stations` section.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `station['id']`
`name` | `station['name']`
`short_name` | -
`lat` | `station['lat']`
`lon` | `station['lon']`
`address` | `station['address']`
`cross_street` | -
`region_id` | -
`post_code` |  `station['post_code']`
`city` |  `station['city']` Note: `city` will be introduced with GBFS v3.1, we publish it nevertheless already with GBFSv2.3
`rental_methods` | -
`is_virtual_station`| -
`station_area` | -
`parking_type` | -
`parking_hoop` | -
`contact_phone` | -
`capacity` | `station['capacity']`
`vehicle_capacity`  |  -
`vehicle_type_capacity` | for every vehicle type listed in `station['vehicle_types']` an entry with key corresponding to normalized vehicle type name and `station['vehicle_types'][n][available]`
`is_valet_station`  | -
`is_charging_station` |  -
`rental_uris` | for web, `station['url']`, if provided



### station_status.json

Station information is extracted from `system/stations` section.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `station['id']`
`num_bikes_available` | sum of all `station["vehicle_types"]["available_count"]`
`vehicle_types_available` | Per `station["vehicle_types"]`: `station["vehicle_types"]["available_count"]`, `vehicle_type_id` corresponds to normalised vehicle typr name, see `vehicle_types.json` above
`num_docks_available` | -
`vehicle_docks_available` | -
`num_docks_disabled` | -
`is_installed` | `True`
`is_renting` | `True`
`is_returning` | `True`
`last_reported` | timestamp of now()


### free_bike_status.json

Feed is static, no free_bike_status is generated.

### system_hours.json

None.

### system_calendar.json

None.

### system_regions.json

None.

### system_pricing_plans.json

None.

### system_alerts.json

As defined in feed_config.

### geofencing_zones.json

None.

## Deep Links

None.
