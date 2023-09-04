
# deer to GBFS Mapping

This document map deer's sharing API to GBFS.

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

This specification describes the mapping of car-sharing provider [deer](https://www.deer-carsharing.de/)'s API to GBFS. 

deer GmbH uses Fleetster as booking service provider. Besides the standard Fleetster API, deer defines a
couple of custom properties, that should e taken into account when mapping to GBFS.

## General Information

This section gives a high level overview of the sharing provider's API and the defined mapping to GBFS.

The Fleetster API is described via a [Swagger API documentation](https://my.fleetster.net/swagger/).

## Open Issues or Questions

This sections lists questions that still need to be clarified. Consider discussing them as GitHub issue, adding the provider name as tag.

1.  Sind vehicles mit active=false die verfügbaren? 
2.  Über fleetser abrufbare tarifInformation scheint nicht Bedingungen auf Homepage zu entsprechen(?): 
'privateTrip': [{'name': 'Stunden', 'type': 'hours', 'startTime': '10:21', 'endTime': '10:21', 'rate': 6.5, 'frequency': 1, '_id': '5d3aed1269a1590007b60c75'}, {'name': 'Stunden', 'type': 'hours', 'startTime': '10:21', 'endTime': '10:21', 'rate': 39.9, 'frequency': 5.91, '_id': '5d3aed1269a1590007b60c74'}, {'name': 'Stunden', 'type': 'hours', 'startTime': '10:21', 'endTime': '10:21', 'rate': 39.9, 'frequency': 24, '_id': '5d3aed1269a1590007b60c72'}, {'name': 'Stunden', 'type': 'hours', 'startTime': '15:49', 'endTime': '15:49', 'rate': 1.63, 'frequency': 0.25, '_id': '5eaaef886b87f45fb875e338'}, {'name': 'Wochenendtarif', 'type': 'day', 'startTime': '17:00', 'endTime': '21:00', 'rate': 74.9, 'startDay': 5, 'endDay': 0, '_id': '5f084f9dbda8db174f07f3fc'}], 'serviceTrip': []

3.  Anhand welchen Attributs lässt sich Fahrzeug den Tarifklassen basic, business, premium zuordnen? Tesla 3 und Porsche Taycan haben beide "category":"premium"
4.  Fleetster scheint keinen Fahrzeugtypen als Entität zu unterstützen. Die bei Fahrzeugen angegebenen brand/model Angaben enthalten vielfach Unterschiede (Groß-/Kleischreibung, Leerschritte, Punkte,…). Diese erschweren eine Zusammenfassung verschiedener Fahrzeug-Typen.
5.  Lässt sich die maximale Reichweite eines Fahrzeugs aus fleetster Angaben ermitteln?
6.  Lässt sich der aktuelle Ladestand/Restreichweite aus fleetster -Angaben ermitteln
7.  Neulingen Rathaus scheint mit falscher Koordinate im System (Null-Island)
8.  Wie lauten discovery uris für ios/android?
9. Unter welcher Lizenz können die Daten veröffentlicht werden? Attribution (in Hinblick auf GBFSv3)?
10. Ist an jeder deer Station eine Lademöglichkeit vorhanden, bzw. wie ist dies aus Daten ableitbar?
11. Wir gehen davon aus, das Fahrzeuge wieder an ihre Heimat-Station zurückgegeben werden müssen

## Files

This section defines the mappings for each GBFS file. Not every file needs to be provided. If a file is omitted, a short explanation shoulld be given.

File Name | REQUIRED | Defines | Mapping Notes
---|---|---|---
gbfs.json | Yes <br/>*(as of v2.0)* | Auto-discovery file that links to all of the other files published by the system. |
gbfs_versions.json <br/>*(added in v1.1)* | OPTIONAL | Lists all feed endpoints published according to versions of the GBFS documentation. |
system_information.json | Yes | Details including system operator, system location, year implemented, URL, contact info, time zone. |
vehicle_types.json <br/>*(added in v2.1)* | Conditionally REQUIRED | Describes the types of vehicles that system operator has available for rent. REQUIRED of systems that include information about vehicle types in the `free_bike_status.json` file. If this file is not included, then all vehicles in the feed are assumed to be non-motorized bicycles. |
station_information.json | Conditionally REQUIRED | List of all stations, their capacities and locations. REQUIRED of systems utilizing docks. |
station_status.json | Conditionally REQUIRED | Number of available vehicles and docks at each station and station availability. REQUIRED of systems utilizing docks. |
free_bike_status.json | Conditionally REQUIRED | *(as of v2.1)* Describes all vehicles that are not currently in active rental. REQUIRED for free floating (dockless) vehicles. OPTIONAL for station based (docked) vehicles. Vehicles that are part of an active rental MUST NOT appear in this feed. |
system_hours.json | OPTIONAL | Hours of operation for the system. |
system_calendar.json | OPTIONAL | Dates of operation for the system. |
system_regions.json | OPTIONAL | Regions the system is broken up into. |
system_pricing_plans.json | OPTIONAL | System pricing scheme. |
system_alerts.json | OPTIONAL | Current system alerts. |
geofencing_zones.json <br/>*(added in v2.1)* | OPTIONAL | Geofencing zones and their associated rules and attributes. |


### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information is manually extracted from the providers homepage. The mapping in the following illustrates the initial setup. For ongoing changes, only the real configuration in [config/deer.json](config/deer.json) is relevant.

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`system_id` | Yes | ID | This is a globally unique identifier for the vehicle share system.  It is up to the publisher of the feed to guarantee uniqueness and MUST be checked against existing `system_id` fields in [systems.csv](https://github.com/NABSA/gbfs/blob/master/systems.csv) to ensure this. This value is intended to remain the same over the life of the system. <br><br>Each distinct system or geographic area in which vehicles are operated SHOULD have its own `system_id`. System IDs SHOULD be recognizable as belonging to a particular system - for example, `bcycle_austin` or `biketown_pdx` - as opposed to random strings. | deer
`language` | Yes | Language | The language that will be used throughout the rest of the files. It MUST match the value in the [gbfs.json](#gbfsjson) file. | de-DE
`name` | Yes | String | Name of the system to be displayed to customers. | deer 
`short_name` | OPTIONAL | String | OPTIONAL abbreviation for a system. | -
`operator` | OPTIONAL | String | Name of the system operator. | DEER GmbH
`url` | OPTIONAL | URL | The URL of the vehicle share system. | https://www.deer-carsharing.de/
`purchase_url` | OPTIONAL | URL | URL where a customer can purchase a membership. | https://www.deer-carsharing.de/registrieren/
`start_date` | OPTIONAL | Date | Date that the system began operations. | -
`phone_number` | OPTIONAL | Phone Number | This OPTIONAL field SHOULD contain a single voice telephone number for the specified system’s customer service department. It can and SHOULD contain punctuation marks to group the digits of the number. Dialable text (for example, Capital Bikeshare’s "877-430-BIKE") is permitted, but the field MUST NOT contain any other descriptive text. | +49 7051 1300-120
`email` | OPTIONAL | Email | This OPTIONAL field SHOULD contain a single contact email address actively monitored by the operator’s customer service department. This email address SHOULD be a direct contact point where riders can reach a customer service representative. | carsharing@deer-mobility.de
`feed_contact_email` <br/>*(added in v1.1)* | OPTIONAL | Email | This OPTIONAL field SHOULD contain a single contact email for feed consumers to report technical issues with the feed. | mobidata-bw@nvbw.de
`timezone` | Yes | Timezone | The time zone where the system is located. | CET
`license_url` | OPTIONAL | URL | A fully qualified URL of a page that defines the license terms for the GBFS data for this system, as well as any other license terms the system would like to define (including the use of corporate trademarks, etc) | -
`brand_assets`<br/>*(added in v2.3)*  | OPTIONAL | Object | An object where each key defines one of the items listed below. |
\- `brand_last_modified`<br/>*(added in v2.3)*  | Conditionally REQUIRED | Date | REQUIRED if `brand_assets` object is defined. Date that indicates the last time any included brand assets were updated or modified. |
\- `brand_terms_url`<br/>*(added in v2.3)*   | OPTIONAL |  URL |  A fully qualified URL pointing to the location of a page that defines the license terms of brand icons, colors, or other trademark information.  This field MUST NOT take the place of `license_url` or `license_id`. |
\- `brand_image_url`<br/>*(added in v2.3)*  | Conditionally REQUIRED |  URL |  REQUIRED if `brand_assets` object is defined. A fully qualified URL pointing to the location of a graphic file representing the brand for the service. File MUST be in SVG V1.1 format and MUST be either square or round. |
\- `brand_image_url_dark`<br/>*(added in v2.3)*  | OPTIONAL |  URL | A fully qualified URL pointing to the location of a graphic file representing the brand for the service for use in dark mode applications.  File MUST be in SVG V1.1 format and MUST be either square or round. |
\- `color`<br/>*(added in v2.3)*  | OPTIONAL |  String |  Color used to represent the brand for the service expressed as a 6 digit hexadecimal color code in the form #000000. |
`terms_url`<br/>*(added in v2.3)* | OPTIONAL | URL | A fully qualified URL pointing to the terms of service (also often called "terms of use" or "terms and conditions") for the service.  | https://www.deer-carsharing.de/wp-content/uploads/2023/03/AGB-deer-1.5.2022.pdf
`terms_last_updated`<br/>*(added in v2.3)* |Conditionally REQUIRED | Date | REQUIRED if `terms_url` is defined. The date that the terms of service provided at `terms_url` were last updated.  | 2022-05-01
`privacy_url`<br/>*(added in v2.3)*| OPTIONAL | URL | A fully qualified URL pointing to the privacy policy for the service. |
`privacy_last_updated`<br/>*(added in v2.3)* |Conditionally REQUIRED | Date | REQUIRED if `privacy_url` is defined. The date that the privacy policy provided at `privacy_url` was last updated.  |
`rental_apps` <br/>*(added in v1.1)* | OPTIONAL | Object | Contains rental app information in the `android` and `ios` JSON objects. |
\-&nbsp;`android` <br/>*(added in v1.1)* | OPTIONAL | Object | Contains rental app download and app discovery information for the Android platform in the `store_uri` and `discovery_uri` fields. See [examples](#examples) of how to use these fields and [supported analytics](#analytics). |
&emsp;- `store_uri` <br/>*(added in v1.1)* | Conditionally REQUIRED | URI | URI where the rental Android app can be downloaded from. Typically this will be a URI to an app store, such as Google Play. If the URI points to an app store, the URI SHOULD follow Android best practices so the viewing app can directly open the URI to the native app store app instead of a website. <br><br> REQUIRED if a `rental_uris`.`android` field is populated.<br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>Example value: `https://play.google.com/store/apps/details?id=com.example.android` | https://play.google.com/store/apps/details?id=de.fleetster.calw
&emsp;- `discovery_uri` <br/>*(added in v1.1)* | Conditionally REQUIRED | URI | URI that can be used to discover if the rental Android app is installed on the device (for example, using [`PackageManager.queryIntentActivities()`](https://developer.android.com/reference/android/content/pm/PackageManager.html#queryIntentActivities)). This intent is used by viewing apps to prioritize rental apps for a particular user based on whether they already have a particular rental app installed. <br><br>REQUIRED if a `rental_uris`.`android` field is populated.<br><br>Example value: `com.example.android://` | ?
\-&nbsp;`ios` <br/>*(added in v1.1)* | OPTIONAL | Object | Contains rental information for the iOS platform in the `store_uri` and `discovery_uri` fields. See [examples](#examples) of how to use these fields and [supported analytics](#analytics). |
&emsp;- `store_uri` <br/>*(added in v1.1)* | Conditionally REQUIRED | URI | URI where the rental iOS app can be downloaded from. Typically this will be a URI to an app store, such as the Apple App Store. If the URI points to an app store, the URI SHOULD follow iOS best practices so the viewing app can directly open the URI to the native app store app instead of a website. <br><br>REQUIRED if a `rental_uris`.`ios` field is populated.<br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>Example value: `https://apps.apple.com/app/apple-store/id123456789` | https://apps.apple.com/de/app/public-e-carsharing-deer/id1380667727
&emsp;- `discovery_uri` <br/>*(added in v1.1)* | Conditionally REQUIRED | URI | URI that can be used to discover if the rental iOS app is installed on the device (for example, using [`UIApplication canOpenURL:`](https://developer.apple.com/documentation/uikit/uiapplication/1622952-canopenurl?language=objc)). This intent is used by viewing apps to prioritize rental apps for a particular user based on whether they already have a particular rental app installed. <br><br>REQUIRED if a `rental_uris`.`ios` field is populated.<br><br>Example value: `com.example.ios://` | ?


### vehicle_types.json


Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`vehicle_types` | Yes | Array | Array that contains one object per vehicle type in the system as defined below. | /vehicles endpoint<br /><br />fleetster API has no explicit endpoint for vehicle types, so the need to be collected from vehicle’s information<br /><br />the vehicles endpoint returns an array, each element is a vehicle, only vehicles meeting the following conditions are considered:<ul><li>vehicle[‘active’]==true</li><li>vehicle[‘deleted’]==false</li></ul>
\- `vehicle_type_id` | Yes | ID | Unique identifier of a vehicle type. See [Field Types](#field-types) above for ID field requirements. | Normalized vehicle.brand + '_' + vehicle.model<br /><br />
\- `form_factor` | Yes | Enum | The vehicle's general form factor. <br /><br />Current valid values are:<br /><ul><li>`bicycle`</li><li>`cargo_bicycle`(*(added in v2.3)*)</li><li>`car`</li><li>`moped`</li><li>`scooter` (will be deprecated in  v3.0)</li><li>`scooter_standing` (standing kick scooter, *added in v2.3*)</li><li>`scooted_seated` (this is a kick scooter with a seat, not to be confused with `moped`, *added in v2.3*)</li><li>`other`</li></ul> | car
\- `rider_capacity`<br/>*(added in v2.3)* | OPTIONAL | Non-negative integer | The number of riders (driver included) the vehicle can legally accommodate. | `vehicle['extended']['Properties']['seats']`
\- `cargo_volume_capacity`<br/>*(added in v2.3)* | OPTIONAL | Non-negative integer | Cargo volume available in the vehicle, expressed in liters. For cars, it corresponds to the space between the boot floor, including the storage under the hatch, to the rear shelf in the trunk. | -
\- `cargo_load_capacity`<br/>*(added in v2.3)* | OPTIONAL | Non-negative integer | The capacity of the vehicle cargo space (excluding passengers), expressed in kilograms. | -
\- `propulsion_type` | Yes | Enum | The primary propulsion type of the vehicle. <br /><br />Current valid values are:<br /><ul><li>`human` _(Pedal or foot propulsion)_</li><li>`electric_assist` _(Provides electric motor assist only in combination with human propulsion - no throttle mode)_</li><li>`electric` _(Powered by battery-powered electric motor with throttle mode)_</li><li>`combustion` _(Powered by gasoline combustion engine)_</li><li>`combustion_diesel` _(Powered by diesel combustion engine, added in v2.3)_</li><li>`hybrid` _(Powered by combined combustion engine and battery-powered motor, added in v2.3)_</li><li>`plug_in_hybrid` _(Powered by combined combustion engine and battery-powered motor with plug-in charging, added in v2.3)_</li><li>`hydrogen_fuel_cell` _(Powered by hydrogen fuel cell powered electric motor, added in v2.3)_</li></ul> This field was inspired by, but differs from the propulsion types field described in the [Open Mobility Foundation Mobility Data Specification](https://github.com/openmobilityfoundation/mobility-data-specification/blob/main/general-information.md#propulsion-types). | vehicle[‘engine’]<br /><br /><ul><li>`electric => electric`</li></ul>Others currently not in use. Converter should report an error if not and ignore this vehicle.
\- `eco_label`<br/>*(added in v2.3)* | OPTIONAL | Array | Vehicle air quality certificate. Official anti-pollution certificate, based on the information on the vehicle's registration certificate, attesting to its level of pollutant emissions based on a defined standard. In Europe, for example, it is the European emission standard. The aim of this measure is to encourage the use of the least polluting vehicles by allowing them to drive during pollution peaks or in low emission zones.<br /><br />Each element in the array is an object with the keys below. | -
&emsp;\-&nbsp; `country_code`<br/>*(added in v2.3)* | Conditionally REQUIRED | Country code | REQUIRED if `eco_label` is defined. Country where the `eco_sticker` applies. | -
&emsp;\-&nbsp; `eco_sticker`<br/>*(added in v2.3)* | Conditionally REQUIRED | String | REQUIRED if `eco_label` is defined. Name of the eco label. The name must be written in lowercase, separated by an underscore.<br /><br />Example of `eco_sticker` in Europe :<ul><li>CritAirLabel (France) <ul><li>critair</li><li>critair_1</li><li>critair_2</li><li>critair_3</li><li>critair_4</li><li>critair_5</li></ul></li><li>UmweltPlakette (Germany)<ul><li>euro_2</li><li>euro_3</li><li>euro_4</li><li>euro_5</li><li>euro_6</li><li>euro_6_temp</li><li>euro_E</li></ul></li><li>UmweltPickerl (Austrich)<ul><li>euro_1</li><li>euro_2</li><li>euro_3</li><li>euro_4</li><li>euro_5</li></ul><li>Reg_certificates (Belgium)<ul><li>reg_certificates</li></ul><li>Distintivo_ambiental (Spain)<ul><li>0</li><li>eco</li><li>b</li><li>c</li></ul></li></ul> | -
\- `max_range_meters` | Conditionally REQUIRED | Non-negative float | REQUIRED if the vehicle has a motor (as indicated by having a value other than `human` in the `propulsion_type` field). This represents the furthest distance in meters that the vehicle can travel without recharging or refueling when it has the maximum amount of energy potential (for example, a full battery or full tank of gas). | ?
\- `name` | OPTIONAL | String | The public name of this vehicle type. | vehicle.brand + vehicle.model 
\- `vehicle_accessories`<br/>*(added in v2.3)* | OPTIONAL | Array | Description of accessories available in the vehicle.  These accessories are part of the vehicle and are not supposed to change frequently. Current valid values are:<ul><li>`air_conditioning` _(Vehicle has air conditioning)_</li><li>`automatic` _(Automatic gear switch)_</li><li>`manual` _(Manual gear switch)_</li><li>`convertible` _(Vehicle is convertible)_</li><li>`cruise_control` _(Vehicle has a cruise control system ("Tempomat"))_</li><li>`doors_2` _(Vehicle has 2 doors)_</li><li>`doors_3` _(Vehicle has 3 doors)_</li><li>`doors_4` _(Vehicle has 4 doors)_</li><li>`doors_5` _(Vehicle has 5 doors)_</li><li>`navigation` _(Vehicle has a built-in navigation system)_</li></ul> | `air_conditioning` if `extended.Properties.aircondition`<br/>`doors_${extended.Properties.doors}` <br/> `navigation` if `extended.Properties.navigation`
\- `g_CO2_km`<br/>*(added in v2.3)* | OPTIONAL | Non-negative integer | Maximum quantity of CO2, in grams, emitted per kilometer, according to the [WLTP](https://en.wikipedia.org/wiki/Worldwide_Harmonised_Light_Vehicles_Test_Procedure). |
\- `vehicle_image`<br/>*(added in v2.3)* | OPTIONAL | URL | URL to an image that would assist the user in identifying the vehicle (for example, an image of the vehicle or a logo).<br /> Allowed formats: JPEG, PNG. |
| \- `make`<br/>*(added in v2.3)*| OPTIONAL| String| The name of the vehicle manufacturer. <br><br>Example: <ul><li>CUBE Bikes</li><li>Renault</li></ul> | `brand`
| \- `model`<br/>*(added in v2.3)*| OPTIONAL| String| The name of the vehicle model. <br><br>Example <ul><li>Giulia</li><li>MX50</li></ul> | `model`
| \- `color`<br/>*(added in v2.3)*| OPTIONAL| String| The color of the vehicle. <br><br>All words must be in lower case, without special characters, quotation marks, hyphens, underscores, commas, or dots. Spaces are allowed in case of a compound name. <br><br>Example <ul><li>green</li><li>dark blue</li></ul>  |
\- `wheel_count`<br/>*(added in v2.3)* | OPTIONAL | Non-negative Integer | Number of wheels this vehicle type has. | `4`
\- `max_permitted_speed`<br/>*(added in v2.3)* | OPTIONAL | Non-negative Integer | The maximum speed in kilometers per hour this vehicle is permitted to reach in accordance with local permit and regulations. | `extended.Properties.vMax`
\- `rated_power`<br/>*(added in v2.3)* | OPTIONAL | Non-negative Integer | The rated power of the motor for this vehicle type in watts. | `extended.Properties.horsepower * 736` (1 PS = 0,736 kW)
\- `default_reserve_time`<br/>*(added in v2.3)* | OPTIONAL | Non-negative Integer | Maximum time in minutes that a vehicle can be reserved before a rental begins. When a vehicle is reserved by a user, the vehicle remains locked until the rental begins. During this time the vehicle is unavailable and cannot be reserved or rented by other users. The vehicle status in `free_bike_status.json` MUST be set to `is_reserved = true`. If the value of `default_reserve_time` elapses without a rental beginning, the vehicle status MUST change to `is_reserved = false`. If `default_reserve_time` is set to `0`, the vehicle type cannot be reserved.  | -
\- `return_constraint`<br/>*(as of v2.3)*| OPTIONAL | Enum | The conditions for returning the vehicle at the end of the rental.<br /><br />Current valid values are:<br /><ul><li>`free_floating` _(The vehicle can be returned anywhere permitted within the service area.  Note that this field is subject to rules in `geofencing_zones.json` if defined.)_</li><li>`roundtrip_station` _(The vehicle has to be returned to the same station from which it was initially rented. Note that a specific station can be assigned to the vehicle in `free_bike_status.json` using home_station.)_</li><li>`any_station` _(The vehicle has to be returned to any station within the service area .)_</li><li>`hybrid` (The vehicle can be returned to any station, or anywhere else permitted within the service area. Note that the vehicle is subject to rules in `geofencing_zones.json` if defined.)</li> | `roundtrip_station`
\- `vehicle_assets`<br/>*(added in v2.3)*| OPTIONAL | Object | An object where each key defines one of the items listed below. |
&emsp;&emsp;\- `icon_url`<br/>*(added in v2.3)*| Conditionally REQUIRED | URL | REQUIRED if `vehicle_assets` is defined. A fully qualified URL pointing to the location of a graphic icon file that MAY be used to represent this vehicle type on maps and in other applications. File MUST be in SVG V1.1 format and MUST be either square or round. |
&emsp;&emsp;\- `icon_url_dark`<br/>*(added in v2.3)*| OPTIONAL | URL | A fully qualified URL pointing to the location of a graphic icon file to be used to represent this vehicle type when in dark mode on maps and in other applications. File MUST be in SVG V1.1 format and MUST be either square or round. |
&emsp;&emsp;\- `icon_last_modified`<br/>*(added in v2.3)*| Conditionally REQUIRED | Date | REQUIRED if `vehicle_assets` is defined. Date that indicates the last time any included vehicle icon images were modified or updated.  |
\- `default_pricing_plan_id`<br/>*(added in v2.3)*| OPTIONAL | ID |  A `plan_id`, as defined in `system_pricing_plans.json`, that identifies a default pricing plan for this vehicle to be used by trip planning applications for purposes of calculating the cost of a single trip using this vehicle type. This default pricing plan is superseded by `pricing_plan_id` when `pricing_plan_id` is defined in `free_bike_status.json` Publishers SHOULD define `default_pricing_plan_id` first and then override it using `pricing_plan_id` in `free_bike_status.json` when necessary. <br />*Note: This field will become Conditionally REQUIRED in the next MAJOR version.* | <ul><li>`business_line`>`business_line` if category in {'business', 'premium'}</li><li>`exclusive_line` if vehicle['brand'] in {'Porsche'}</li><li>`basic_line` if category in {'compact', 'midsize', 'city', 'economy', 'fullsize'}</li></ul>
\- `pricing_plan_ids`<br/>*(added in v2.3)* | OPTIONAL | Array | Array of all pricing plan IDs, as defined in `system_pricing_plans.json`, that are applied to this vehicle type. <br /><br />This array SHOULD be published when there are multiple pricing plans defined in `system_pricing_plans.json` that apply to a single vehicle type. | -


### station_information.json


Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`stations` | Yes | Array | Array that contains one object per station as defined below. | /locations<br /><br />JSON response contains array, each representing a station. Only those with the following attributes will be considered:<ul><li>deleted=false</li><li>extended/PublicCarsharing/hasPublicCarsharing=true</li></ul>
\-&nbsp;`station_id` | Yes | ID | Identifier of a station. | `station['_id']`
\-&nbsp;`name` | Yes | String | The public name of the station for display in maps, digital signage, and other text applications. Names SHOULD reflect the station location through the use of a cross street or local landmark. Abbreviations SHOULD NOT be used for names and other text (for example, "St." for "Street") unless a location is called by its abbreviated name (for example, “JFK Airport”). See [Text Fields and Naming](#text-fields-and-naming). <br>Examples: <ul><li>Broadway and East 22nd Street</li><li>Convention Center</li><li>Central Park South</li></ul> | `station['name']`
\-&nbsp;`short_name` | OPTIONAL | String | Short name or other type of identifier. | -
\-&nbsp;`lat` | Yes | Latitude | Latitude of the station in decimal degrees. This field SHOULD have a precision of 6 decimal places (0.000001). See [Coordinate Precision](#coordinate-precision). | `station['extended'] ['GeoPosition'] ['latitude']`
\-&nbsp;`lon` | Yes | Longitude | Longitude of the station in decimal degrees. This field SHOULD have a precision of 6 decimal places (0.000001). See [Coordinate Precision](#coordinate-precision). | `station['extended'] ['GeoPosition'] ['longitude']`
\-&nbsp;`address` | OPTIONAL | String | Address (street number and name) where station is located. This MUST be a valid address, not a free-form text description. Example: 1234 Main Street | `station['streetName'] + ' ' + station['streetNumber']`
\-&nbsp;`cross_street` | OPTIONAL | String | Cross street or landmark where the station is located. |
\-&nbsp;`region_id` | OPTIONAL | ID | Identifier of the region where station is located. See [system_regions.json](#system_regionsjson). |
\-&nbsp;`post_code` | OPTIONAL | String | Postal code where station is located. | `station['postcode']`
\-&nbsp;`rental_methods` | OPTIONAL | Array | Payment methods accepted at this station. <br /> Current valid values are:<br /> <ul><li>`key` (operator issued vehicle key / fob / card)</li><li>`creditcard`</li><li>`paypass`</li><li>`applepay`</li><li>`androidpay`</li><li>`transitcard`</li><li>`accountnumber`</li><li>`phone`</li></ul> |
\-&nbsp;`is_virtual_station` <br/>*(added in v2.1)* | OPTIONAL | Boolean | Is this station a location with or without smart dock technology? <br /><br /> `true` - The station is a location without smart docking infrastructure.  the station may be defined by a point (lat/lon) and/or `station_area` (below). <br /><br /> `false` - The station consists of smart docking infrastructure (docks). <br /><br /> This field SHOULD be published by mobility systems that have station locations without standard, internet connected physical docking infrastructure. These may be racks or geofenced areas designated for rental and/or return of vehicles. Locations that fit within this description SHOULD have the `is_virtual_station` boolean set to `true`. |
\-&nbsp;`station_area` <br/>*(added in v2.1)* | OPTIONAL | GeoJSON MultiPolygon | A GeoJSON MultiPolygon that describes the area of a virtual station. If `station_area` is supplied, then the record describes a virtual station. <br /><br /> If lat/lon and `station_area` are both defined, the lat/lon is the significant coordinate of the station (for example, parking facility or valet drop-off and pick up point). The `station_area` takes precedence over any `ride_allowed` rules in overlapping `geofencing_zones`. |
\-&nbsp;`parking_type` <br/>*(added in v2.3)* | OPTIONAL | Enum | Type of parking station.<br /><br />Current valid values are:<ul><li>`parking_lot` _(Off-street parking lot)_</li><li>`street_parking` _(Curbside parking)_</li><li>`underground_parking` _(Parking that is below street level, station may be non-communicating)_</li><li>`sidewalk_parking` _(Park vehicle on sidewalk, out of the pedestrian right of way)_</li><li>`other`</li></ul> |
\-&nbsp; `parking_hoop`<br/>*(added in v2.3)* | OPTIONAL | Boolean | Are parking hoops present at this station?<br /><br />`true` - Parking hoops are present at this station.<br />`false` - Parking hoops are not present at this station.<br /><br />Parking hoops are lockable devices that are used to secure a parking space to prevent parking of unauthorized vehicles. |
\-&nbsp; `contact_phone`<br/>*(added in v2.3)* | OPTIONAL | Phone number | Contact phone of the station. |
\-&nbsp;`capacity` | OPTIONAL | Non-negative integer | Number of total docking points installed at this station, both available and unavailable, regardless of what vehicle types are allowed at each dock. <br/><br/>If this is a virtual station defined using the `is_virtual_station` field, this number represents the total number of vehicles of all types that can be parked at the virtual station.<br/><br/>If the virtual station is defined by `station_area`, this is the number that can park within the station area. If `lat`/`lon` are defined, this is the number that can park at those coordinates. |
\-&nbsp;`vehicle_capacity` <br/>*(added in v2.1)* | OPTIONAL | Object | An object used to describe the parking capacity of virtual stations (defined using the `is_virtual_station` field), where each key is a `vehicle_type_id` as described in [vehicle_types.json](#vehicle_typesjson), and the value is a number representing the total number of vehicles of this type that can park within the virtual station.<br/><br/>If the virtual station is defined by `station_area`, this is the number that can park within the station area. If `lat`/`lon` is defined, this is the number that can park at those coordinates. |
\-&nbsp;`vehicle_type_capacity` <br/>*(added in v2.1)* | OPTIONAL | Object | An object used to describe the docking capacity of a station where each key is a `vehicle_type_id` as described in [vehicle_types.json](#vehicle_typesjson), and the value is a number representing the total docking points installed at this station, both available and unavailable for the specified vehicle type. |
\-&nbsp;`is_valet_station` <br/>*(added in v2.1)* | OPTIONAL | Boolean | Are valet services provided at this station? <br /><br /> `true` - Valet services are provided at this station. <br /> `false` - Valet services are not provided at this station. <br /><br /> If this field is empty, it is assumed that valet services are not provided at this station. <br><br>This field’s boolean SHOULD be set to `true` during the hours which valet service is provided at the station. Valet service is defined as providing unlimited capacity at a station. |
\-&nbsp;`is_charging_station` <br/>*(added in v2.3)* | OPTIONAL | Boolean | Does the station support charging of electric vehicles? <br /><br /> `true` - Electric vehicle charging is available at this station. <br /> `false` -  Electric vehicle charging is not available at this station. | ?
\-&nbsp;`rental_uris` <br/>*(added in v1.1)* | OPTIONAL | Object | Contains rental URIs for Android, iOS, and web in the `android`, `ios`, and `web` fields. See [examples](#examples) of how to use these fields and [supported analytics](#analytics). |
&emsp;\-&nbsp;`android` <br/>*(added in v1.1)* | OPTIONAL | URI | URI that can be passed to an Android app with an `android.intent.action.VIEW` Android intent to support Android Deep Links (https://developer.android.com/training/app-links/deep-linking). Please use Android App Links (https://developer.android.com/training/app-links) if possible so viewing apps do not need to manually manage the redirect of the user to the app store if the user does not have the application installed. <br><br>This URI SHOULD be a deep link specific to this station, and SHOULD NOT be a general rental page that includes information for more than one station. The deep link SHOULD take users directly to this station, without any prompts, interstitial pages, or logins. Make sure that users can see this station even if they never previously opened the application.  <br><br>If this field is empty, it means deep linking is not supported in the native Android rental app. <br><br>Note that the URI does not necessarily include the `station_id` for this station - other identifiers can be used by the rental app within the URI to uniquely identify this station. <br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>Android App Links example value: `https://www.example.com/app?sid=1234567890&platform=android` <br><br>Deep Link (without App Links) example value: `com.example.android://open.example.app/app?sid=1234567890` |
&emsp;\-&nbsp;`ios` <br/>*(added in v1.1)* | OPTIONAL | URI | URI that can be used on iOS to launch the rental app for this station. More information on this iOS feature can be found [here](https://developer.apple.com/documentation/uikit/core_app/allowing_apps_and_websites_to_link_to_your_content/communicating_with_other_apps_using_custom_urls?language=objc). Please use iOS Universal Links (https://developer.apple.com/ios/universal-links/) if possible so viewing apps do not need to manually manage the redirect of the user to the app store if the user does not have the application installed. <br><br>This URI SHOULD be a deep link specific to this station, and SHOULD NOT be a general rental page that includes information for more than one station.  The deep link SHOULD take users directly to this station, without any prompts, interstitial pages, or logins. Make sure that users can see this station even if they never previously opened the application.  <br><br>If this field is empty, it means deep linking is not supported in the native iOS rental app. <br><br>Note that the URI does not necessarily include the 'station_id' for this station - other identifiers can be used by the rental app within the URI to uniquely identify this station. <br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>iOS Universal Links example value: `https://www.example.com/app?sid=1234567890&platform=ios` <br><br>Deep Link (without Universal Links) example value: `com.example.ios://open.example.app/app?sid=1234567890` |
&emsp;\-&nbsp;`web` <br/>*(added in v1.1)* | OPTIONAL | URL | URL that can be used by a web browser to show more information about renting a vehicle at this station. <br><br>This URL SHOULD be a deep link specific to this station, and SHOULD NOT be a general rental page that includes information for more than one station.  The deep link SHOULD take users directly to this station, without any prompts, interstitial pages, or logins. Make sure that users can see this station even if they never previously opened the application.  <br><br>If this field is empty, it means deep linking is not supported for web browsers. <br><br>Example value: `https://www.example.com/app?sid=1234567890` |


### station_status.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`stations` | Yes | Array | Array that contains one object per station in the system as defined below. | /vehicles?page=n endpoint<br /><br />Requires iterating over array-typed property stations (vehicles might be a better name).<br /><br />Filter `vehicle[‘available’]=true` as for now, GBFS provides realtime availability<br /><br />Group all vehicles per location id
\-&nbsp;`station_id` | Yes | ID | Identifier of a station. See [station_information.json](#station_informationjson). | `vehicle/location[‘id]`
\-&nbsp;`num_bikes_available` | Yes | Non-negative integer | Number of functional vehicles physically at the station that may be offered for rental. To know if the vehicles are available for rental, see `is_renting`. <br/><br/>If `is_renting` = `true`, this is the number of vehicles that are currently available for rent. If `is_renting` =`false`, this is the number of vehicles that would be available for rent if the station were set to allow rentals. | per location id: count(vehicle[availabilty]==true) having location id==station_id
\- `vehicle_types_available` <br/>*(added in v2.1)* | Conditionally REQUIRED | Array | REQUIRED if the [vehicle_types.json](#vehicle_typesjson) file has been defined. This field's value is an array of objects. Each of these objects is used to model the total number of each defined vehicle type available at a station. The total number of vehicles from each of these objects SHOULD add up to match the value specified in the `num_bikes_available`  field. | Deduceable from vehicles at stations
&emsp;\- `vehicle_type_id` <br/>*(added in v2.1)* | Conditionally REQUIRED | ID | REQUIRED if the `vehicle_types_available` is defined. The `vehicle_type_id` of each vehicle type at the station as described in [vehicle_types.json](#vehicle_typesjson).  |
&emsp;\- `count` <br/>*(added in v2.1)* | Conditionally REQUIRED | Non-negative integer | The total number of available vehicles of the corresponding `vehicle_type_id`, as defined in [vehicle_types.json](#vehicle_typesjson), at the station. |
\-&nbsp;`num_bikes_disabled` | OPTIONAL | Non-negative integer | Number of disabled vehicles of any type at the station. Vendors who do not want to publicize the number of disabled vehicles or docks in their system can opt to omit station `capacity` (in [station_information.json](#station_informationjson), `num_bikes_disabled`, and `num_docks_disabled` *(as of v2.0)*. If station `capacity` is published, then broken docks/vehicles can be inferred (though not specifically whether the decreased capacity is a broken vehicle or dock). | -
\-&nbsp;`num_docks_available` | Conditionally REQUIRED <br/>*(as of v2.0)* | Non-negative integer | REQUIRED except for stations that have unlimited docking capacity (for example, valet stations) *(as of v2.0)*. Number of functional docks physically at the station that are able to accept vehicles for return. To know if the docks are accepting vehicle returns, see `is_returning`. <br /><br/> If `is_returning` = `true`, this is the number of docks that are currently available to accept vehicle returns. If `is_returning` = `false`, this is the number of docks that would be available if the station were set to allow returns. | -
\- `vehicle_docks_available` <br/>*(added in v2.1)* | Conditionally REQUIRED | Array | REQUIRED in feeds where the [vehicle_types.json](#vehicle_typesjson) is defined and where certain docks are only able to accept certain vehicle types. If every dock at the station is able to accept any vehicle type, then this field is not REQUIRED. This field's value is an array of objects. Each of these objects is used to model the number of docks available for certain vehicle types. The total number of docks from each of these objects SHOULD add up to match the value specified in the `num_docks_available` field. | -
&emsp;\- `vehicle_type_ids` <br/>*(added in v2.1)* | Conditionally REQUIRED | Array | REQUIRED if `vehicle_docks_available` is defined. An array of strings where each string represents a `vehicle_type_id` that is able to use a particular type of dock at the station | -
&emsp;\- `count` <br/>*(added in v2.1)* | Conditionally REQUIRED | Non-negative integer | REQUIRED if `vehicle_docks_available` is defined. The total number of available docks at the station, that can accept vehicles of the corresponding `vehicle_type_id`, in the `vehicle_type_ids` array. | -
\-&nbsp;`num_docks_disabled` | OPTIONAL | Non-negative integer | Number of disabled dock points at the station. |
\-&nbsp;`is_installed` | Yes | Boolean | Is the station currently on the street?<br/><br/>`true` - Station is installed on the street.<br/>`false` - Station is not installed on the street.<br/><br/>Boolean SHOULD be set to `true` when equipment is present on the street. In seasonal systems where equipment is removed during winter, boolean SHOULD be set to `false` during the off season. May also be set to false to indicate planned (future) stations which have not yet been installed. | `true`
\-&nbsp;`is_renting` | Yes | Boolean | Is the station currently renting vehicles? <br /><br />`true` - Station is renting vehicles. Even if the station is empty, if it would otherwise allow rentals, this value MUST be `true`.<br/>`false` - Station is not renting vehicles.<br/><br/>If the station is temporarily taken out of service and not allowing rentals, this field MUST be set to `false`.<br/><br/>If a station becomes inaccessible to users due to road construction or other factors this field SHOULD be set to `false`. Field SHOULD be set to `false` during hours or days when the system is not offering vehicles for rent. | `true` 
\-&nbsp;`is_returning` | Yes | Boolean | Is the station accepting vehicle returns? <br /><br />`true` - Station is accepting vehicle returns. Even if the station is full, if it would otherwise allow vehicle returns, this value MUST be `true`.<br /> `false` - Station is not accepting vehicle returns.<br/><br/>If the station is temporarily taken out of service and not allowing vehicle returns, this field MUST be set to `false`.<br/><br/>If a station becomes inaccessible to users due to road construction or other factors, this field SHOULD be set to `false`. | `true`
\-&nbsp;`last_reported` | Yes | Timestamp | The last time this station reported its status to the operator's backend. | Not part of API. Setting to current timestamp.


### free_bike_status.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`bikes` | Yes | Array | Array that contains one object per vehicle that is currently not part of an active rental, as defined below. | /vehicles endpoint<br /><br />
\-&nbsp;`bike_id` | Yes | ID | Identifier of a vehicle. The `bike_id` identifier MUST be rotated to a random string after each trip to protect user privacy *(as of v2.0)*. Use of persistent vehicle IDs poses a threat to user privacy. The `bike_id` identifier SHOULD only be rotated once per trip. | `vehicle[’_id’]`
\-&nbsp;`lat` | Conditionally REQUIRED <br/>*(as of v2.1)* | Latitude | Latitude of the vehicle in decimal degrees. *(as of v2.1)* REQUIRED if `station_id` is not provided for this vehicle (free floating). This field SHOULD have a precision of 6 decimal places (0.000001). See [Coordinate Precision](#coordinate-precision). | -
\-&nbsp;`lon` | Conditionally REQUIRED <br/>*(as of v2.1)* | Longitude | Longitude of the vehicle in decimal degrees. *(as of v2.1)* REQUIRED if `station_id` is not provided for this vehicle (free floating). This field SHOULD have a precision of 6 decimal places (0.000001). See [Coordinate Precision](#coordinate-precision). | -
\-&nbsp;`is_reserved` | Yes | Boolean | Is the vehicle currently reserved? <br /><br /> `true` - Vehicle is currently reserved. <br /> `false` - Vehicle is not currently reserved. | ?
\-&nbsp;`is_disabled` | Yes | Boolean | Is the vehicle currently disabled? <br /><br /> `true` - Vehicle is currently disabled. <br /> `false` - Vehicle is not currently disabled.<br><br>This field is used to indicate vehicles that are in the field but not available for rental.  This may be due to a mechanical issue, low battery, etc. Publishing this data may prevent users from attempting to rent vehicles that are disabled and not available for rental. | ?
\-&nbsp;`rental_uris` <br/>*(added in v1.1)* | OPTIONAL | Object | JSON object that contains rental URIs for Android, iOS, and web in the `android`, `ios`, and `web` fields. See [examples](#examples) of how to use these fields and [supported analytics](#analytics). | ?
&emsp;\-&nbsp;`android` <br/>*(added in v1.1)* | OPTIONAL | URI | URI that can be passed to an Android app with an android.intent.action.VIEW Android intent to support Android Deep Links (https://developer.android.com/training/app-links/deep-linking). Please use Android App Links (https://developer.android.com/training/app-links) if possible, so viewing apps do not need to manually manage the redirect of the user to the app store if the user does not have the application installed. <br><br>This URI SHOULD be a deep link specific to this vehicle, and SHOULD NOT be a general rental page that includes information for more than one vehicle. The deep link SHOULD take users directly to this vehicle, without any prompts, interstitial pages, or logins. Make sure that users can see this vehicle even if they never previously opened the application. Note that as a best practice providers SHOULD rotate identifiers within deep links after each rental to avoid unintentionally exposing private vehicle trip origins and destinations.<br><br>If this field is empty, it means deep linking is not supported in the native Android rental app.<br><br>Note that the URI does not necessarily include the `bike_id` for this vehicle - other identifiers can be used by the rental app within the URI to uniquely identify this vehicle. <br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>Android App Links example value: `https://www.example.com/app?sid=1234567890&platform=android` <br><br>Deep Link (without App Links) example value: `com.example.android://open.example.app/app?sid=1234567890` | ?
&emsp;\-&nbsp;`ios` <br/>*(added in v1.1)* | OPTIONAL | URI | URI that can be used on iOS to launch the rental app for this vehicle. More information on this iOS feature can be found [here](https://developer.apple.com/documentation/uikit/core_app/allowing_apps_and_websites_to_link_to_your_content/communicating_with_other_apps_using_custom_urls?language=objc). Please use iOS Universal Links (https://developer.apple.com/ios/universal-links/) if possible, so viewing apps do not need to manually manage the redirect of the user to the app store if the user does not have the application installed. <br><br>This URI SHOULD be a deep link specific to this vehicle, and SHOULD NOT be a general rental page that includes information for more than one vehicle.  The deep link SHOULD take users directly to this vehicle, without any prompts, interstitial pages, or logins. Make sure that users can see this vehicle even if they never previously opened the application. Note that as a best practice providers SHOULD rotate identifiers within deep links after each rental to avoid unintentionally exposing private vehicle trip origins and destinations. <br><br>If this field is empty, it means deep linking is not supported in the native iOS rental app.<br><br>Note that the URI does not necessarily include the `bike_id` - other identifiers can be used by the rental app within the URL to uniquely identify this vehicle. <br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>iOS Universal Links example value: `https://www.example.com/app?sid=1234567890&platform=ios` <br><br>Deep Link (without Universal Links) example value: `com.example.ios://open.example.app/app?sid=1234567890` | ?
&emsp;\-&nbsp;`web` <br/>*(added in v1.1)* | OPTIONAL | URL | URL that can be used by a web browser to show more information about renting a vehicle at this vehicle. <br><br>This URL SHOULD be a deep link specific to this vehicle, and SHOULD NOT be a general rental page that includes information for more than one vehicle.  The deep link SHOULD take users directly to this vehicle, without any prompts, interstitial pages, or logins. Make sure that users can see this vehicle even if they never previously opened the application. Note that as a best practice providers SHOULD rotate identifiers within deep links after each rental to avoid unintentionally exposing private vehicle trip origins and destinations.<br><br>If this field is empty, it means deep linking is not supported for web browsers. <br><br>Example value: `https://www.example.com/app?sid=1234567890` |
\- `vehicle_type_id` <br/>*(added in v2.1)* | Conditionally REQUIRED | ID | REQUIRED if the [vehicle_types.json](#vehicle_typesjson) file is defined. The `vehicle_type_id` of this vehicle, as described in [vehicle_types.json](#vehicle_typesjson).  | ?
\- `last_reported` <br/>*(added in v2.1)* | OPTIONAL | Timestamp | The last time this vehicle reported its status to the operator's backend. |
\- `current_range_meters` <br/>*(added in v2.1)* | Conditionally REQUIRED | Non-negative float | REQUIRED if the corresponding `vehicle_type` definition for this vehicle has a motor. This value represents the furthest distance in meters that the vehicle can travel with the vehicle's current charge or fuel (without recharging or refueling). Note that in the case of carsharing, the given range is indicative and can be different from the one displayed on the vehicle's dashboard. |
\- `current_fuel_percent` <br/>*(added in v2.3)*| OPTIONAL | Non-negative float | This value represents the current percentage, expressed from 0 to 1, of fuel or battery power remaining in the vehicle. |
\- `station_id` <br/>*(added in v2.1)* | Conditionally REQUIRED | ID | REQUIRED if the vehicle is currently at a station and the [vehicle_types.json](#vehicle_typesjson) file has been defined. Identifier referencing the `station_id` field in [station_information.json](#station_informationjson).  | `vehicle[’locationId’]`
\- `home_station_id` <br/>*(added in v2.3)* | OPTIONAL | ID | The `station_id` of the station this vehicle must be returned to as defined in [station_information.json](#station_informationjson). |
\- `pricing_plan_id` <br/>*(added in v2.2)* | OPTIONAL | ID | The `plan_id` of the pricing plan this vehicle is eligible for as described in [system_pricing_plans.json](#system_pricing_plansjson). If this field is defined it supersedes `default_pricing_plan_id` in `vehicle_types.json`. This field SHOULD be used to override `default_pricing_plan_id` in `vehicle_types.json` to define pricing plans for individual vehicles when necessary. |
\- `vehicle_equipment`<br/>*(added in v2.3)* | OPTIONAL | Array | List of vehicle equipment provided by the operator in addition to the accessories already provided in the vehicle (field `vehicle_accessories` of `vehicle_types.json`) but subject to more frequent updates.<br/><br/>Current valid values are:<ul><li>`child_seat_a` _(Baby seat ("0-10kg"))_</li><li>`child_seat_b`     _(Seat or seat extension for small children ("9-18 kg"))_</li><li>`child_seat_c`   _(Seat or seat extension for older children ("15-36 kg"))_</li><li>`winter_tires`   _(Vehicle has tires for winter weather)_</li><li>`snow_chains`</li></ul> | `winter_tires` if `extended.Properties.winterTires`
\- `available_until`<br/>*(added in v2.3)* | OPTIONAL |  Datetime | The date and time when any rental of the vehicle must be completed. The vehicle must be returned and made available for the next user by this time. If this field is empty, it indicates that the vehicle is available indefinitely.<br /><br /> This field SHOULD be published by carsharing or other mobility systems where vehicles can be booked in advance for future travel. |


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
