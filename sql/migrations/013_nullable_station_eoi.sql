-- ===========================================================================
-- 013 — stations.station_eoi_code nullable
--
-- AQR3 STA_02 StationEoICode is the EEA/EIONET identifier for a monitoring
-- station. NOT NULL asserted that every station in Raven has one. That holds for
-- a network reporting to the EEA; it does not hold for the full NILU estate.
--
-- On the AirQUIS production database 633 of 749 stations have no ST_EOI, and they
-- are not an accident or a data-quality gap: they are industrial and internal
-- sites — Elkem Fiskå, Årdal Hydro, Trollhaugen, Pukkverk Stjørdal, indoor
-- measurement points — which are monitored operationally and are not part of any
-- EEA reporting obligation. An EOI code is *assigned* by EIONET, so there is
-- nothing to put in the column for them.
--
-- NOT NULL therefore left the same three bad options as 012 did for the
-- measurement columns: invent an identifier, assert someone else's, or refuse to
-- store the station. Inventing an EOI code is the worse version of the invented
-- eea_times '5min' row that 012's cleanup removed — a fabricated value in a field
-- whose whole purpose is to be a globally agreed identifier.
--
-- NULL means "this site has no EEA identifier", not "unknown". Consequences,
-- which mirror 012 exactly:
--
--   * Not reportable. StationEoICode is mandatory in the guide, so
--     core/reporting/aqr3/spec.py excludes NULL-EOI stations from STA and SPO.
--     A station with no identifier cannot appear in a report that is keyed by it.
--   * No sampling_point_reference_id for its sampling points: SPO_03 is
--     SPOref_<StationEoICode>_<PollutantId>_<idx> and there is no EoI to build it
--     from. That column is already nullable.
--
-- Observations for these sites still import and are visible in the UI. Only
-- reporting excludes them, which is correct.
--
-- Idempotent; reversible by re-adding NOT NULL once every station has an EOI.
-- ===========================================================================

begin;

alter table stations
    alter column station_eoi_code drop not null;

comment on column stations.station_eoi_code is
    'AQR3 STA_02 StationEoICode, assigned by EIONET. NULL for sites with no EEA '
    'identifier (industrial and internal monitoring points), which are not reportable: '
    'core/reporting/aqr3/spec.py excludes them from STA and SPO, and their sampling '
    'points get no sampling_point_reference_id.';

insert into schema_version (version, description)
values ('4.502.13',
        'stations.station_eoi_code nullable: an EOI code is assigned by EIONET, and 633 of '
        '749 AirQUIS production stations are industrial or internal sites that have none. '
        'NULL means "no EEA identifier applies"; such stations are excluded from AQR3 '
        'exports rather than being unstorable')
on conflict (version) do nothing;

commit;
