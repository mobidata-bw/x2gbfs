
# XYZ to GBFS Mapping

This document map XYZ's sharing API to GBFS.

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

This specification describes the mapping of car-sharing provider [XYZ](https://xyz/)'s API to GBFS.


## General Information

This section gives a high level overview of the sharing provider's API and the defined mapping to GBFS.

The providers API documentation is available via a [API documentation](https://xyz/).

## Open Issues or Questions

Open questions are managed as [issues](https://github.com/mobidata-bw/x2gbfs/issues?q=is%3Aissue+is%3Aopen+label%3Axyz). They should be tagged with `xyz`.


## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information is manually extracted from the providers homepage. Only the real configuration in [config/xyz.json](config/xyz.json) is relevant.


### vehicle_types.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*

#### Field Mappings

GBFS Field |
--- |
`vehicle_type_id` |
`form_factor` |
`rider_capacity`|
`cargo_volume_capacity` |
`cargo_load_capacity` |
`propulsion_type` |
`eco_label` |
`max_range_meters` |
`name` |
`vehicle_accessories` |
`g_CO2_km` |
`vehicle_image` |
`make` |
`model` |
`wheel_count` |
`max_permitted_speed` |
`rated_power` |
`default_reserve_time` |
`return_constraint`|
`vehicle_assets`|
`default_pricing_plan_id`|
`pricing_plan_ids`|


### station_information.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*

#### Field Mappings

GBFS Field |
--- |
`station_id` |
`name` |
`short_name` |
`lat` |
`lon` |
`address` |
`cross_street` |
`region_id` |
`post_code` |
`rental_methods` |
`is_virtual_station`|
`station_area` |
`parking_type` |
`parking_hoop` |
`contact_phone` |
`capacity` |
`vehicle_capacity`  |
`vehicle_type_capacity` |
`is_valet_station`  |
`is_charging_station` |
`rental_uris` |


### station_status.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*

#### Field Mappings

GBFS Field |
--- |
`station_id` |
`num_bikes_available` |
`vehicle_types_available` |
`num_bikes_disabled` |
`num_docks_available` |
`vehicle_docks_available` |
`num_docks_disabled` |
`is_installed` |
`is_renting` |
`is_returning` |
`last_reported` |


### free_bike_status.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*

#### Field Mappings

GBFS Field |
--- |
`bike_id` |
`lat` |
`lon` |
`is_reserved` |
`is_disabled` |
`rental_uris` |
`vehicle_type_id` |
`last_reported` |
`current_range_meters` |
`current_fuel_percent` |
`station_id` |
`home_station_id` |
`pricing_plan_id` |
`vehicle_equipment` |
`available_until` |


### system_hours.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*


### system_calendar.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*


### system_regions.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*


### system_pricing_plans.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*


### system_alerts.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*


### geofencing_zones.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*


## Deep Links

*Describe deep links template rules, if any*
