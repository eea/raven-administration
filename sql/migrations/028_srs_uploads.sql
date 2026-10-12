-- ===========================================================================
-- 028 — a Spatial representativeness area is saved whole, however large
--
-- The SR form uploaded a spatial file to /spatialrepresentativeness/parse, got its
-- points back as JSON, and sent them again with the save. Parse returned at most
-- 50,000, so a larger area -- a fine raster, or a polygon filled at 100 m -- was
-- saved cut short, with only "preview capped" on screen to say so.
--
-- Parse now keeps every point here, in EPSG:3035, under a random token, and
-- returns the token with a small preview sample. The save sends the token, and
-- the insert snaps the staged points onto the grid in SQL. They are kept in the
-- database rather than in the worker: dev-raven4 runs two API replicas, and the
-- save need not reach the one that parsed the file.
--
-- A save deletes the upload it used. Parse deletes uploads older than a day,
-- which are files picked and never saved.
--
-- Idempotent. schema.sql carries the same DDL and seeds this version.
-- ===========================================================================

begin;

create table if not exists srs_uploads
(
    token              varchar(32)  not null primary key,
    filename           varchar(255) not null,
    point_count        integer      not null,
    fill_resolution    integer,
    uploaded_at        timestamp    not null default current_timestamp
);

comment on table srs_uploads is 'A spatial file parsed for a Spatial representativeness area and not yet saved. Its points are in srs_upload_points; a save consumes it, and parse deletes those older than a day.';
comment on column srs_uploads.fill_resolution is 'The cell size, in metres, that the file''s polygons and lines were filled with; NULL when it held only points or a raster. A save at another resolution must parse the file again.';

create table if not exists srs_upload_points
(
    token varchar(32)       not null
        references srs_uploads (token) on delete cascade,
    x     double precision  not null,
    y     double precision  not null
);

comment on table srs_upload_points is 'The points of an srs_uploads file, in EPSG:3035 and not yet snapped: the resolution is the record''s, chosen when it is saved.';

create index if not exists idx_srs_upload_points_token
    on srs_upload_points (token);

insert into schema_version (version, description)
values ('4.502.28', 'srs_uploads: a parsed SR area is staged in full and saved by token, '
                    'not sent back capped at 50,000 points')
on conflict (version) do nothing;

commit;
