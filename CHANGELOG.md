# Changelog

All notable changes to this project will be documented in this file.  
Changes before version 3.1.0 is not included

## [3.3.1] - 2025-05-15

### Fixes

- A bug in calculating coverage when pre generating aggregations. Specifically, when timestep is bigger than the number of seconds in an aggregation. ie hourly aggregation with daily values.
- A [sql file](sql/pre_aggregates.sql) required to be rerun to fix the issue.

## [3.3.0] - 2025-05-15

### Added

- Convertion: Do not convert data if validation flag is below (invalid) 0 and values are -9900,-990 or -999

## [3.2.4] - 2025-05-07

### Fixed

- Version mixup fix
- Convertions between numby and native types

## [3.2.2] - 2025-05-05

### Fixed

- Handling empty dataset when generating attainment
- Rounding issue on None values

## [3.2.0]

- Added option to see raw data in historical data module
- Added experimental generation of G. To enable it, add `?experimental=true` to `attainments` url
- Added a notification at the top of the menu when a new version is available

## [3.1.4] - 2024-10-24

### Added

- A technical overview. See [file here](guides/technical_overview.md)
- Meteo components to the eea_pollutants table.
- A [sql file](sql/meteo.sql) required to be run in order for meteo components to be available.

## [3.1.3] - 2024-09-27

### Added

- Added a new guide explaing how to get E2a dataflow

### Fixed

- Make sure epoch dates from "fill in missing" is int not float. It sometimes causes an error on import.

## [3.1.2] - 2024-09-26

### Added

- Added variable for container name in docker-compose file
- Exclude -9900 values, even if "include invalid values" is enabled in "historical data" module. The change is in Mean class, so it may affect others

## [3.1.1] - 2024-06-28

### Fixed

- The call to Dataflows.get_dataflows() is replaced with Dataflows.get_xml()

## [3.1.0] - 2024-05-15

### Added

- A column **_use_in_public_api_** in samplingpoints table that controls whether the samplingpoint should be exposed when using the [public api](https://git.nilu.no/raven/raven-public-api/)
- A [sql file](sql/use_in_public_api.sql) required to be run in order for this version to work
