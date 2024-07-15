# Changelog

The changelog lists most feature changes between each release. Search GitHub issues and pull requests for smaller issues.

## [Unreleased]
- add Cantamen provider stadtmobil_rhein-neckar
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
