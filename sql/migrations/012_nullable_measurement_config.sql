-- ===========================================================================
-- 012 — sampling_points: pollutant_id, unit_id and time_resolution_id nullable
--
-- These three columns each point at an EEA vocabulary, and NOT NULL asserted
-- that every sampling point has a vocabulary value for all three. For a network
-- that reports only EEA-reportable air quality that holds. It does not hold for
-- the full NILU AirQUIS estate, and the vocabularies say so:
--
--   * aq/primaryObservation has ten concepts and NOTHING sub-hourly. A 60 s,
--     300 s or 900 s series has no EEA time resolution. `var` exists, but it
--     means "variable sample", which a fixed 5-minute series is not.
--   * uom/concentration has 36 concepts, all mass concentration. Of the units
--     NILU meteorology needs — m/s, deg, hPa, %, W/m2, degC — only `mm` is
--     present. Wind speed has no EEA concentration unit, because it is not a
--     concentration.
--   * aq/pollutant has 678 concepts and still lacks local components; PM Coarse
--     (which AirQUIS maps to 165) is not among them.
--
-- NOT NULL therefore left three bad options: invent vocabulary rows, assert a
-- value that is factually wrong, or refuse to store the series. All three were
-- tried in this codebase. eea_times accumulated nine rows from uom/time — a
-- different vocabulary — plus a hand-made '5min'; eea_pollutants accumulated 21
-- invented 999xxx meteo rows. The rule now is that eea_* tables contain the EEA
-- vocabulary and nothing else, which requires these columns to admit "no EEA
-- value applies".
--
-- NULL is not a data-quality escape hatch: it is a statement that no vocabulary
-- term exists. What the instrument actually measured is recorded by the
-- sampling-point-extended plugin (plugin_sp_extended.timestep / .unit /
-- .plugin_pollutant_id), so nothing is lost — it just stops being expressed as a
-- vocabulary value it is not.
--
-- AQR3 is unaffected: all three are mandatory in the reporting guide, and that
-- is enforced where it belongs, at export. core/reporting/aqr3/spec.py filters
-- `pollutant_id > 0` (NULL > 0 is NULL, so these rows drop out), and OMR reaches
-- unit and time resolution through INNER JOINs, which excludes them too. A
-- series with no EEA vocabulary value is not reportable and is now simply
-- absent from the CSVs, rather than being unstorable.
--
-- Nothing is dropped and nothing is rewritten, so this is reversible by
-- re-adding NOT NULL once no NULLs remain. Idempotent: DROP NOT NULL on a column
-- that is already nullable is a no-op in PostgreSQL.
-- ===========================================================================

begin;

alter table sampling_points
    alter column pollutant_id drop not null;

alter table sampling_points
    alter column unit_id drop not null;

alter table sampling_points
    alter column time_resolution_id drop not null;

comment on column sampling_points.pollutant_id is
    'AQR3 SPO_04 PollutantId -> eea_pollutants. NULL when the component has no EEA '
    'pollutant code; the local component is then identified by '
    'plugin_sp_extended.plugin_pollutant_id (nilu-pollutants plugin). NULL is not '
    'reportable and is excluded from every AQR3 table.';

comment on column sampling_points.unit_id is
    'AQR3 OMR_07 Unit -> eea_concentrations. NULL when the measured quantity is not a '
    'concentration and so has no uom/concentration term (wind speed, temperature, '
    'pressure...); the real unit is then in plugin_sp_extended.unit.';

comment on column sampling_points.time_resolution_id is
    'AQR3 OMR_11 TimeResolution -> eea_times. NULL when the sampling interval has no '
    'aq/primaryObservation term — the vocabulary has nothing sub-hourly — in which case '
    'the true interval in seconds is in plugin_sp_extended.timestep.';

insert into schema_version (version, description)
values ('4.502.12',
        'sampling_points.pollutant_id / unit_id / time_resolution_id nullable: the EEA '
        'vocabularies have no term for sub-hourly resolutions, non-concentration units or '
        'local components, so NULL now means "no vocabulary value applies" and the real '
        'value lives in plugin_sp_extended. AQR3 mandatory-ness is enforced at export')
on conflict (version) do nothing;

commit;
