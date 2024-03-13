# MOQO to GBFS Mapping

This document map MOQO's sharing API to GBFS.

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

This specification describes the mapping of MOQO's API to GBFS.


## General Information

This section gives a high level overview of the sharing provider's API and the defined mapping to GBFS.

Official API documentation is access restricted, hence not included.

Examples from th


## Open Issues or Questions

Open questions are managed as [issues](https://github.com/mobidata-bw/x2gbfs/issues?q=is%3Aissue+is%3Aopen+label%moqo). They should be tagged with `moqo`.


## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information is manually extracted from the providers homepage. Only the real configuration in e.g. [config/stadtwerk-tauberfranken.json](../../config/stadtwerk-tauberfranken.json) is relevant.


### vehicle_types.json

Vehicle Types, vehicles are extracted from the `cars` endpoint, extracting this from the returned cars.


#### Field Mappings

GBFS Field | Mapping
--- | ---
`vehicle_type_id` |  lowercased `row['car_model_name']`, spaces transformed in underscore
`form_factor` | `row['vehicle_type']` mapped to GBFS vehicle types.
`rider_capacity`| -
`cargo_volume_capacity` | -
`cargo_load_capacity` | -
`propulsion_type` | `row['fuel_type']` mapped to GBFS vehicle types.
`eco_label` | -
`max_range_meters` | Not availabe via API, set to `250.000`
`name` | `row['car_model_name']`
`g_CO2_km` | -
`vehicle_image` | -
`make` | first word of `row['car_model_name']`
`model` | all words after the first word of `row['car_model_name']`
`wheel_count` | -
`max_permitted_speed` | -
`rated_power` | -
`default_reserve_time` | -
`return_constraint`| `roundtrip`
`vehicle_assets`| -
`default_pricing_plan_id`| `tarif` (current provided only has one pricing plan, might be overwritten in subclasses)
`pricing_plan_ids`| -


### station_information.json

Station information is extracted from `parkings` endpoint.


#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `row['id']`
`name` | `row['name']`
`short_name` | -
`lat` | `row['center']['lat']`
`lon` | `row['center']['lon']`
`address` | `row['town'] + ', ' + row['street'] + ' ' + row['street_number']`
`cross_street` | -
`region_id` | -
`post_code` |  `row['zipcode']`
`rental_methods` |`['key']`
`is_virtual_station`| -
`station_area` | -
`parking_type` | -
`parking_hoop` | -
`contact_phone` | -
`capacity` | `row['capacity_max']`
`vehicle_capacity`  |  -
`vehicle_type_capacity` | _deduced from vehicles assigned to this station free_bike_status.station_id_
`is_valet_station`  | -
`is_charging_station` |  -
`rental_uris` | -


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

Free vehicles are extracted from `cars` endpoint. As currently unavailable cars have no `latest_parking` set, we filter them out. We request availablity status as being available in the next 3 hours.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`bike_id` | `row['id']`
`lat` | - Vehicles are at station, so we don't provide coords
`lon` | - Vehicles are at station, so we don't provide coords
`is_reserved` | `row['available'] is not True`
`is_disabled` | -
`rental_uris` | -
`vehicle_type_id` | see section vehicle_types
`last_reported` | curent time
`license_plate`: `row['license'].split('|')[0].strip()` (at least Stadtwerk Tauberfranken seems to append station name after the license plate)
`current_range_meters` | `vehicle_type['max_rang_meters'] * vehicle['fuel_level'] / 100.0`
`current_fuel_percent` | `vehicle['fuel_level'] / 100.0`
`station_id` | `row['laatest_parking']['id']`, if set
`home_station_id` | -
`pricing_plan_id` | -
`vehicle_equipment` | -
`available_until` | - (API does not provide this information explicitly)


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

Deep links seem not to be available for vehicles yet.
