# Changelog

All notable changes to this project will be documented in this file.  
Changes before version 3.1.0 is not included

## [latest commits]

- Added variable for container name in docker-compose file

## [3.1.1] - 2024-06-28

### Fixed

- The call to Dataflows.get_dataflows() is replaced with Dataflows.get_xml()

## [3.1.0] - 2024-05-15

### Added

- A column **_use_in_public_api_** in samplingpoints table that controls whether the samplingpoint should be exposed when using the [public api](https://git.nilu.no/raven/raven-public-api/)
- A [sql file](sql/use_in_public_api.sql) required to be run in order for this version to work
