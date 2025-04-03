# Changelog

The changelog lists most feature changes between each release. Search GitHub issues and pull requests for smaller issues.

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
