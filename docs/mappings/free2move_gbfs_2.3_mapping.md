# Free2move to GBFS Mapping

This document map Free2move's sharing API to GBFS.

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

This specification describes the mapping of Free2move's API to GBFS.


## General Information

This section gives a high level overview of the sharing provider's API and the defined mapping to GBFS.

Official API documentation is access restricted, hence not included.



## Open Issues or Questions

Currently none.

## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information is manually extracted from the providers homepage. Only the real configuration in e.g. [config/free2move_stuttgart.json](../../config/free2move_stuttgart.json) is relevant.


### vehicle_types.json

Vehicle Types, vehicles are extracted from the `vehicles` endpoint, extracting this from the returned cars.

Example extract of a vehicle:

```json
{
    "maxGlobalVersion":7506155225,
    "locationId":18,
    "locationName":"stuttgart",
    "vehicles":[
        {
            "vin":"XXXXXXXXXXXXXX",
            "plate":"XX-X99999E",
            "geoCoordinate": {
                "latitude":48.814445,
                "longitude":9.175282,
                "altitude":null
            },
            "fuelLevel":64,
            "address":"Leitzstraße, 70469 Stuttgart",
            "locationAlias": "stuttgart",
            "locationId":18,
            "attributes":[],
            "buildSeries":"FIAT_500_BEV",
            "fuelType":"ELECTRIC",
            "primaryColor":"205U",
            "charging":false,
            "freeForRental":true,
            "hardwareVersion":"HW43",
            "generation":"UNDEFINED",
            "region":"EU",
            "imageUrl":"https://www.share-now.com/api/rental/rental-assets/vehicles/{density}/fiat_500_bev_mineralgrey.png",
            "globalVersion":7506151647,
            "brand":"SHARENOW",
            "batteryVoltage":12.73,
            "transmission":"GA",
            "plannedEndDate":1769904000000,
            "seats":4
        }
    ]
}
```


#### Field Mappings

GBFS Field | Mapping
--- | ---
`vehicle_type_id` |  `row['buildSeries']` appended with the vehicle's primaryColor.
`form_factor` | Always `car`.
`rider_capacity`| -
`cargo_volume_capacity` | -
`cargo_load_capacity` | -
`propulsion_type` | `row['fuelType']` mapped to GBFS vehicle types (`ELECTRIC`: `electric`, `SUPER_95`: `combustion`, `GASOLINE`: `combustion`, `DIESEL`: `combustion_diesel`).
`eco_label` | -
`max_range_meters` | Not availabe via API, set to default, currently `400.000`
`name` | Combination of `make` and `model`, which are extracted from `row['buildSeries']` and mapped in the code. If no mapping is defined, `buildSeries` is split at the first underscore, and first part is used as `make`, last as `model`.
`g_CO2_km` | -
`vehicle_image` | -
`make` | extracted from `row['buildSeries']` and mapped in the code.
`model` | extracted from `row['buildSeries']` and mapped in the code.
`color` | `row['primaryColor']` mapped to `weiß`, `silber`, `schwarz` or `grau`. In case no mapping is defined, we return the last part of the `imageUrl`, as this seems to contain the color string (in English). If no `imageUrl` is provided, we return `unbekannt`.
`wheel_count` | Always `4`.
`max_permitted_speed` | -
`rated_power` | -
`default_reserve_time` | -
`return_constraint`| Always `free_floating`
`vehicle_assets`| -
`seats` | `row['seats']`
`default_pricing_plan_id`| `{pricing_plan_prefix}_minutes`, where `pricing_plan_prefix` is deduced from a hard coded `buildSeries to prefix mapping, and `standard`, if none matches.
`pricing_plan_ids`| All pricing plans defined in the provider's config, if they start with `{pricing_plan_prefix}`.

### station_information.json

No stations, as Free2move is free floating.

### station_status.json

No stations, as Free2move is free floating.

### free_bike_status.json

Free vehicles are extracted from `vehicles` endpoint.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`bike_id` | `row['vid']` (NOTE: the vin is not rotated by Free2move. As a consequence, this feed should not be published publicly for GDBR reasons. The generated GBFS is, in consequence, not appropriate for unrestriced use. Users must handle GDPR requirements.)
`lat` | - `row['geoCoordinate']['latitude']`
`lon` | - `row['geoCoordinate']['longitude']`
`is_reserved` | `not row['freeForRental']`
`is_disabled` | `False`
`rental_uris` | -
`vehicle_type_id` | see section vehicle_types
`last_reported` | curent time
`current_range_meters` | `row['remainingRange']`, if set
`current_fuel_percent` | `row['fuelLevel'] / 100.0`, or `.25` if unset
`station_id` | -
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

No endpoint. Manually defined in the provider's config in `feed_data/pricing_plans`.

### system_alerts.json

No endpoint.

### geofencing_zones.json

Geofencing zones are extracted from the `operation_area` endpoint, which returns a single GeoJSON feature.

The geofencing zones are generated as a one element collection with a MultiPolygon counterclockwise ordered lists of coordinates (to reflect the restrictions outside the service area) and the following properties:

GBFS Field | Mapping
--- | ---
`name` | OPTIONAL | String | Public name of the geofencing zone.
`start` | -
`end` | -
`rules` | List of rules
\-&nbsp;`vehicle_type_id` | None, restrictions apply to all vehicle types.
\-&nbsp;`ride_allowed` | `false` - Undocked (“free floating”) ride cannot start or end in this zone.
\-&nbsp;`ride_through_allowed` | `true` - Ride can travel through this zone.
\-&nbsp;`maximum_speed_kph` | No maximum speed to observe, thus omitted.
\-&nbsp;`station_parking`| -

## Deep Links

Deep links seem not to be available for vehicles yet.