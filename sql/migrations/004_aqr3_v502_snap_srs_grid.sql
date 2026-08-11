-- ===========================================================================
-- 004 — AQR3 v5.02: align srs_inline column types and snap cells to the grid
--
-- Two fixes for databases where srs_inline came from the NILU-only
-- sr_area_inline (created by sql/migrate_airquis.py):
--
-- 1. Column types. Migration 002 renames the table, but its
--    `create table if not exists srs_inline` is a no-op when the table already
--    exists, so the old types survived: x/y as numeric and spatial_resolution
--    as varchar(20). AQR3 declares SRI_03/04 as bigint and SRI_05 as int.
--
-- 2. Grid snapping. The SR ingest already reprojected to EPSG:3035 but stored
--    the raw reprojected floats. AQR3 identifies a cell by its lower-left
--    origin, so an unsnapped coordinate does not line up with the EEA's own
--    gridding and the SRI key (CountryCode, SRSApplicationId, X, Y) cannot be
--    cross-checked. New uploads are snapped by core/reporting/aqr3/grid.py;
--    this brings older rows forward. Floor, not round, to match
--    to_inspire_grid().
--
-- Idempotent: re-running changes nothing.
-- ===========================================================================

begin;

-- 1. Types. Cast through numeric so a varchar resolution converts cleanly, and
--    floor x/y on the way to bigint rather than letting the cast round.
do
$$
    begin
        if exists (select 1 from information_schema.columns
                   where table_name = 'srs_inline' and column_name = 'spatial_resolution'
                     and data_type <> 'integer')
        then
            alter table srs_inline
                alter column spatial_resolution type integer
                    using nullif(trim(spatial_resolution::text), '')::numeric::integer;
        end if;

        if exists (select 1 from information_schema.columns
                   where table_name = 'srs_inline' and column_name = 'x'
                     and data_type <> 'bigint')
        then
            alter table srs_inline
                alter column x type bigint using floor(x::numeric)::bigint,
                alter column y type bigint using floor(y::numeric)::bigint;
        end if;
    end
$$;

-- 2. Snapping.
do
$$
    declare
        unsnappable integer;
        snapped     integer;
    begin
        -- Rows with no resolution cannot be placed on a grid at all.
        select count(*) into unsnappable
        from srs_inline
        where spatial_resolution is null
           or spatial_resolution not in (10, 100, 1000, 10000);

        if unsnappable > 0 then
            raise warning
                'srs_inline: % row(s) have no usable spatial_resolution and were left unsnapped. '
                'They will not pass AQR3 QC. Inspect with: SELECT DISTINCT spatial_representativeness_id, '
                'spatial_resolution FROM srs_inline WHERE spatial_resolution IS NULL OR '
                'spatial_resolution NOT IN (10,100,1000,10000);',
                unsnappable;
        end if;

        with updated as (
            update srs_inline
            set x = floor(x::numeric / spatial_resolution) * spatial_resolution,
                y = floor(y::numeric / spatial_resolution) * spatial_resolution
            where spatial_resolution in (10, 100, 1000, 10000)
              and (x <> floor(x::numeric / spatial_resolution) * spatial_resolution
                or y <> floor(y::numeric / spatial_resolution) * spatial_resolution)
            returning 1)
        select count(*) into snapped from updated;

        raise notice 'srs_inline: snapped % row(s) to the INSPIRE grid', snapped;
    end
$$;

-- Snapping can collapse distinct source points onto one cell. AQR3 keys SRI on
-- (SRSApplicationId, X, Y), so drop the duplicates that snapping created,
-- keeping the lowest id.
delete from srs_inline a
using srs_inline b
where a.id > b.id
  and a.spatial_representativeness_id = b.spatial_representativeness_id
  and a.x = b.x
  and a.y = b.y
  and a.spatial_resolution = b.spatial_resolution;

insert into schema_version (version, description)
values ('5.0.0-snapgrid',
        'AQR3 v5.02: snap pre-existing srs_inline cells to the EPSG:3035 INSPIRE grid and de-duplicate')
on conflict (version) do nothing;

commit;
