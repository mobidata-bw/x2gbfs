
# LastenVelo Freiburg to GBFS Mapping

This document map LastenVelo Freiburg's sharing API to GBFS.

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

This specification describes the mapping of cargo bike-sharing provider [LastenVelo Freiburg](https://www.lastenvelofreiburg.de/)'s API to GBFS.


## General Information

This section gives a high level overview of the sharing provider's API and the defined mapping to GBFS.

No official API documentation exists.

The API is a kind of csv table, but returned as html page.
Line breaks are written as HTML-br-tags, column headers don't match exactly the returned columns and need to be fixed.

We transform the header row from:

`UTC Timestamp,Human readable Timestamp,BikeID,lattitude of station,longitude of station,rental state (available, rented or defect),name of bike,further information`

to
`UTC Timestamp,Human readable Timestamp,BikeID,lat,lon,rental_state,name of bike,further information,url`

## Open Issues or Questions

Open questions are managed as [issues](https://github.com/mobidata-bw/x2gbfs/issues?q=is%3Aissue+is%3Aopen+label%3Alastenvelo_fr). They should be tagged with `lastenvelo_fr`.


## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information is manually extracted from the providers homepage. Only the real configuration in [config/lastenvelo_fr.json](config/lastenvelo_fr.json) is relevant.


### vehicle_types.json

Vehicle Types, vehicles, and station information are all extracted from https://www.lastenvelofreiburg.de/LVF_usage.html. As no brand/model nformation is available, we treat every row as a new vehicle type.


#### Field Mappings

GBFS Field | Mapping
--- | ---
`vehicle_type_id` | normalized `row[name of bike]`
`form_factor` | `cargo_bicycle`. Note: some of the vehicles are bikes with a cargo trailer, but we handle them as `cargo_bicycle` anyway.
`rider_capacity`| 2 if 'Kindertransport' in `row[further information]` else 1.
`cargo_volume_capacity` | -
`cargo_load_capacity` | -
`propulsion_type` | `electric_assist` if 'mit Motor' in `row[further information]` else `human`
`eco_label` | -
`max_range_meters` | `20.000`
`name` | `row['name of bike']`
`vehicle_accessories` | -
`g_CO2_km` | -
`vehicle_image` | -
`make` | -
`model` | -
`wheel_count` | `3 if '3-rädrig' in row[further information] else 2`
`max_permitted_speed` | -
`rated_power` | -
`default_reserve_time` | -
`return_constraint`| `roundtrip`
`vehicle_assets`| -
`default_pricing_plan_id`| `kostenfrei`
`pricing_plan_ids`| -


### station_information.json

Vehicle Types, vehicles, and station information are all extracted from https://www.lastenvelofreiburg.de/LVF_usage.html. As no station name is provided, we treat rows with the same coords as one location.


#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `row['lon']_row['lat']`
`name` | `row['name of bike']` Note: no station name is given, so we use the vehicle's name, which sometimes contains the stations name.
`short_name` | -
`lat` | `row['lat']`
`lon` | `row['lon']`
`address` | -
`cross_street` | -
`region_id` | -
`post_code` | -
`rental_methods` |`['key']`
`is_virtual_station`| -
`station_area` | -
`parking_type` | -
`parking_hoop` | -
`contact_phone` | -
`capacity` | -
`vehicle_capacity`  | -
`vehicle_type_capacity` | -
`is_valet_station`  | -
`is_charging_station` |  `not ('ohne Ladestation' in row['further information'])`
`rental_uris` | `row['url']`


### station_status.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `row['lon']_row['lat']`
`num_bikes_available` | _deduced by x2gbfs from free_bike_status.station_id_
`vehicle_types_available` | _deduced by x2gbfs from free_bike_status.station_id_
`num_docks_available` | -
`vehicle_docks_available` | -
`num_docks_disabled` | -
`is_installed` | `True`
`is_renting` | `True` (Note: the API does not return opening hours information yet)
`is_returning` | `True` (Note: the API does not return opening hours information yet)
`last_reported` | `row['UTC Timestamp']`


### free_bike_status.json

*Describe endpoint from which information is extracted and potential filter rules to be applied*

#### Field Mappings

GBFS Field | Mapping
--- | ---
`bike_id` | `row['BikeID']`
`lat` | - Bikes are at station, so we don't provide coords
`lon` | - Bikes are at station, so we don't provide coords
`is_reserved` | `rented` in `row['rental_state']`
`is_disabled` | `defect` in `row['rental_state']`
`rental_uris` | `row['url']`
`vehicle_type_id` |
`last_reported` | `row['UTC Timestamp']`
`current_range_meters` | `20.000`. API does not provide any information yet
`current_fuel_percent` | -
`station_id` | `row['lon']_row['lat']`
`home_station_id` | `row['lon']_row['lat']`
`pricing_plan_id` | -
`vehicle_equipment` | -
`available_until` | API does not provide any information yet


### system_hours.json

No endpoint.

### system_calendar.json

No endpoint.

### system_regions.json

No endpoint.

### system_pricing_plans.json

No endpoint. Manually de

### system_alerts.json

No endpoint.

### geofencing_zones.json

No endpoint.

## Deep Links

Deep links are available for vehicles only. As usually only on (type of) vehicles is available at one station, we use the first's vehicle's url as station url, too.
