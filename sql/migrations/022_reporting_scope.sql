-- ===========================================================================
-- 022 — stations.report_to_eea and sampling_points.report_to_eea
--
-- Raven is a general air quality system, and most of what it holds is not part
-- of an EEA reporting obligation. Until now nothing said so: scope was inferred
-- from two identifier columns in core/reporting/aqr3/spec.py --
--
--     a station is reported when station_eoi_code IS NOT NULL
--     a sampling point is reported when pollutant_id > 0
--
-- -- and 013 and 012 wrote that inference down as the intended meaning of NULL.
-- It is a reasonable reading of the data and it is wrong in both directions.
--
-- IT LETS INTERNAL SITES THROUGH. An EoI code is assigned by EIONET, and a site
-- keeps it after it leaves the programme; a site can also acquire one for
-- reasons of its own. The 2026-09-09 export shipped two stations and five
-- sampling points belonging to a network named "NILU internal (no Oracle
-- network)", because those two stations happen to carry EoI codes.
--
-- IT CANNOT BE ACTED ON. 013 made the column nullable so an out-of-scope station
-- could be stored, but the write path never followed: StationModel declares
-- station_eoi_code as `str` and stations/pageOptions.js declares it required, so
-- until the change that accompanies this migration nobody could register a
-- station without one. The predictable result is invented identifiers -- 66 of
-- 174 stations on the local development database carry codes of the form
-- `NILU-1002 Gvarv`, every one of which passes the reportability test today.
--
-- AND IT CONFLATES TWO DIFFERENT FACTS. A NULL identifier means both "we do not
-- report this site" and "somebody has not filled this in yet", which are not the
-- same thing and want opposite responses.
--
-- So intent gets a column of its own, and the identifier goes back to being an
-- identifier:
--
--     report_to_eea       intent      -- a decision an operator makes
--     station_eoi_code    capability  -- an identifier AQR3 needs to express the row
--     pollutant_id        capability  -- likewise
--
-- and the export is the conjunction. Both halves are still required: a station
-- marked for reporting that has no EoI code still cannot appear in a submission
-- keyed on it. What changes is that such a station is now a visible discrepancy
-- rather than an ordinary silent omission -- /api/dataflow/scope reports it.
--
-- INHERITANCE IS BY CONJUNCTION, NOT BY COPYING. A sampling point is exported
-- when its own flag and its station's are both set, so switching a station off
-- takes its sampling points with it, and a single series can still be taken out
-- on its own -- a research instrument or a meteorological parameter colocated at
-- a reporting station. Nothing has to be cascaded on write, and no row can drift
-- out of agreement with its station.
--
-- THE BACKFILL REPRODUCES TODAY'S OUTPUT EXACTLY. Stations inherit
-- `station_eoi_code IS NOT NULL`, which is the predicate being replaced, so the
-- first export after this migration is byte-identical and the new flag changes
-- nothing until somebody uses it. Sampling points keep the `true` default: a
-- series at a reporting station is reported unless someone says otherwise.
--
-- Clearing the fabricated EoI codes is deliberately NOT part of this migration.
-- Destroying identifiers is not reversible and those rows are one deployment's
-- data accident, so it runs on demand from sql/cleanup_fabricated_eoi.py, which
-- archives what it clears.
--
-- Idempotent; a no-op on a fresh install, where schema.sql already declares both
-- columns and seeds this version.
-- ===========================================================================

begin;

alter table stations
    add column if not exists report_to_eea boolean not null default true;

alter table sampling_points
    add column if not exists report_to_eea boolean not null default true;

-- Only on the first run: `add column ... default true` has already filled every
-- row, so re-running must not overwrite a decision an operator has since made.
-- The guard is the migration's own presence in schema_version, which
-- apply_migrations.py checks before executing this file at all; belt and braces
-- here because the file is also runnable by hand.
do $$
begin
    if not exists (select 1 from schema_version where version = '4.502.22') then
        update stations set report_to_eea = (station_eoi_code is not null);
        raise notice '022: % of % stations marked for EEA reporting (those with an EoI code)',
            (select count(*) from stations where report_to_eea),
            (select count(*) from stations);
    else
        raise notice '022: already applied, leaving report_to_eea as it stands';
    end if;
end $$;

comment on column stations.report_to_eea is
    'Intent, not capability: true when this site is part of the EEA reporting obligation. '
    'Distinct from station_eoi_code, which is the identifier EIONET assigned and which '
    'AQR3 additionally requires -- a station is exported only when both hold. Backfilled '
    'by migration 022 from station_eoi_code IS NOT NULL.';

comment on column sampling_points.report_to_eea is
    'Intent, not capability: true when this series is part of the EEA reporting '
    'obligation. ANDed with the station''s own flag, so a station switched off takes its '
    'sampling points with it; set false on its own for a series that is not reported from '
    'a station that is -- a colocated research instrument, a meteorological parameter.';

insert into schema_version (version, description)
values ('4.502.22',
        'stations.report_to_eea and sampling_points.report_to_eea: EEA reporting scope '
        'becomes an explicit decision rather than an inference from whether an EoI code '
        'or an EEA pollutant happens to be present. Raven holds industrial, internal and '
        'research sites that are not reported, and could neither express that nor store a '
        'station without an invented identifier. Backfilled from station_eoi_code IS NOT '
        'NULL so the first export after this migration is unchanged')
on conflict (version) do nothing;

commit;
