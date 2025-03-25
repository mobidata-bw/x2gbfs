
# Fleetster to GBFS Mapping

This document maps Fleetster's sharing API to GBFS.

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

This specification describes the mapping of fleetster-based car-sharing providers like [deer](https://www.deer-carsharing.de/) or [mikar](https://www.mikar.de/) to GBFS.

deer GmbH uses Fleetster as booking service provider. Besides the standard Fleetster API, deer defines a
couple of custom properties, that should be taken into account when mapping to GBFS.

## General Information

This section gives a high level overview of the sharing provider's API and the defined mapping to GBFS.

The Fleetster API is described via a [Swagger API documentation](https://my.fleetster.net/swagger/).

## Open Issues or Questions

Open questions are now managed as [issues](https://github.com/mobidata-bw/x2gbfs/issues?q=is%3Aissue+is%3Aopen+label%3Adeer). They should be tagged with the specific provider, e.g. `deer` or `mikar`.


## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information is manually extracted from the providers homepage.

Note: According to fleetster, currently no rental_app uri's exist.


### vehicle_types.json

fleetster API has no explicit endpoint for vehicle types, so they need to be collected from vehicle’s information.
The vehicles endpoint returns an array, each element is a vehicle, only vehicles meeting the following conditions are considered:

* `vehicle['active'] is True`
* `vehicle['deleted'] is False`
* `vehicle['typeOfUsage'] == 'carsharing'`
* station with ID `vehicle['locationId']` is a valid carsharing station (see station_information)

#### Field Mappings

GBFS Field | Mapping
--- | ---
`vehicle_type_id` | normalized, lower cased `vehicle['brand'] + '_' + ` normalized, lower cased `vehicle['model']`
`form_factor` | `'car'`
`rider_capacity`| `vehicle['extended']['Properties']['seats']`
`cargo_volume_capacity` | -
`cargo_load_capacity` | -
`propulsion_type` | vehicle[‘engine’]<br /><br /><ul><li>`electric => electric`</li></ul>Others currently not in use. Converter should report an error if not and ignore this vehicle.
`eco_label` | -
`max_range_meters` | Not provided by fleetster. Set to `200000` for all vehicle types (200km)
`name` | normalized vehicle['brand'] + normalized vehicle['model']
`vehicle_accessories` | `air_conditioning` if `vehicle['extended']['Properties']['aircondition']`<br/>`doors_${vehicle['extended']['Properties']['doors']}` <br/> `navigation` if `vehicle['extended']['Properties']['navigation']`
`g_CO2_km` |
`vehicle_image` |
`make` | normalized `brand`
`model` | `vehicle.extended.Properties.color` mapped to a (German language) color name. For specific mappings, see [fleetster.py](https://github.com/mobidata-bw/x2gbfs/blob/main/x2gbfs/providers/fleetster.py)
`wheel_count` | `4`
`max_permitted_speed` | `vehicle['extended']['Properties']['vMax']`
`rated_power` | `vehicle['extended']['Properties']['horsepower'] * 736` (1 PS = 0,736 kW)
`default_reserve_time` |
`return_constraint`| `"any_station"` (called `Stationsflexibel` at https://www.deer-mobility.de/so-einfach-gehts/)
`vehicle_assets`| -
`default_pricing_plan_id`| <ul><li>`business_line`>`business_line` if category in {'business', 'premium'}</li><li>`exclusive_line` if vehicle['brand'] in {'Porsche'}</li><li>`basic_line` if category in {'compact', 'midsize', 'city', 'economy', 'fullsize'}</li></ul>
`pricing_plan_ids`| -


### station_information.json

JSON response for `/locations` contains array, each representing a station. Only those with the following attributes will be considered:

* `location['deleted'] is False`
* `location['extended']['PublicCarsharing']['hasPublicCarsharing'] is True`

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `location['_id']`
`name` | `location['name']`
`short_name` | -
`lat` | `location['extended']['GeoPosition']['latitude']`
`lon` | `location['extended']['GeoPosition']['longitude']`
`address` | `location['streetName'] + ' ' + station['streetNumber']`
`city` | `location['city']` Note that this property is not part of GBFS v2.3 and will become official only with GBFSv3.2. We include it nevertheless.
`cross_street` |
`region_id` |
`post_code` | `location['postcode']`
`rental_methods` | `['key']`
`is_virtual_station`|
`station_area` |
`parking_type` |
`parking_hoop` |
`contact_phone` |
`capacity` |
`vehicle_capacity`  |
`vehicle_type_capacity` |
`is_valet_station`  |
`is_charging_station` | Fleetster does not provide this information. For some providers, external knowledge allows setting it to `true` (i.e. for deer).
`rental_uris` | No information available


### station_status.json

Returns all stations of `/locations` endpoint, criteria see above (station_information.json)

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `location['id']`
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

Returns all vehicles of `/vehicles` endpoint, filtering criteria see above (vehicle_types.json).

#### Field Mappings

GBFS Field | Mapping
--- | ---
`bike_id` |  `vehicle['_id']`
`lat` |  -
`lon` |  -
`is_reserved` | `False`, if bookings request does not return any active booking having startDate < now < endDate for this vehicle, else `True` (see also `available_until`). An active booking is a booking which is not in any of the following states: `canceled`, `rejected`, `keyreturned`.
`is_disabled` | -
`rental_uris` | None. fleetster/deer do not provide rental uris for now
`vehicle_type_id` | normalized, lower cased `vehicle['brand']` + '_' + normalized, lower cased `vehicle['model']`
`last_reported` |
`current_range_meters` | Hard coded to `50000` (50km) as no realtime info is available
`current_fuel_percent` | -
`station_id` | `vehicle['locationId']`
`home_station_id` | -
`pricing_plan_id` | -
`vehicle_equipment` | `winter_tires` if `extended.Properties.winterTires`
`available_until` | `/bookings?endDate%5B%24gte%5D={now}Z` returns all bookings ending in the future. If there is no active booking (see above for a definition of an active booking) for this vehicle (`vehicleId == booking['vehicleId']`) which has already started (`bookings['startDate'] < now`) ), available_until is the earliest booking's `bookings['startDate']`. Unset else.


### system_hours.json

Not provided for now. system_hours would describe the whole system, not opening_hours per station.


### system_calendar.json

Not provided for now.


### system_regions.json

Not provided for now.


### system_pricing_plans.json

Information is manually extracted from the providers website. See [config/deer.json](config/deer.json).


### system_alerts.json

Not provided for now.


### geofencing_zones.json

Not provided for now.


## Deep Links

This sections describes how Deep Links can be costructed from `station_id` or `vehicle_id`.

Currently, no deeplinks for deer are provided.
