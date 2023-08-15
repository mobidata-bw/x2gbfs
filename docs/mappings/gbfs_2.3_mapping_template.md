
# Mapping Template

This document is a template which can be used to map proprietary sharing APIs to GBFS.

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

This specification describes the mapping of provider `Insert provider name here`'s API to GBFS 

## General Information

This section gives a high level overview of the sharing provider's API and the defined mapping to GBFS.

## Open Issues or Questions

This sections lists questions that still need to be clarified. Consider discussing them as GitHub issue, adding the provider name as tag.

Questions might be:
* Does provider's app support deep links and what is the uri template for them?
* ...

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


Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`language` | Yes | Language | The language that will be used throughout the rest of the files. It MUST match the value in the [system_information.json](#system_informationjson) file. |
\-&nbsp;`feeds` | Yes | Array | An array of all of the feeds that are published by this auto-discovery file. Each element in the array is an object with the keys below. |
&emsp;\-&nbsp;`name` | Yes | String | Key identifying the type of feed this is. The key MUST be the base file name defined in the spec for the corresponding feed type (`system_information` for `system_information.json` file, `station_information` for `station_information.json` file). |
&emsp;\-&nbsp;`url` | Yes | URL | URL for the feed. Note that the actual feed endpoints (urls) may not be defined in the `file_name.json` format. For example, a valid feed endpoint could end with `station_info` instead of `station_information.json`. |

### gbfs_versions.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`versions` | Yes | Array | Contains one object, as defined below, for each of the available versions of a feed. The array MUST be sorted by increasing MAJOR and MINOR version number. |
\-&nbsp;`version` | Yes | String | The semantic version of the feed in the form `X.Y`. |
\-&nbsp;`url` | Yes | URL | URL of the corresponding gbfs.json endpoint. |


### system_information.json


Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`system_id` | Yes | ID | This is a globally unique identifier for the vehicle share system.  It is up to the publisher of the feed to guarantee uniqueness and MUST be checked against existing `system_id` fields in [systems.csv](https://github.com/NABSA/gbfs/blob/master/systems.csv) to ensure this. This value is intended to remain the same over the life of the system. <br><br>Each distinct system or geographic area in which vehicles are operated SHOULD have its own `system_id`. System IDs SHOULD be recognizable as belonging to a particular system - for example, `bcycle_austin` or `biketown_pdx` - as opposed to random strings. |
`language` | Yes | Language | The language that will be used throughout the rest of the files. It MUST match the value in the [gbfs.json](#gbfsjson) file. |
`name` | Yes | String | Name of the system to be displayed to customers. |
`short_name` | OPTIONAL | String | OPTIONAL abbreviation for a system. |
`operator` | OPTIONAL | String | Name of the system operator. |
`url` | OPTIONAL | URL | The URL of the vehicle share system. |
`purchase_url` | OPTIONAL | URL | URL where a customer can purchase a membership. |
`start_date` | OPTIONAL | Date | Date that the system began operations. |
`phone_number` | OPTIONAL | Phone Number | This OPTIONAL field SHOULD contain a single voice telephone number for the specified system’s customer service department. It can and SHOULD contain punctuation marks to group the digits of the number. Dialable text (for example, Capital Bikeshare’s "877-430-BIKE") is permitted, but the field MUST NOT contain any other descriptive text. |
`email` | OPTIONAL | Email | This OPTIONAL field SHOULD contain a single contact email address actively monitored by the operator’s customer service department. This email address SHOULD be a direct contact point where riders can reach a customer service representative. |
`feed_contact_email` <br/>*(added in v1.1)* | OPTIONAL | Email | This OPTIONAL field SHOULD contain a single contact email for feed consumers to report technical issues with the feed. |
`timezone` | Yes | Timezone | The time zone where the system is located. |
`license_url` | OPTIONAL | URL | A fully qualified URL of a page that defines the license terms for the GBFS data for this system, as well as any other license terms the system would like to define (including the use of corporate trademarks, etc) |
`brand_assets`<br/>*(added in v2.3)*  | OPTIONAL | Object | An object where each key defines one of the items listed below. |
\- `brand_last_modified`<br/>*(added in v2.3)*  | Conditionally REQUIRED | Date | REQUIRED if `brand_assets` object is defined. Date that indicates the last time any included brand assets were updated or modified. |
\- `brand_terms_url`<br/>*(added in v2.3)*   | OPTIONAL |  URL |  A fully qualified URL pointing to the location of a page that defines the license terms of brand icons, colors, or other trademark information.  This field MUST NOT take the place of `license_url` or `license_id`. |
\- `brand_image_url`<br/>*(added in v2.3)*  | Conditionally REQUIRED |  URL |  REQUIRED if `brand_assets` object is defined. A fully qualified URL pointing to the location of a graphic file representing the brand for the service. File MUST be in SVG V1.1 format and MUST be either square or round. |
\- `brand_image_url_dark`<br/>*(added in v2.3)*  | OPTIONAL |  URL | A fully qualified URL pointing to the location of a graphic file representing the brand for the service for use in dark mode applications.  File MUST be in SVG V1.1 format and MUST be either square or round. |
\- `color`<br/>*(added in v2.3)*  | OPTIONAL |  String |  Color used to represent the brand for the service expressed as a 6 digit hexadecimal color code in the form #000000. |
`terms_url`<br/>*(added in v2.3)* | OPTIONAL | URL | A fully qualified URL pointing to the terms of service (also often called "terms of use" or "terms and conditions") for the service.  |
`terms_last_updated`<br/>*(added in v2.3)* |Conditionally REQUIRED | Date | REQUIRED if `terms_url` is defined. The date that the terms of service provided at `terms_url` were last updated.  |
`privacy_url`<br/>*(added in v2.3)*| OPTIONAL | URL | A fully qualified URL pointing to the privacy policy for the service. |
`privacy_last_updated`<br/>*(added in v2.3)* |Conditionally REQUIRED | Date | REQUIRED if `privacy_url` is defined. The date that the privacy policy provided at `privacy_url` was last updated.  |
`rental_apps` <br/>*(added in v1.1)* | OPTIONAL | Object | Contains rental app information in the `android` and `ios` JSON objects. |
\-&nbsp;`android` <br/>*(added in v1.1)* | OPTIONAL | Object | Contains rental app download and app discovery information for the Android platform in the `store_uri` and `discovery_uri` fields. See [examples](#examples) of how to use these fields and [supported analytics](#analytics). |
&emsp;- `store_uri` <br/>*(added in v1.1)* | Conditionally REQUIRED | URI | URI where the rental Android app can be downloaded from. Typically this will be a URI to an app store, such as Google Play. If the URI points to an app store, the URI SHOULD follow Android best practices so the viewing app can directly open the URI to the native app store app instead of a website. <br><br> REQUIRED if a `rental_uris`.`android` field is populated.<br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>Example value: `https://play.google.com/store/apps/details?id=com.example.android` |
&emsp;- `discovery_uri` <br/>*(added in v1.1)* | Conditionally REQUIRED | URI | URI that can be used to discover if the rental Android app is installed on the device (for example, using [`PackageManager.queryIntentActivities()`](https://developer.android.com/reference/android/content/pm/PackageManager.html#queryIntentActivities)). This intent is used by viewing apps to prioritize rental apps for a particular user based on whether they already have a particular rental app installed. <br><br>REQUIRED if a `rental_uris`.`android` field is populated.<br><br>Example value: `com.example.android://` |
\-&nbsp;`ios` <br/>*(added in v1.1)* | OPTIONAL | Object | Contains rental information for the iOS platform in the `store_uri` and `discovery_uri` fields. See [examples](#examples) of how to use these fields and [supported analytics](#analytics). |
&emsp;- `store_uri` <br/>*(added in v1.1)* | Conditionally REQUIRED | URI | URI where the rental iOS app can be downloaded from. Typically this will be a URI to an app store, such as the Apple App Store. If the URI points to an app store, the URI SHOULD follow iOS best practices so the viewing app can directly open the URI to the native app store app instead of a website. <br><br>REQUIRED if a `rental_uris`.`ios` field is populated.<br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>Example value: `https://apps.apple.com/app/apple-store/id123456789` |
&emsp;- `discovery_uri` <br/>*(added in v1.1)* | Conditionally REQUIRED | URI | URI that can be used to discover if the rental iOS app is installed on the device (for example, using [`UIApplication canOpenURL:`](https://developer.apple.com/documentation/uikit/uiapplication/1622952-canopenurl?language=objc)). This intent is used by viewing apps to prioritize rental apps for a particular user based on whether they already have a particular rental app installed. <br><br>REQUIRED if a `rental_uris`.`ios` field is populated.<br><br>Example value: `com.example.ios://` |


### vehicle_types.json


Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`vehicle_types` | Yes | Array | Array that contains one object per vehicle type in the system as defined below. |
\- `vehicle_type_id` | Yes | ID | Unique identifier of a vehicle type. See [Field Types](#field-types) above for ID field requirements. |
\- `form_factor` | Yes | Enum | The vehicle's general form factor. <br /><br />Current valid values are:<br /><ul><li>`bicycle`</li><li>`cargo_bicycle`(*(added in v2.3)*)</li><li>`car`</li><li>`moped`</li><li>`scooter` (will be deprecated in  v3.0)</li><li>`scooter_standing` (standing kick scooter, *added in v2.3*)</li><li>`scooted_seated` (this is a kick scooter with a seat, not to be confused with `moped`, *added in v2.3*)</li><li>`other`</li></ul> |
\- `rider_capacity`<br/>*(added in v2.3)* | OPTIONAL | Non-negative integer | The number of riders (driver included) the vehicle can legally accommodate. |
\- `cargo_volume_capacity`<br/>*(added in v2.3)* | OPTIONAL | Non-negative integer | Cargo volume available in the vehicle, expressed in liters. For cars, it corresponds to the space between the boot floor, including the storage under the hatch, to the rear shelf in the trunk. |
\- `cargo_load_capacity`<br/>*(added in v2.3)* | OPTIONAL | Non-negative integer | The capacity of the vehicle cargo space (excluding passengers), expressed in kilograms. |
\- `propulsion_type` | Yes | Enum | The primary propulsion type of the vehicle. <br /><br />Current valid values are:<br /><ul><li>`human` _(Pedal or foot propulsion)_</li><li>`electric_assist` _(Provides electric motor assist only in combination with human propulsion - no throttle mode)_</li><li>`electric` _(Powered by battery-powered electric motor with throttle mode)_</li><li>`combustion` _(Powered by gasoline combustion engine)_</li><li>`combustion_diesel` _(Powered by diesel combustion engine, added in v2.3)_</li><li>`hybrid` _(Powered by combined combustion engine and battery-powered motor, added in v2.3)_</li><li>`plug_in_hybrid` _(Powered by combined combustion engine and battery-powered motor with plug-in charging, added in v2.3)_</li><li>`hydrogen_fuel_cell` _(Powered by hydrogen fuel cell powered electric motor, added in v2.3)_</li></ul> This field was inspired by, but differs from the propulsion types field described in the [Open Mobility Foundation Mobility Data Specification](https://github.com/openmobilityfoundation/mobility-data-specification/blob/main/general-information.md#propulsion-types). |
\- `eco_label`<br/>*(added in v2.3)* | OPTIONAL | Array | Vehicle air quality certificate. Official anti-pollution certificate, based on the information on the vehicle's registration certificate, attesting to its level of pollutant emissions based on a defined standard. In Europe, for example, it is the European emission standard. The aim of this measure is to encourage the use of the least polluting vehicles by allowing them to drive during pollution peaks or in low emission zones.<br /><br />Each element in the array is an object with the keys below. |
&emsp;\-&nbsp; `country_code`<br/>*(added in v2.3)* | Conditionally REQUIRED | Country code | REQUIRED if `eco_label` is defined. Country where the `eco_sticker` applies. |
&emsp;\-&nbsp; `eco_sticker`<br/>*(added in v2.3)* | Conditionally REQUIRED | String | REQUIRED if `eco_label` is defined. Name of the eco label. The name must be written in lowercase, separated by an underscore.<br /><br />Example of `eco_sticker` in Europe :<ul><li>CritAirLabel (France) <ul><li>critair</li><li>critair_1</li><li>critair_2</li><li>critair_3</li><li>critair_4</li><li>critair_5</li></ul></li><li>UmweltPlakette (Germany)<ul><li>euro_2</li><li>euro_3</li><li>euro_4</li><li>euro_5</li><li>euro_6</li><li>euro_6_temp</li><li>euro_E</li></ul></li><li>UmweltPickerl (Austrich)<ul><li>euro_1</li><li>euro_2</li><li>euro_3</li><li>euro_4</li><li>euro_5</li></ul><li>Reg_certificates (Belgium)<ul><li>reg_certificates</li></ul><li>Distintivo_ambiental (Spain)<ul><li>0</li><li>eco</li><li>b</li><li>c</li></ul></li></ul> |
\- `max_range_meters` | Conditionally REQUIRED | Non-negative float | REQUIRED if the vehicle has a motor (as indicated by having a value other than `human` in the `propulsion_type` field). This represents the furthest distance in meters that the vehicle can travel without recharging or refueling when it has the maximum amount of energy potential (for example, a full battery or full tank of gas). |
\- `name` | OPTIONAL | String | The public name of this vehicle type. |
\- `vehicle_accessories`<br/>*(added in v2.3)* | OPTIONAL | Array | Description of accessories available in the vehicle.  These accessories are part of the vehicle and are not supposed to change frequently. Current valid values are:<ul><li>`air_conditioning` _(Vehicle has air conditioning)_</li><li>`automatic` _(Automatic gear switch)_</li><li>`manual` _(Manual gear switch)_</li><li>`convertible` _(Vehicle is convertible)_</li><li>`cruise_control` _(Vehicle has a cruise control system ("Tempomat"))_</li><li>`doors_2` _(Vehicle has 2 doors)_</li><li>`doors_3` _(Vehicle has 3 doors)_</li><li>`doors_4` _(Vehicle has 4 doors)_</li><li>`doors_5` _(Vehicle has 5 doors)_</li><li>`navigation` _(Vehicle has a built-in navigation system)_</li></ul> |
\- `g_CO2_km`<br/>*(added in v2.3)* | OPTIONAL | Non-negative integer | Maximum quantity of CO2, in grams, emitted per kilometer, according to the [WLTP](https://en.wikipedia.org/wiki/Worldwide_Harmonised_Light_Vehicles_Test_Procedure). |
\- `vehicle_image`<br/>*(added in v2.3)* | OPTIONAL | URL | URL to an image that would assist the user in identifying the vehicle (for example, an image of the vehicle or a logo).<br /> Allowed formats: JPEG, PNG. |
| \- `make`<br/>*(added in v2.3)*| OPTIONAL| String| The name of the vehicle manufacturer. <br><br>Example: <ul><li>CUBE Bikes</li><li>Renault</li></ul> |
| \- `model`<br/>*(added in v2.3)*| OPTIONAL| String| The name of the vehicle model. <br><br>Example <ul><li>Giulia</li><li>MX50</li></ul> |
| \- `color`<br/>*(added in v2.3)*| OPTIONAL| String| The color of the vehicle. <br><br>All words must be in lower case, without special characters, quotation marks, hyphens, underscores, commas, or dots. Spaces are allowed in case of a compound name. <br><br>Example <ul><li>green</li><li>dark blue</li></ul>  |
\- `wheel_count`<br/>*(added in v2.3)* | OPTIONAL | Non-negative Integer | Number of wheels this vehicle type has. |
\- `max_permitted_speed`<br/>*(added in v2.3)* | OPTIONAL | Non-negative Integer | The maximum speed in kilometers per hour this vehicle is permitted to reach in accordance with local permit and regulations. |
\- `rated_power`<br/>*(added in v2.3)* | OPTIONAL | Non-negative Integer | The rated power of the motor for this vehicle type in watts. |
\- `default_reserve_time`<br/>*(added in v2.3)* | OPTIONAL | Non-negative Integer | Maximum time in minutes that a vehicle can be reserved before a rental begins. When a vehicle is reserved by a user, the vehicle remains locked until the rental begins. During this time the vehicle is unavailable and cannot be reserved or rented by other users. The vehicle status in `free_bike_status.json` MUST be set to `is_reserved = true`. If the value of `default_reserve_time` elapses without a rental beginning, the vehicle status MUST change to `is_reserved = false`. If `default_reserve_time` is set to `0`, the vehicle type cannot be reserved.  |
\- `return_constraint`<br/>*(as of v2.3)*| OPTIONAL | Enum | The conditions for returning the vehicle at the end of the rental.<br /><br />Current valid values are:<br /><ul><li>`free_floating` _(The vehicle can be returned anywhere permitted within the service area.  Note that this field is subject to rules in `geofencing_zones.json` if defined.)_</li><li>`roundtrip_station` _(The vehicle has to be returned to the same station from which it was initially rented. Note that a specific station can be assigned to the vehicle in `free_bike_status.json` using home_station.)_</li><li>`any_station` _(The vehicle has to be returned to any station within the service area .)_</li><li>`hybrid` (The vehicle can be returned to any station, or anywhere else permitted within the service area. Note that the vehicle is subject to rules in `geofencing_zones.json` if defined.)</li> |
\- `vehicle_assets`<br/>*(added in v2.3)*| OPTIONAL | Object | An object where each key defines one of the items listed below. |
&emsp;&emsp;\- `icon_url`<br/>*(added in v2.3)*| Conditionally REQUIRED | URL | REQUIRED if `vehicle_assets` is defined. A fully qualified URL pointing to the location of a graphic icon file that MAY be used to represent this vehicle type on maps and in other applications. File MUST be in SVG V1.1 format and MUST be either square or round. |
&emsp;&emsp;\- `icon_url_dark`<br/>*(added in v2.3)*| OPTIONAL | URL | A fully qualified URL pointing to the location of a graphic icon file to be used to represent this vehicle type when in dark mode on maps and in other applications. File MUST be in SVG V1.1 format and MUST be either square or round. |
&emsp;&emsp;\- `icon_last_modified`<br/>*(added in v2.3)*| Conditionally REQUIRED | Date | REQUIRED if `vehicle_assets` is defined. Date that indicates the last time any included vehicle icon images were modified or updated.  |
\- `default_pricing_plan_id`<br/>*(added in v2.3)*| OPTIONAL | ID |  A `plan_id`, as defined in `system_pricing_plans.json`, that identifies a default pricing plan for this vehicle to be used by trip planning applications for purposes of calculating the cost of a single trip using this vehicle type. This default pricing plan is superseded by `pricing_plan_id` when `pricing_plan_id` is defined in `free_bike_status.json` Publishers SHOULD define `default_pricing_plan_id` first and then override it using `pricing_plan_id` in `free_bike_status.json` when necessary. <br />*Note: This field will become Conditionally REQUIRED in the next MAJOR version.* |
\- `pricing_plan_ids`<br/>*(added in v2.3)* | OPTIONAL | Array | Array of all pricing plan IDs, as defined in `system_pricing_plans.json`, that are applied to this vehicle type. <br /><br />This array SHOULD be published when there are multiple pricing plans defined in `system_pricing_plans.json` that apply to a single vehicle type. |


### station_information.json


Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`stations` | Yes | Array | Array that contains one object per station as defined below. |
\-&nbsp;`station_id` | Yes | ID | Identifier of a station. |
\-&nbsp;`name` | Yes | String | The public name of the station for display in maps, digital signage, and other text applications. Names SHOULD reflect the station location through the use of a cross street or local landmark. Abbreviations SHOULD NOT be used for names and other text (for example, "St." for "Street") unless a location is called by its abbreviated name (for example, “JFK Airport”). See [Text Fields and Naming](#text-fields-and-naming). <br>Examples: <ul><li>Broadway and East 22nd Street</li><li>Convention Center</li><li>Central Park South</li></ul> |
\-&nbsp;`short_name` | OPTIONAL | String | Short name or other type of identifier. |
\-&nbsp;`lat` | Yes | Latitude | Latitude of the station in decimal degrees. This field SHOULD have a precision of 6 decimal places (0.000001). See [Coordinate Precision](#coordinate-precision). |
\-&nbsp;`lon` | Yes | Longitude | Longitude of the station in decimal degrees. This field SHOULD have a precision of 6 decimal places (0.000001). See [Coordinate Precision](#coordinate-precision). |
\-&nbsp;`address` | OPTIONAL | String | Address (street number and name) where station is located. This MUST be a valid address, not a free-form text description. Example: 1234 Main Street |
\-&nbsp;`cross_street` | OPTIONAL | String | Cross street or landmark where the station is located. |
\-&nbsp;`region_id` | OPTIONAL | ID | Identifier of the region where station is located. See [system_regions.json](#system_regionsjson). |
\-&nbsp;`post_code` | OPTIONAL | String | Postal code where station is located. |
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
\-&nbsp;`is_charging_station` <br/>*(added in v2.3)* | OPTIONAL | Boolean | Does the station support charging of electric vehicles? <br /><br /> `true` - Electric vehicle charging is available at this station. <br /> `false` -  Electric vehicle charging is not available at this station. |
\-&nbsp;`rental_uris` <br/>*(added in v1.1)* | OPTIONAL | Object | Contains rental URIs for Android, iOS, and web in the `android`, `ios`, and `web` fields. See [examples](#examples) of how to use these fields and [supported analytics](#analytics). |
&emsp;\-&nbsp;`android` <br/>*(added in v1.1)* | OPTIONAL | URI | URI that can be passed to an Android app with an `android.intent.action.VIEW` Android intent to support Android Deep Links (https://developer.android.com/training/app-links/deep-linking). Please use Android App Links (https://developer.android.com/training/app-links) if possible so viewing apps do not need to manually manage the redirect of the user to the app store if the user does not have the application installed. <br><br>This URI SHOULD be a deep link specific to this station, and SHOULD NOT be a general rental page that includes information for more than one station. The deep link SHOULD take users directly to this station, without any prompts, interstitial pages, or logins. Make sure that users can see this station even if they never previously opened the application.  <br><br>If this field is empty, it means deep linking is not supported in the native Android rental app. <br><br>Note that the URI does not necessarily include the `station_id` for this station - other identifiers can be used by the rental app within the URI to uniquely identify this station. <br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>Android App Links example value: `https://www.example.com/app?sid=1234567890&platform=android` <br><br>Deep Link (without App Links) example value: `com.example.android://open.example.app/app?sid=1234567890` |
&emsp;\-&nbsp;`ios` <br/>*(added in v1.1)* | OPTIONAL | URI | URI that can be used on iOS to launch the rental app for this station. More information on this iOS feature can be found [here](https://developer.apple.com/documentation/uikit/core_app/allowing_apps_and_websites_to_link_to_your_content/communicating_with_other_apps_using_custom_urls?language=objc). Please use iOS Universal Links (https://developer.apple.com/ios/universal-links/) if possible so viewing apps do not need to manually manage the redirect of the user to the app store if the user does not have the application installed. <br><br>This URI SHOULD be a deep link specific to this station, and SHOULD NOT be a general rental page that includes information for more than one station.  The deep link SHOULD take users directly to this station, without any prompts, interstitial pages, or logins. Make sure that users can see this station even if they never previously opened the application.  <br><br>If this field is empty, it means deep linking is not supported in the native iOS rental app. <br><br>Note that the URI does not necessarily include the 'station_id' for this station - other identifiers can be used by the rental app within the URI to uniquely identify this station. <br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>iOS Universal Links example value: `https://www.example.com/app?sid=1234567890&platform=ios` <br><br>Deep Link (without Universal Links) example value: `com.example.ios://open.example.app/app?sid=1234567890` |
&emsp;\-&nbsp;`web` <br/>*(added in v1.1)* | OPTIONAL | URL | URL that can be used by a web browser to show more information about renting a vehicle at this station. <br><br>This URL SHOULD be a deep link specific to this station, and SHOULD NOT be a general rental page that includes information for more than one station.  The deep link SHOULD take users directly to this station, without any prompts, interstitial pages, or logins. Make sure that users can see this station even if they never previously opened the application.  <br><br>If this field is empty, it means deep linking is not supported for web browsers. <br><br>Example value: `https://www.example.com/app?sid=1234567890` |


### station_status.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`stations` | Yes | Array | Array that contains one object per station in the system as defined below. |
\-&nbsp;`station_id` | Yes | ID | Identifier of a station. See [station_information.json](#station_informationjson). |
\-&nbsp;`num_bikes_available` | Yes | Non-negative integer | Number of functional vehicles physically at the station that may be offered for rental. To know if the vehicles are available for rental, see `is_renting`. <br/><br/>If `is_renting` = `true`, this is the number of vehicles that are currently available for rent. If `is_renting` =`false`, this is the number of vehicles that would be available for rent if the station were set to allow rentals. |
\- `vehicle_types_available` <br/>*(added in v2.1)* | Conditionally REQUIRED | Array | REQUIRED if the [vehicle_types.json](#vehicle_typesjson) file has been defined. This field's value is an array of objects. Each of these objects is used to model the total number of each defined vehicle type available at a station. The total number of vehicles from each of these objects SHOULD add up to match the value specified in the `num_bikes_available`  field. |
&emsp;\- `vehicle_type_id` <br/>*(added in v2.1)* | Conditionally REQUIRED | ID | REQUIRED if the `vehicle_types_available` is defined. The `vehicle_type_id` of each vehicle type at the station as described in [vehicle_types.json](#vehicle_typesjson).  |
&emsp;\- `count` <br/>*(added in v2.1)* | Conditionally REQUIRED | Non-negative integer | The total number of available vehicles of the corresponding `vehicle_type_id`, as defined in [vehicle_types.json](#vehicle_typesjson), at the station. |
\-&nbsp;`num_bikes_disabled` | OPTIONAL | Non-negative integer | Number of disabled vehicles of any type at the station. Vendors who do not want to publicize the number of disabled vehicles or docks in their system can opt to omit station `capacity` (in [station_information.json](#station_informationjson), `num_bikes_disabled`, and `num_docks_disabled` *(as of v2.0)*. If station `capacity` is published, then broken docks/vehicles can be inferred (though not specifically whether the decreased capacity is a broken vehicle or dock). |
\-&nbsp;`num_docks_available` | Conditionally REQUIRED <br/>*(as of v2.0)* | Non-negative integer | REQUIRED except for stations that have unlimited docking capacity (for example, valet stations) *(as of v2.0)*. Number of functional docks physically at the station that are able to accept vehicles for return. To know if the docks are accepting vehicle returns, see `is_returning`. <br /><br/> If `is_returning` = `true`, this is the number of docks that are currently available to accept vehicle returns. If `is_returning` = `false`, this is the number of docks that would be available if the station were set to allow returns. |
\- `vehicle_docks_available` <br/>*(added in v2.1)* | Conditionally REQUIRED | Array | REQUIRED in feeds where the [vehicle_types.json](#vehicle_typesjson) is defined and where certain docks are only able to accept certain vehicle types. If every dock at the station is able to accept any vehicle type, then this field is not REQUIRED. This field's value is an array of objects. Each of these objects is used to model the number of docks available for certain vehicle types. The total number of docks from each of these objects SHOULD add up to match the value specified in the `num_docks_available` field. |
&emsp;\- `vehicle_type_ids` <br/>*(added in v2.1)* | Conditionally REQUIRED | Array | REQUIRED if `vehicle_docks_available` is defined. An array of strings where each string represents a `vehicle_type_id` that is able to use a particular type of dock at the station |
&emsp;\- `count` <br/>*(added in v2.1)* | Conditionally REQUIRED | Non-negative integer | REQUIRED if `vehicle_docks_available` is defined. The total number of available docks at the station, that can accept vehicles of the corresponding `vehicle_type_id`, in the `vehicle_type_ids` array. |
\-&nbsp;`num_docks_disabled` | OPTIONAL | Non-negative integer | Number of disabled dock points at the station. |
\-&nbsp;`is_installed` | Yes | Boolean | Is the station currently on the street?<br/><br/>`true` - Station is installed on the street.<br/>`false` - Station is not installed on the street.<br/><br/>Boolean SHOULD be set to `true` when equipment is present on the street. In seasonal systems where equipment is removed during winter, boolean SHOULD be set to `false` during the off season. May also be set to false to indicate planned (future) stations which have not yet been installed. |
\-&nbsp;`is_renting` | Yes | Boolean | Is the station currently renting vehicles? <br /><br />`true` - Station is renting vehicles. Even if the station is empty, if it would otherwise allow rentals, this value MUST be `true`.<br/>`false` - Station is not renting vehicles.<br/><br/>If the station is temporarily taken out of service and not allowing rentals, this field MUST be set to `false`.<br/><br/>If a station becomes inaccessible to users due to road construction or other factors this field SHOULD be set to `false`. Field SHOULD be set to `false` during hours or days when the system is not offering vehicles for rent. |
\-&nbsp;`is_returning` | Yes | Boolean | Is the station accepting vehicle returns? <br /><br />`true` - Station is accepting vehicle returns. Even if the station is full, if it would otherwise allow vehicle returns, this value MUST be `true`.<br /> `false` - Station is not accepting vehicle returns.<br/><br/>If the station is temporarily taken out of service and not allowing vehicle returns, this field MUST be set to `false`.<br/><br/>If a station becomes inaccessible to users due to road construction or other factors, this field SHOULD be set to `false`. |
\-&nbsp;`last_reported` | Yes | Timestamp | The last time this station reported its status to the operator's backend.


### free_bike_status.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`bikes` | Yes | Array | Array that contains one object per vehicle that is currently not part of an active rental, as defined below. |
\-&nbsp;`bike_id` | Yes | ID | Identifier of a vehicle. The `bike_id` identifier MUST be rotated to a random string after each trip to protect user privacy *(as of v2.0)*. Use of persistent vehicle IDs poses a threat to user privacy. The `bike_id` identifier SHOULD only be rotated once per trip. |
\-&nbsp;`lat` | Conditionally REQUIRED <br/>*(as of v2.1)* | Latitude | Latitude of the vehicle in decimal degrees. *(as of v2.1)* REQUIRED if `station_id` is not provided for this vehicle (free floating). This field SHOULD have a precision of 6 decimal places (0.000001). See [Coordinate Precision](#coordinate-precision). |
\-&nbsp;`lon` | Conditionally REQUIRED <br/>*(as of v2.1)* | Longitude | Longitude of the vehicle in decimal degrees. *(as of v2.1)* REQUIRED if `station_id` is not provided for this vehicle (free floating). This field SHOULD have a precision of 6 decimal places (0.000001). See [Coordinate Precision](#coordinate-precision). |
\-&nbsp;`is_reserved` | Yes | Boolean | Is the vehicle currently reserved? <br /><br /> `true` - Vehicle is currently reserved. <br /> `false` - Vehicle is not currently reserved. |
\-&nbsp;`is_disabled` | Yes | Boolean | Is the vehicle currently disabled? <br /><br /> `true` - Vehicle is currently disabled. <br /> `false` - Vehicle is not currently disabled.<br><br>This field is used to indicate vehicles that are in the field but not available for rental.  This may be due to a mechanical issue, low battery, etc. Publishing this data may prevent users from attempting to rent vehicles that are disabled and not available for rental. |
\-&nbsp;`rental_uris` <br/>*(added in v1.1)* | OPTIONAL | Object | JSON object that contains rental URIs for Android, iOS, and web in the `android`, `ios`, and `web` fields. See [examples](#examples) of how to use these fields and [supported analytics](#analytics). |
&emsp;\-&nbsp;`android` <br/>*(added in v1.1)* | OPTIONAL | URI | URI that can be passed to an Android app with an android.intent.action.VIEW Android intent to support Android Deep Links (https://developer.android.com/training/app-links/deep-linking). Please use Android App Links (https://developer.android.com/training/app-links) if possible, so viewing apps do not need to manually manage the redirect of the user to the app store if the user does not have the application installed. <br><br>This URI SHOULD be a deep link specific to this vehicle, and SHOULD NOT be a general rental page that includes information for more than one vehicle. The deep link SHOULD take users directly to this vehicle, without any prompts, interstitial pages, or logins. Make sure that users can see this vehicle even if they never previously opened the application. Note that as a best practice providers SHOULD rotate identifiers within deep links after each rental to avoid unintentionally exposing private vehicle trip origins and destinations.<br><br>If this field is empty, it means deep linking is not supported in the native Android rental app.<br><br>Note that the URI does not necessarily include the `bike_id` for this vehicle - other identifiers can be used by the rental app within the URI to uniquely identify this vehicle. <br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>Android App Links example value: `https://www.example.com/app?sid=1234567890&platform=android` <br><br>Deep Link (without App Links) example value: `com.example.android://open.example.app/app?sid=1234567890` |
&emsp;\-&nbsp;`ios` <br/>*(added in v1.1)* | OPTIONAL | URI | URI that can be used on iOS to launch the rental app for this vehicle. More information on this iOS feature can be found [here](https://developer.apple.com/documentation/uikit/core_app/allowing_apps_and_websites_to_link_to_your_content/communicating_with_other_apps_using_custom_urls?language=objc). Please use iOS Universal Links (https://developer.apple.com/ios/universal-links/) if possible, so viewing apps do not need to manually manage the redirect of the user to the app store if the user does not have the application installed. <br><br>This URI SHOULD be a deep link specific to this vehicle, and SHOULD NOT be a general rental page that includes information for more than one vehicle.  The deep link SHOULD take users directly to this vehicle, without any prompts, interstitial pages, or logins. Make sure that users can see this vehicle even if they never previously opened the application. Note that as a best practice providers SHOULD rotate identifiers within deep links after each rental to avoid unintentionally exposing private vehicle trip origins and destinations. <br><br>If this field is empty, it means deep linking is not supported in the native iOS rental app.<br><br>Note that the URI does not necessarily include the `bike_id` - other identifiers can be used by the rental app within the URL to uniquely identify this vehicle. <br><br>See the [Analytics](#analytics) section for how viewing apps can report the origin of the deep link to rental apps. <br><br>iOS Universal Links example value: `https://www.example.com/app?sid=1234567890&platform=ios` <br><br>Deep Link (without Universal Links) example value: `com.example.ios://open.example.app/app?sid=1234567890` |
&emsp;\-&nbsp;`web` <br/>*(added in v1.1)* | OPTIONAL | URL | URL that can be used by a web browser to show more information about renting a vehicle at this vehicle. <br><br>This URL SHOULD be a deep link specific to this vehicle, and SHOULD NOT be a general rental page that includes information for more than one vehicle.  The deep link SHOULD take users directly to this vehicle, without any prompts, interstitial pages, or logins. Make sure that users can see this vehicle even if they never previously opened the application. Note that as a best practice providers SHOULD rotate identifiers within deep links after each rental to avoid unintentionally exposing private vehicle trip origins and destinations.<br><br>If this field is empty, it means deep linking is not supported for web browsers. <br><br>Example value: `https://www.example.com/app?sid=1234567890` |
\- `vehicle_type_id` <br/>*(added in v2.1)* | Conditionally REQUIRED | ID | REQUIRED if the [vehicle_types.json](#vehicle_typesjson) file is defined. The `vehicle_type_id` of this vehicle, as described in [vehicle_types.json](#vehicle_typesjson).  |
\- `last_reported` <br/>*(added in v2.1)* | OPTIONAL | Timestamp | The last time this vehicle reported its status to the operator's backend. |
\- `current_range_meters` <br/>*(added in v2.1)* | Conditionally REQUIRED | Non-negative float | REQUIRED if the corresponding `vehicle_type` definition for this vehicle has a motor. This value represents the furthest distance in meters that the vehicle can travel with the vehicle's current charge or fuel (without recharging or refueling). Note that in the case of carsharing, the given range is indicative and can be different from the one displayed on the vehicle's dashboard. |
\- `current_fuel_percent` <br/>*(added in v2.3)*| OPTIONAL | Non-negative float | This value represents the current percentage, expressed from 0 to 1, of fuel or battery power remaining in the vehicle. |
\- `station_id` <br/>*(added in v2.1)* | Conditionally REQUIRED | ID | REQUIRED if the vehicle is currently at a station and the [vehicle_types.json](#vehicle_typesjson) file has been defined. Identifier referencing the `station_id` field in [station_information.json](#station_informationjson).  |
\- `home_station_id` <br/>*(added in v2.3)* | OPTIONAL | ID | The `station_id` of the station this vehicle must be returned to as defined in [station_information.json](#station_informationjson). |
\- `pricing_plan_id` <br/>*(added in v2.2)* | OPTIONAL | ID | The `plan_id` of the pricing plan this vehicle is eligible for as described in [system_pricing_plans.json](#system_pricing_plansjson). If this field is defined it supersedes `default_pricing_plan_id` in `vehicle_types.json`. This field SHOULD be used to override `default_pricing_plan_id` in `vehicle_types.json` to define pricing plans for individual vehicles when necessary. |
\- `vehicle_equipment`<br/>*(added in v2.3)* | OPTIONAL | Array | List of vehicle equipment provided by the operator in addition to the accessories already provided in the vehicle (field `vehicle_accessories` of `vehicle_types.json`) but subject to more frequent updates.<br/><br/>Current valid values are:<ul><li>`child_seat_a` _(Baby seat ("0-10kg"))_</li><li>`child_seat_b`	 _(Seat or seat extension for small children ("9-18 kg"))_</li><li>`child_seat_c`	_(Seat or seat extension for older children ("15-36 kg"))_</li><li>`winter_tires` 	_(Vehicle has tires for winter weather)_</li><li>`snow_chains`</li></ul> |
\- `available_until`<br/>*(added in v2.3)* | OPTIONAL |  Datetime | The date and time when any rental of the vehicle must be completed. The vehicle must be returned and made available for the next user by this time. If this field is empty, it indicates that the vehicle is available indefinitely.<br /><br /> This field SHOULD be published by carsharing or other mobility systems where vehicles can be booked in advance for future travel. |


### system_hours.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`rental_hours` | Yes | Array | Array of objects as defined below. The array MUST contain a minimum of one object identifying hours for every day of the week or a maximum of two for each day of the week  objects (one for each user type). |
\-&nbsp;`user_types` | Yes | Array | An array of `member` and/or `nonmember` value(s). This indicates that this set of rental hours applies to either members or non-members only. |
\-&nbsp;`days` | Yes | Array | An array of abbreviations (first 3 letters) of English names of the days of the week for which this object applies (for example, `["mon", "tue", "wed", "thu", "fri", "sat, "sun"]`). Rental hours MUST NOT be defined more than once for each day and user type. |
\-&nbsp;`start_time` | Yes | Time | Start time for the hours of operation of the system in the time zone indicated in [system_information.json](#system_informationjson). |
\-&nbsp;`end_time` | Yes | Time | End time for the hours of operation of the system in the time zone indicated in [system_information.json](#system_informationjson). |


### system_calendar.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`calendars` | Yes | Array | Array of objects describing the system operational calendar. A minimum of one calendar object is REQUIRED. If start and end dates are the same every year, then start_year and end_year SHOULD be omitted. |
\-&nbsp;`start_month` | Yes | Non-negative Integer | Starting month for the system operations (`1`-`12`). |
\-&nbsp;`start_day` | Yes | Non-negative Integer | Starting date for the system operations (`1`-`31`). |
\-&nbsp;`start_year` | OPTIONAL | Non-negative Integer | Starting year for the system operations. |
\-&nbsp;`end_month` | Yes | Non-negative Integer | Ending month for the system operations (`1`-`12`). |
\-&nbsp;`end_day` | Yes | Non-negative Integer | Ending date for the system operations (`1`-`31`). |
\-&nbsp;`end_year` | OPTIONAL | Non-negative Integer | Ending year for the system operations. |

### system_regions.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`regions` | Yes | Array | Array of objects as defined below. |
\-&nbsp;`region_id` | Yes | ID | Identifier for the region. |
\-&nbsp;`name` | Yes | String | Public name for this region. |


### system_pricing_plans.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`plans` | Yes | Array | Array of objects as defined below. |
\-&nbsp;`plan_id` | Yes | ID | Identifier for a pricing plan in the system. |
\-&nbsp;`url` | OPTIONAL | URL | URL where the customer can learn more about this pricing plan. |
\-&nbsp;`name` | Yes | String | Name of this pricing plan. |
\-&nbsp;`currency` | Yes | String | Currency used to pay the fare. <br /><br /> This pricing is in ISO 4217 code: http://en.wikipedia.org/wiki/ISO_4217 <br />(for example, `CAD` for Canadian dollars, `EUR` for euros, or `JPY` for Japanese yen.) |
\-&nbsp;`price` | Yes | Non-Negative float OR String | Fare price, in the unit specified by currency. If string, MUST be in decimal monetary value. <br/>*(added in v2.2)* Note: v3.0 will only allow non-negative float, therefore new implementations SHOULD be non-negative float.<br /><br />In case of non-rate price, this field is the total price. In case of rate price, this field is the base price that is charged only once per trip (typically the price for unlocking) in addition to `per_km_pricing` and/or `per_min_pricing`. |
\-&nbsp;`is_taxable` | Yes | Boolean | Will additional tax be added to the base price?<br /><br />`true` - Yes.<br />  `false` - No.  <br /><br />`false` MAY be used to indicate that tax is not charged or that tax is included in the base price. |
\-&nbsp;`description` | Yes | String | Customer-readable description of the pricing plan. This SHOULD include the duration, price, conditions, etc. that the publisher would like users to see. |
\-&nbsp;`per_km_pricing` <br/>*(added in v2.2)* | OPTIONAL | Array | Array of segments when the price is a function of distance traveled, displayed in kilometers.<br /><br />Total cost is the addition of `price` and all segments in `per_km_pricing` and `per_min_pricing`. If this array is not provided, there are no variable costs based on distance. |
&emsp;&emsp;\-&nbsp;`start` <br/>*(added in v2.2)* | Conditionally REQUIRED | Non-Negative Integer | REQUIRED if `per_km_pricing` is defined. The kilometer at which this segment rate starts being charged *(inclusive)*. |
&emsp;&emsp;\-&nbsp;`rate` <br/>*(added in v2.2)* | Conditionally REQUIRED | Float | REQUIRED if `per_km_pricing` is defined. Rate that is charged for each kilometer `interval` after the `start`. Can be a negative number, which indicates that the traveler will receive a discount. |
&emsp;&emsp;\-&nbsp;`interval` <br/>*(added in v2.2)* | Conditionally REQUIRED | Non-Negative Integer | REQUIRED if `per_km_pricing` is defined. Interval in kilometers at which the `rate` of this segment is either reapplied indefinitely, or if defined, up until (but not including) `end` kilometer.<br /><br />An interval of 0 indicates the rate is only charged once. |
&emsp;&emsp;\-&nbsp; `end` <br/>*(added in v2.2)* | OPTIONAL | Non-Negative Integer | The kilometer at which the rate will no longer apply *(exclusive)* for example, if `end` is `20` the rate no longer applies at 20.00 km.<br /><br /> If this field is empty, the price issued for this segment is charged until the trip ends, in addition to the cost of any subsequent segments. |
\-&nbsp;`per_min_pricing` <br/>*(added in v2.2)* | OPTIONAL | Array | Array of segments when the price is a function of time traveled, displayed in minutes.<br /><br />Total cost is the addition of `price` and all segments in `per_km_pricing` and `per_min_pricing`. If this array is not provided, there are no variable costs based on time. |
&emsp;&emsp;\-&nbsp;`start` <br/>*(added in v2.2)* | Conditionally REQUIRED | Non-Negative Integer | REQUIRED if `per_min_pricing` is defined. The minute at which this segment rate starts being charged *(inclusive)*. |
&emsp;&emsp;\-&nbsp;`rate` <br/>*(added in v2.2)* | Conditionally REQUIRED | Float | REQUIRED if `per_min_pricing` is defined.  Rate that is charged for each minute `interval` after the `start`. Can be a negative number, which indicates that the traveler will receive a discount. |
&emsp;&emsp;\-&nbsp;`interval` <br/>*(added in v2.2)* | Conditionally REQUIRED | Non-Negative Integer | REQUIRED if `per_min_pricing` is defined. Interval in minutes at which the `rate` of this segment is either reapplied indefinitely, or up until (but not including) the `end` minute, if `end` is defined.<br /><br />An interval of 0 indicates the rate is only charged once. |
&emsp;&emsp;\-&nbsp; `end` <br/>*(added in v2.2)* | OPTIONAL | Non-Negative Integer | The minute at which the rate will no longer apply  *(exclusive)* for example, if `end` is `20` the rate no longer applies after 19:59.<br /><br />If this field is empty, the price issued for this segment is charged until the trip ends, in addition to the cost of any subsequent segments. |
\-&nbsp;`surge_pricing` <br/>*(added in v2.2)* | OPTIONAL | Boolean | Is there currently an increase in price in response to increased demand in this pricing plan? If this field is empty, it means there is no surge pricing in effect.<br /><br />`true` - Surge pricing is in effect.<br />  `false` - Surge pricing is not in effect. |

### system_alerts.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`alerts` | Yes | Array | Array of objects each indicating a system alert as defined below. |
\-&nbsp;`alert_id` | Yes | ID | Identifier for this alert. |
\-&nbsp;`type` | Yes | Enum | Valid values are:<br /><br /><ul><li>`system_closure`</li><li>`station_closure`</li><li>`station_move`</li><li>`other`</li></ul> |
\-&nbsp;`times` | OPTIONAL | Array | Array of objects with the fields `start` and `end` indicating when the alert is in effect (for example, when the system or station is actually closed, or when a station is scheduled to be moved). |
&emsp;\-&nbsp;`start` | Conditionally REQUIRED | Timestamp | REQUIRED if `times` array is defined. Start time of the alert. |
&emsp;\-&nbsp;`end` | OPTIONAL | Timestamp | End time of the alert. If there is currently no end time planned for the alert, this can be omitted. |
\-&nbsp;`station_ids` | OPTIONAL | Array | If this is an alert that affects one or more stations, include their ID(s). Otherwise omit this field. If both `station_id` and `region_id` are omitted, this alert affects the entire system. |
\-&nbsp;`region_ids` | OPTIONAL | Array | If this system has regions, and if this alert only affects certain regions, include their ID(s). Otherwise, omit this field. If both `station_id`s and `region_id`s are omitted, this alert affects the entire system. |
\-&nbsp;`url` | OPTIONAL | URL | URL where the customer can learn more information about this alert. |
\-&nbsp;`summary` | Yes | String | A short summary of this alert to be displayed to the customer. |
\-&nbsp;`description` | OPTIONAL | String | Detailed description of the alert. |
\-&nbsp;`last_updated` | OPTIONAL | Timestamp | Indicates the last time the info for the alert was updated. |


### geofencing_zones.json

Field Name | REQUIRED | Type | Defines | Mapping Notes
---|---|---|---|---
`geofencing_zones` | Yes | GeoJSON FeatureCollection | Each geofenced zone and its associated rules and attributes is described as an object within the array of features, as follows. |
\-&nbsp;`type` | Yes | String | “FeatureCollection” (as per IETF [RFC 7946](https://tools.ietf.org/html/rfc7946#section-3.3)). |
\-&nbsp;`features` | Yes | Array | Array of objects as defined below. |
&emsp;\-&nbsp;`type` | Yes | String | “Feature” (as per IETF [RFC 7946](https://tools.ietf.org/html/rfc7946#section-3.3)). |
&emsp;\-&nbsp;`geometry` | Yes | GeoJSON MultiPolygon | A polygon that describes where rides might not be able to start, end, go through, or have other limitations. A clockwise arrangement of points defines the area enclosed by the polygon, while a counterclockwise order defines the area outside the polygon ([right-hand rule](https://tools.ietf.org/html/rfc7946#section-3.1.6)). All geofencing zones contained in this list are public (meaning they can be displayed on a map for public use). |
&emsp;\-&nbsp;`properties` | Yes | Object | Properties: As defined below, describing travel allowances and limitations. |
&emsp;&emsp;\-&nbsp;`name` | OPTIONAL | String | Public name of the geofencing zone. |
&emsp;&emsp;\-&nbsp;`start` | OPTIONAL | Timestamp | Start time of the geofencing zone. If the geofencing zone is always active, this can be omitted. |
&emsp;&emsp;\-&nbsp;`end` | OPTIONAL | Timestamp | End time of the geofencing zone. If the geofencing zone is always active, this can be omitted. |
&emsp;&emsp;\-&nbsp;`rules` | OPTIONAL | Array | Array that contains one object per rule as defined below. <br /><br /> In the event of colliding rules within the same polygon, the earlier rule (in order of the JSON file) takes precedence. <br> In the case of overlapping polygons, the combined set of rules associated with the overlapping polygons applies to the union of the polygons. In the event of colliding rules in this set, the earlier rule (in order of the JSON file) also takes precedence. |
&emsp;&emsp;&emsp;\-&nbsp;`vehicle_type_id` | OPTIONAL | Array | Array of IDs of vehicle types for which any restrictions SHOULD be applied (see vehicle type definitions in `vehicle_types.json`). If vehicle type IDs are not specified, then restrictions apply to all vehicle types. |
&emsp;&emsp;&emsp;\-&nbsp;`ride_allowed` | Conditionally REQUIRED | Boolean | REQUIRED if `rules` array is defined. Is the undocked (“free floating”) ride allowed to start and end in this zone? <br /><br /> `true` - Undocked (“free floating”) ride can start and end in this zone. <br /> `false` - Undocked (“free floating”) ride cannot start or end in this zone. |
&emsp;&emsp;&emsp;\-&nbsp;`ride_through_allowed` | Conditionally REQUIRED | Boolean | REQUIRED if `rules` array is defined. Is the ride allowed to travel through this zone? <br /><br /> `true` - Ride can travel through this zone. <br /> `false` - Ride cannot travel through this zone. |
&emsp;&emsp;&emsp;\-&nbsp;`maximum_speed_kph` | OPTIONAL | Non-negative Integer | What is the maximum speed allowed, in kilometers per hour? <br /><br /> If there is no maximum speed to observe, this can be omitted. |
&emsp;&emsp;&emsp;\-&nbsp;`station_parking`<br/>*(added in v2.3)* | OPTIONAL | Boolean | Can vehicles only be parked at stations defined in `station_information.json` within this geofence zone? <br /><br />`true` - Vehicles can only be parked at stations.  <br /> `false` - Vehicles may be parked outside of stations. |


## Deep Links

This sections describes how Deep Links can be costructed from `station_id` or `vehicle_id`.


