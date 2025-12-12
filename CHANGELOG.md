# Changelog

The changelog lists most feature changes between each release. Search GitHub issues and pull requests for smaller issues.

## 2025-12-12

- Breaking: remove MOQO providers `coono` and `gmuend_bewegt`
- fix: last_reported timezone now has timezone appended

## 2025-11-26

- fix: lastUpdated timezone is now formatted with colon

## 2025-11-19

- Breaking: Switches output format to [GBFSv3](https://github.com/MobilityData/gbfs/blob/v3.0/gbfs.md). For differences to [v2](https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md), check MobilityData's [migration guide](https://mobilitydata.org/how-to-upgrade-to-gbfs-v3-0/). If you intend to generate v2 feeds, you'll need to declare a `"x2gbfs": { "gbfs_version": 2}` section in those feed configs. For existing feed configs in this project, this has been added for `free2move_stuttgart` and `alpsgo` only.
  Note: in consequence of this switch, feed configs might require some adjustments. x2gbfs tries to convert these automatically but check for warnings which might highlight recommended changes.

## 2025-11-17

- add Cantamen provider `conficars_ulm`

## 2025-10-20

- set `privacy_last_updated` for feeds with `privacy_url`

## 2025-10-06

- add MOQO provider `stadtwerke_wertheim`

## 2025-09-26

- add MOQO provider `seefahrer_ecarsharing`

## 2025-09-09

- fix: MOQO provider `einfach_unterwegs`: detect cargo bicycle by name

## 2025-09-05

- add MOQO provider `einfach_unterwegs`

## 2025-08-21

- handle websocket InvalidMessage exceptions
- fix: MOQO provider: for stations without vehicles, `vehicle_types_available` was dict, now it's empty list

## 2025-08-11
- add moqo provider `ford_carsharing_autohausbaur`

## 2025-07-16
- add (Fleetster-based) mikar carsharing service. With this change, the Deer provider code has been generalized to `FleetsterProvider` so other Fleetster based car sharing providers should be able to reuse it via subclassing.
- change custom `station_information` property from `_city` to `city` for cambio and deer, to unify across different providers.

## 2025-07-04
- correct `per_min_pricing`, `per_km_pricing` for various providers

## 2025-07-03
- add cantamen provider `swu2go`

## 2025-06-25
- update teilauto_neckar-alb pricing

## 2025-06-23:
- update flinkster pricing
- make moqo provider robust against unknown car_type values
- skip gruene-flotte_freiburg free floating stations

## 2025-06-06:
- flinkster_carsharing fix: pricing plans for `other`

## 2025-05-23
- add moqo provider `lara_to_go`

## 2025-05-06
- feat: add support for "GBFS-Light", a single file json format suggested by the city of Herrenberg to provide static bikesharing data via a single JSON file.
- providers: config for new systems `herrenberg_lastenrad`, `herrenberg_alf`, `herrenberg_guelf`, `herrenberg_fare`.
- refactor: `pricing_plan`, `system_information` and `alerts` data retrieval moved form `GbfsWriter` to Provider, so these can return dynamic information. Per default, these feeds are still retrieved from the feed config.
- set deer return_constraint to `any_station`, requested by https://github.com/mobidata-bw/x2gbfs/issues/236

## 2025-04-08
- update gruene-flotte_freiburg pricing

## 2025-04-03
- fix: set default value for `deer` hasPublicCarsharing

## 2025-03-28
- set free2move return_constraint to `hybrid`
- remove zeag_energie provider

## 2025-03-13
- transform coono into static feed
- remove voi_raumobil provider

## 2025-03-03
- fix: update `deer` pricing plans
- moved (optional) feed config property `ttl` to `x2gbfs` section.
- add new option `useCustomBaseUrl` option (`boolean`, default is `False`), which can be configured per feed in the config section (e.g. `'x2gbfs: { "useCustomBaseUrl": True }`). If set, instead of x2gbfs parameter `baseUrl` the optional parameter `customBaseUrl` is used in gbfs.json`
- make FREE2MOVE_BASE_URL configurable (must now be provided as env var for free2move providers)
- round vehicle and station coords to at most six decimal places
- fix: `free2move_stuttgart` pricing plan, color naming, range and fuel level issues
- add MOQO provider coono. the MOQO converter still must be extended to support static data

## 2024-12-19
- rename Cantamen provider stadtmobil_suedbaden to naturenergie_sharing and update it's system / pricing information
- add Cantamen provider teilauto_schwaebisch_hall
- remove flinkster provider

## 2024-12-18
- add `Free2moveProvider` and feed `free2move_stuttgart`.

## 2024-12-11
- add MOQO providers oberschwabenmobil, gmuend_beweg

## 2024-11-29
- add CambioProvider and feed `cambio_aachen`.

## 2024-11-26
- add MOQO provider flinkster_carsharing
- use latest-parking cache for MOQO provider cars

## 2024-11-12
- add Cantamen provider gruene-flotte_freiburg

## 2024-10-30
- add Cantamen provider oekostadt_renningen
- extend Cantamen provider stadtmobil_suedbaden with pricing for bookee class 'bike'

## 2024-10-22
- add MOQO provider zeag_energie
- change pricing for MOQO provider stadtwerk_tauberfranken

## 2024-10-01
- add Cantamen provider teilauto_biberach

## 2024-09-24
- log timeout errors as error without stacktrace
- add Cantamen provider teilauto_neckar-alb

## 2024-09-10
- add Flinkster provider

## 2024-07-23
- add Cantamen provider stadtmobil_rhein-neckar, ignore its bookees having a pool name instead of a vehicle name
- stabilize cantamen providers against attributes data error

## 2024-07-03
- add pricing  plans for my-e-car e-carGOsharing
- fix: for some feeds, the vehicle_type.return_constraint was mis-spelled and is now fixed. (https://github.com/mobidata-bw/x2gbfs/pull/129)

## 2024-06-07
- add discovery uris for `stadtwerk_tauberfranken` (https://github.com/mobidata-bw/x2gbfs/commit/8f1f026e7f2132fae30de2c450965df0746bbbdd)
- add additional pricing plans for cantamen based providers (#117)
- fix: deer vehicles with missing extended properties are supported now, vehicles that can't be parsed from source will be ignored and a warning reported (#116)

## 2024-06-03
- add deeplinks for MOQO based providers, i.e. `stadtwerk_tauberfranken`

## 2024-05-02
- fix: remove plus and minus (-+) chars from cantamen vehicle type ids to workaround lamassu id restriction

## 2024-04-29
- fix: for deer, ignore inactive bookings (fixes #132)
- add new feed stadtmobil_karlsruhe (#97)
