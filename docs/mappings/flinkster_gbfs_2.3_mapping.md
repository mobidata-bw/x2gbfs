
# Flinkster to GBFS Mapping

This document maps the Flinkster API to GBFS.

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

This specification describes the mapping of car-sharing provider [Flinkster](https://www.flinkster.de/)'s API to GBFS.


## General Information

This section gives a high level overview of the sharing provider's API and the defined mapping to GBFS.

The Deutsche Bahn Connect Customer B2B API is available via a [API documentation](https://dbconnect-b2b-prod.service.dbrent.net/customer-b2b-api/docs/customer-b2b-api.html).


## Open Issues or Questions

Open questions are managed as [issues](https://github.com/mobidata-bw/x2gbfs/issues?q=is%3Aissue+is%3Aopen+label%3Aflinkster). They should be tagged with `flinkster`.


## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information is manually extracted from the providers homepage. Only the real configuration in [config/flinkster.json](config/flinkster.json) is relevant.


### vehicle_types.json

Flinkster API has no explicit endpoint for vehicle types, so they need to be collected from the `/availableRentalObjects` endpoint.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`vehicle_type_id` | uncapitalized, normalized `rentalObject['name']` (not only make and model, as name provides additional infos like number of doors or capacity)
`form_factor` | `car`
`rider_capacity`| Extracted from rentalObject['name'] if `X-Sitzer` or `X Sitze` are contained.
`cargo_volume_capacity` | -
`cargo_load_capacity` | -
`propulsion_type` | rentalObject['fuelType']<br /><ul><li>`electric => electric`</li><li>`petrol => combustion`</li><li>`diesel => combustion_diesel`</li><li>`multifuel => combustion`</li><li>`hybrid => hybrid`</li></ul>
`eco_label` | -
`max_range_meters` | Not provided by Flinkster. Set to `200000` for all vehicle types (200km)
`name` | `vehicle_type['make'] + ' ' + vehicle_type['model']`
`vehicle_accessories` | doors_X if rentalObject['name'] contains `X-türig` or `X türig` <br/> `navigation` if rentalObject['categoryName'] does not contain `ohne Navi`
`g_CO2_km` | -
`vehicle_image` | -
`make` | Extracted from rentalObject['name']
`model` | Extracted from rentalObject['name']
`wheel_count` | 4
`max_permitted_speed` | -
`rated_power` | -
`default_reserve_time` | -
`return_constraint`| `roundtrip_station`
`vehicle_assets`| -
`default_pricing_plan_id`| <ul><li>`mini_hour` if rentalObject['categoryID'] == 1000</li><li>`small_hour` if rentalObject['categoryID'] == 1001</li><li>`compact_hour` if rentalObject['categoryID'] == 1002</li><li>`medium_hour` if rentalObject['categoryID'] == 1003</li><li>`transporter_hour` if rentalObject['categoryID'] == 1004</li></ul>
`pricing_plan_ids`| <ul><li>`[mini_hour, mini_day]` if rentalObject['categoryID'] == 1000</li><li>`[small_hour, small_day]` if rentalObject['categoryID'] == 1001</li><li>`[compact_hour, compact_day]` if rentalObject['categoryID'] == 1002</li><li>`[medium_hour, medium_day]` if rentalObject['categoryID'] == 1003</li><li>`[transporter_hour, transporter_day]` if rentalObject['categoryID'] == 1004</li></ul>


### station_information.json

Returns all stations of `/areas` endpoint.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `area['uid']`
`name` | `area['name']`
`short_name` | -
`lat` | `area['geometry']['position']['coordinates'][1]`
`lon` | `area['geometry']['position']['coordinates'][0]`
`address` | `area['address']['street'] + ' ' + area['address']['number']`
`cross_street` | -
`region_id` | -
`post_code` | `area['address']['zip']`, if present
`rental_methods` | `key`
`is_virtual_station`| -
`station_area` | -
`parking_type` | -
`parking_hoop` | -
`contact_phone` | -
`capacity` | -
`vehicle_capacity`  | -
`vehicle_type_capacity` | -
`is_valet_station`  | -
`is_charging_station` | -
`rental_uris` | -
`web` | -


### station_status.json

Returns all stations of `/areas` endpoint.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `area['uid']`
`num_bikes_available` | no need to provide, will be deduced from `x2gbfs` via vehicles' stationIds and availability
`vehicle_types_available` | no need to provide, will be deduced from `x2gbfs` via vehicles' stationIds and availability
`num_bikes_disabled` | -
`num_docks_available` | -
`vehicle_docks_available` | -
`num_docks_disabled` | -
`is_installed` | `true`
`is_renting` | `true`
`is_returning` | `true`
`last_reported` | Not part of API. Setting to current timestamp.


### free_bike_status.json

Returns all vehicles of `/availableRentalObjects` endpoint.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`bike_id` | `rentalObject['uid']`
`lat` | `rentalObject['position']['coordinates'][1]`
`lon` | `rentalObject['position']['coordinates'][0]`
`is_reserved` | `false`
`is_disabled` | `false`
`rental_uris` | -
`vehicle_type_id` | uncapitalized `vehicle_type['make'] + '_' + vehicle_type['model']`
`last_reported` |  Not part of API. Setting to current timestamp.
`current_range_meters` | `max_range_meters` * `current_fuel_percent` (Will be `50000` (50km) if no realtime info is available)
`current_fuel_percent` | `rentalObject['fillLevel']/100.0` if existant, 0.25 if not
`station_id` | `rentalObject['areaUid']`
`home_station_id` | -
`pricing_plan_id` | -
`vehicle_equipment` | -
`available_until` | -
`license_plate` | `rentalObject['licensePlate']`



### system_hours.json

Not provided for now. system_hours would describe the whole system, not opening_hours per station.


### system_calendar.json

Not provided for now.


### system_regions.json

Not provided for now.


### system_pricing_plans.json

Information is manually extracted from the providers website. See [config/flinkster.json](config/flinkster.json).


### system_alerts.json

Not provided for now.


### geofencing_zones.json

Not provided for now.


## Deep Links

Currently, no deeplinks for Flinkster are provided.
