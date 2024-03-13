
# IXSI to GBFS Mapping

This document maps the IXSI API to GBFS.

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

This specification describes the mapping of [IXSI (Interface for X-Sharing Information) v5](https://carsharing.de/themen/carsharing-schnittstelle/einheitliche-carsharing-schnittstelle-ixsi-50)'s API to GBFS.

Various stadtmobil organizations and other car sharing operators use IXSI as booking API.

## General Information

The IXSI API is described via a [API documentation](https://carsharing.de/sites/default/files/uploads/ixsi-v5_docu_v0.9_bcs.pdf).

### Provider ID

To request a specific sharing provider, it's provider ID is required and needs to be configured in the provider config (see e.g. the [stadtmobiL-suedbaden config](https://github.com/mobidata-bw/x2gbfs/blob/a8bdd98ce51ca2a2aa0b008d2f906c5401fbd9eb/config/stadtmobil_suedbaden.json#L282))


### Example

The following fragment is an example of the IXSI static bookee document:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Ixsi xmlns="http://www.ixsi-schnittstelle.de/">
    <Response>
        <Transaction>
            <TimeStamp>2023-11-10T12:01:49</TimeStamp>
            <MessageID>1</MessageID>
        </Transaction>
        <CalcTime>PT0.407129976S</CalcTime>
        <BaseData>
            <Timestamp>2023-11-10T12:01:49</Timestamp>
            <Bookee>
                <ID>16198</ID>
                <Name>
                    <Text>Renault Zoe Reichweite &lt;280km (LÖ-MY 1122E)</Text>
                    <Language>DE</Language>
                </Name>
                <PlaceID>4912</PlaceID>
                <Class>mini</Class>
                <BookingHorizon>PT8784H</BookingHorizon>
                <BookingGrid>15</BookingGrid>
                <AttributeID>10532</AttributeID>
                <AttributeID>10539</AttributeID>
            </Bookee>
            <!-- ... -->
            <Place>
                <ID>3533</ID>
                <GeoPosition>
                    <Coord>
                        <Longitude>7.805383000</Longitude>
                        <Latitude>48.01163500</Latitude>
                    </Coord>
                </GeoPosition>
                <Capacity>2</Capacity>
                <Name>
                    <Text>Paduaallee / P+R Parkplatz</Text>
                    <Language>DE</Language>
                </Name>
                <ProviderID>64</ProviderID>
            </Place>
            <!-- ... -->
            <Attributes>
                <Text>
                    <Text>Winterreifen</Text>
                    <Language>DE</Language>
                </Text>
                <WithText>true</WithText>
                <Class>winter_tyres</Class>
                <ID>10522</ID>
            </Attributes>
        </BaseData>
    </Response>
</Ixsi>
```


### Attributes
Various properties of vehicles can be assigned to bookees. As they sometimes don't match exactly their GBFS counterpart, the following transformations from attribute/Class to gbfs accessories/equippment code are applied:

- `air_condition` is mapped as an `air_conditioning` entry in `vehicle_accessories`
- `manualgear` is mapped as an  `manual` in `vehicle_accessories`
- `allseasontyres` and `winter_tyres` are both mapped to an `winter_tires` entry in `vehicle_equipements`, as `allseasontyres` are not yet supported in GBFS.


## Open Issues or Questions

Open questions are now managed as [issues](https://github.com/mobidata-bw/x2gbfs/issues?q=is%3Aissue+is%3Aopen+label%3Aixsi). They should be tagged with `ixsi`.


## Files

### gbfs.json

Standard file, feed will be provided in feed language `de` only.

### gbfs_versions.json

Optional file, will not be provided. Only GBFSv2.3 supported.

### system_information.json

System information needs to be manually extracted from the provider's homepage, as IXSI does not provide this information.

### vehicle_types.json

IXSI API has no explicit endpoint for vehicle types, so they need to be collected from bookee's information.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`vehicle_type_id` | Extracted from the bookee name without license plate information
`form_factor` | `cargo_bicycle` for bookees with `Class = bike`, otherwise `car`
`rider_capacity`| extracted from attributes, assumed it is specified (which is only the case for a few vehicles)
`cargo_volume_capacity` | -
`cargo_load_capacity` | -
`propulsion_type` | If the `10532` (electric propulsion) attribute is specified (which is only the case for a few vehicles), `electric` will be used. Otherwise, if the bookee's name contains "km" or the bookee has a property `CurrentStateOfCharge`, `electric` is chosen. For vehicles with `form_factor=cargo_bicycle` (currently only one Urban Arrow bike of provider my-e-car), `electric_assist` is chosen. For all other `vehicle_types`, `combustion` is chosen.
`cargo_volume_capacity` | -
`eco_label` | -
`max_range_meters` | Extracted from bookee name, if specified. Otherwise set to `300000` (300km) for vehicle types wth form_factor `car`, `30000` for cargo_bicycles.
`name` | Extracted from the bookee name without license plate information
`vehicle_accessories` | `air_conditioning`, `cruise_control`, `automatic`, `manual` `navigation`, if correspondding attribute is set for bookee.
`g_CO2_km` | -
`vehicle_image` | -
`make` | first word of name
`model` | name without first word
`wheel_count` | `4` for cars, `2` for cargo_bicycle
`max_permitted_speed` | -
`rated_power` | -
`default_reserve_time` | -
`return_constraint`| `roundtrip_station`
`vehicle_assets`| -
`default_pricing_plan_id`| `stationwagon` if vehicle has attribute 'stationwagon' or 'stationwagonhighroof', else bookee's Class (`micro`, `mini`, `small`, `large`,`transporter`)
`pricing_plan_ids`| -


### station_information.json

JSON response for `/locations` contains array, each representing a station. Only those with the following attributes will be considered:

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `place/ID`
`name` | `place/Name`
`short_name` | -
`lat` | `place/GeoPosition/Coord/Latitude`
`lon` | `place/GeoPosition/Coord/Longitude`
`address` | -
`cross_street` | -
`region_id` | -
`post_code` | -
`rental_methods` | -
`is_virtual_station`| -
`station_area` | -
`parking_type` | -
`parking_hoop` | -
`contact_phone` | -
`capacity` | `place/Capacity`
`vehicle_capacity`  | -
`vehicle_type_capacity` | -
`is_valet_station`  | -
`is_charging_station` | -
`rental_uris` | for web, provider specific url like `https://ewi3-<provider>.cantamen.de/#{lat}-{lon}-17-0/place/{placeId}`


### station_status.json

Returns all stations of `/locations` endpoint, criteria see above (station_information.json)

#### Field Mappings

GBFS Field | Mapping
--- | ---
`station_id` | `place/ID`
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

Returns all bookees.

#### Field Mappings

GBFS Field | Mapping
--- | ---
`bike_id` |  `bookee/ID`
`lat` |  -
`lon` |  -
`is_reserved` | `True`, no live information available, so we set all to reserved
`is_disabled` | -
`rental_uris` | for web, provider specific url like `https://ewi3-<provider>.cantamen.de/#{lat}-{lon}-17-0/place/{placeId}/{vehicleId}`
`vehicle_type_id` | name without license plate information
`last_reported` |
`current_fuel_percent` | `CurrentStateOfCharge/100.0` if defined, else default value of 50%
`current_range_meters` | `max range meters * current_fuel_percent`
`station_id` | `bookee/placeID`
`home_station_id` | -
`pricing_plan_id` | -
`vehicle_equipment` | `winter_tires` if `winter_tyres` or `allseasontyres` in attributes (`allseasontyres` is currently not available in GBFS)
`available_until` | -


### system_hours.json

Not provided for now. system_hours would describe the whole system, not opening_hours per station.


### system_calendar.json

Not provided for now.


### system_regions.json

Not provided for now.


### system_pricing_plans.json

Information is manually extracted from the provider's website.


### system_alerts.json

Not provided for now.


### geofencing_zones.json

Not provided for now.
