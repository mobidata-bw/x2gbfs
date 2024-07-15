
# Cambio to GBFS Mapping

This document maps the Cambio API to GBFS.

# Reference version

This documentation refers to **[GBFS v2.3](https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md)**.

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
Cambio only provides static information, so GBFS feeds generated for Cambio don't provide realtime information. The following sections describe how Cambio's API is mapped to GBFS.

## General Information

Cambio provides static endpoints per city to retrieve their stations and vehicles, &lt;city&gt; to be replaced by the city short name, e.g. AAC for Aachen:

* https://cwapi.cambio-carsharing.com/opendata/v1/mandator/&lt;city&gt;/stations
* https://cwapi.cambio-carsharing.com/opendata/v1/mandator/&lt;city&gt;/vehicles



### Example

The following fragment is an example of the Cambio station document:

```json
[ {
  "id" : "15-4568",
  "displayName" : "Dom",
  "name" : "Dom",
  "address" : {
    "streetAddress" : "Jesuitenstr.",
    "streetNumber" : "12",
    "addressLocation" : "Aachen",
    "postalCode" : "52062",
    "addressCountry" : "DE"
  },
  "information" : {
    "description" : "Karte zum Öffnen der Schranken bei Ein- und Ausfahrt befindet sich am Schlüsselbund. Karte direkt vor das Lesefeld halten. Lesefeld am jeweiligen Schrankenautomaten rechts unten ausgewiesen. Karte mindestens eine Sekunde vorhalten.\n\nBeim Verlassen des Stellplatzes unbedingt den rotweißen Poller aufrichten. Der Dreikant-Schlüssel zum Entriegeln und Niederlegen des Pollers liegt im Fahrzeug (Handschuhfach oder Türablage).",
    "access" : "per cambio-App",
    "ptLines" : "2, 5, 11, 11E, 12, 14, 14E, 21, 22, 23, 24, 25, 31, 35, 43, 45, 51, 53, 55, 75, E, N2, N4, N5, N7, N60, SB63, 11V, 24V, 31V, V, SB63V",
    "ptStops" : "Alter Posthof",
    "location" : "Reservierte Stellplätze im Parkhaus am Dom. ACHTUNG: Bitte Haupttreppenhaus benutzen. Parkdeck 3, Plätze 301 bis 304."
  },
  "geoposition" : {
    "longitude" : 6.08171223,
    "latitude" : 50.77344063,
    "googleZoom" : 20
  },
  "stationType" : "FIXED",
  "vehicleClasses" : [ {
    "id" : "15-493",
    "displayName" : "S E-Auto ZOE Corsa-e"
  }, {
    "id" : "15-393",
    "displayName" : "S Fiesta Corsa Clio"
  } ]
}]
```

and this is an example extract of Cambio's vehicle document:

```json

[ {
  "id" : "15-604",
  "displayName" : "L Citroen Transport",
  "description" : "3-Sitzer, Transporter, 4 Türen, großes Ladevolumen",
  "availableAtStations" : [ {
    "id" : "15-28",
    "displayName" : "Rothe-Erde"
  } ],
  "equipment" : [ {
    "id" : "15-128",
    "displayName" : "Antiblockiersystem"
  }, {
    "id" : "15-130",
    "displayName" : "Fahrer-Airbag"
  }, {
    "id" : "15-135",
    "displayName" : "Kopfstützen vorn"
  }, {
    "id" : "15-136",
    "displayName" : "Radio"
  }, {
    "id" : "15-141",
    "displayName" : "Zentralverriegelung"
  } ],
  "priceClass" : {
    "id" : "15-30",
    "displayName" : "L"
  }
}
]
```


## Open Issues or Questions
Various information which could be provided via GBFS can't be deduced from Cambios static feed:

* propulsion_type (we guess it from the vehicle's name)
* max_range_meters (we assume 200km for propulsion type electric, 600km else)

Other information which might be extracted for Cambio's API is not yet extracted:
* station access
* vehicle equipement (GBFS mostly support different equipement information from those provided by cambio)
* number of seats

## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information needs to be manually extracted from the provider's homepage, as Cambio does not provide this information.

### vehicle_types.json

Vehicle types are read from Cambio's vehicles endpoint and mapped as follows:

#### Field Mappings

GBFS Field | Mapping
--- | ---
`vehicle_type_id` | `id`
`form_factor` | `car`
`rider_capacity`| -
`cargo_volume_capacity` | -
`cargo_load_capacity` | -
`propulsion_type` | Not explicitly provided by Cambio. We assume electric for those vehicleClasses which habe an `e-auto` in their lowercased name, or `smart ed`
`cargo_volume_capacity` | -
`eco_label` | -
`max_range_meters` | Not provided by Cambio. We assume 200km für vehicles with propulsion `electric`, 600km for those with `combustion`/`combustion_diesel`
`g_CO2_km` | -
`vehicle_image` | -
`make` | -
`model` | -
`wheel_count` | `4`
`max_permitted_speed` | -
`rated_power` | -
`default_reserve_time` | -
`return_constraint`| `roundtrip_station`
`vehicle_assets`| -
`default_pricing_plan_id`| `priceClass`.`id`
`pricing_plan_ids`| -


### station_information.json

JSON response for `/stations` is a list of station. Only those with the following attributes will be considered:

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `id`
`name` | `displayName`
`short_name` | -
`lat` | `geoposition/latitude`
`lon` | `geoposition/longitude`
`address` | `address`.`streetAddress` + `address`.`streetNumber`
`cross_street` | -
`region_id` | -
`post_code` | `address`.`postalCode`
`_city` | custom attribute extracted from `address`.`addressLocation`
`rental_methods` | -
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
`rental_uris` | `{ 'web': 'https://www.cambio-carsharing.de/stationen/station/{station.name.lower()}-{station.id}'}`


### station_status.json

Returns all stations of `/stations` endpoint, criteria see above (station_information.json)

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `id`
`num_bikes_available` | hypthothetical value: count of different vehicle types potentially available at this station, as announced via property `vehicleClasses`.
`vehicle_types_available` | list of vehicle_type_ids extracted from `vehicleClasses`, each with a hypthetical availability of 1.
`num_bikes_disabled` | -
`num_docks_available` | -
`vehicle_docks_available` | -
`num_docks_disabled` | -
`is_installed` | `true`
`is_renting` | `true`
`is_returning` | `true`
`last_reported` | Not part of API. Setting to current timestamp.


### free_bike_status.json

Not provided as Cambio only provides static feeds.

### system_hours.json

Not provided for now. system_hours would describe the whole system, not opening_hours per station.


### system_calendar.json

Not provided for now.


### system_regions.json

Not provided for now.


### system_pricing_plans.json

Information is manually and only partially extracted from the provider's website.


### system_alerts.json

Static file provided via the feed configuration, which explicitly states that the availability information is static and realtime availability needs to be checked with the provider.


### geofencing_zones.json

Not provided for now.
