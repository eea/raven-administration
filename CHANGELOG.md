# Changelog

All notable changes to this project will be documented in this file.  
Changes before version 3.1.0 is not included

## [3.1.2] - 2024-09-26

- Added variable for container name in docker-compose file
- Exclude -9900 values, even if "include invalid values" is enabled in "historical data" module. The change is in Mean class, so it may affect others

## [3.1.1] - 2024-06-28

### Fixed

- The call to Dataflows.get_dataflows() is replaced with Dataflows.get_xml()

## [3.1.0] - 2024-05-15

### Added

- A column **_use_in_public_api_** in samplingpoints table that controls whether the samplingpoint should be exposed when using the [public api](https://git.nilu.no/raven/raven-public-api/)
- A [sql file](sql/use_in_public_api.sql) required to be run in order for this version to work
