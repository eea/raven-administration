-- ===========================================================================
-- 032 — seed the statistics configuration on a database that has none
--
-- The Statistics page lists the pollutants and aggregation processes in `statistics`.
-- sql/statistics.sql was its only seed, and it could not run on v4: it named a v3
-- `pollutant_uri` column and passed URIs. The migrate wizard copies the table from
-- the v3 source and nothing else, so a database whose source had no rows -- Malta,
-- now dev-raven4 -- ended up empty, and the page offered nothing.
--
-- Only when the table is empty. A database that has its own configuration
-- (raven_local and raven-airquis carry 77 rows copied from v3) keeps it as it is.
--
-- The rows are sql/statistics.sql's, which tests/unit/test_statistics_seed.py keeps
-- identical. Pairs whose pollutant or aggregation process is missing are skipped
-- rather than failing the migration, which would stop the API pods from starting.
-- ===========================================================================

begin;

insert into statistics (pollutant_id, aggregation_process_id, directive_2008_50,
                        directive_2024_2881)
select v.pollutant_id, v.aggregation_process_id, v.directive_2008_50, v.directive_2024_2881
  from (values
          (   1, 'winter-avg',              true,  true),
          (   7, 'AOT40c',                  true,  true),
          (   7, 'AOT40c-P5Y',              true,  true),
          (   1, 'P1Y',                     true,  true),
          (   7, 'P1Y',                     true,  true),
          (   5, 'P1Y',                     true,  true),
          (   8, 'P1Y',                     true,  true),
          (   9, 'P1Y',                     true,  true),
          (  10, 'P1Y',                     true,  true),
          (  38, 'P1Y',                     true,  true),
          (6001, 'P1Y',                     true,  true),
          (   1, 'P1Y-hr-max',              true,  true),
          (   7, 'P1Y-hr-max',              true,  true),
          (   5, 'P1Y-hr-max',              true,  true),
          (   8, 'P1Y-hr-max',              true,  true),
          (   9, 'P1Y-hr-max',              true,  true),
          (  10, 'P1Y-hr-max',              true,  true),
          (  38, 'P1Y-hr-max',              true,  true),
          (6001, 'P1Y-hr-max',              true,  true),
          (   1, 'P1Y-hr-min',              true,  true),
          (   7, 'P1Y-hr-min',              true,  true),
          (   5, 'P1Y-hr-min',              true,  true),
          (   8, 'P1Y-hr-min',              true,  true),
          (   9, 'P1Y-hr-min',              true,  true),
          (  10, 'P1Y-hr-min',              true,  true),
          (  38, 'P1Y-hr-min',              true,  true),
          (6001, 'P1Y-hr-min',              true,  true),
          (   1, 'P1Y-day-max',             true,  true),
          (   7, 'P1Y-day-max',             true,  true),
          (   5, 'P1Y-day-max',             true,  true),
          (   8, 'P1Y-day-max',             true,  true),
          (   9, 'P1Y-day-max',             true,  true),
          (  10, 'P1Y-day-max',             true,  true),
          (  38, 'P1Y-day-max',             true,  true),
          (6001, 'P1Y-day-max',             true,  true),
          (   1, 'P1Y-day-min',             true,  true),
          (   7, 'P1Y-day-min',             true,  true),
          (   5, 'P1Y-day-min',             true,  true),
          (   8, 'P1Y-day-min',             true,  true),
          (   9, 'P1Y-day-min',             true,  true),
          (  10, 'P1Y-day-min',             true,  true),
          (  38, 'P1Y-day-min',             true,  true),
          (6001, 'P1Y-day-min',             true,  true),
          (   1, 'P1Y-P1D-per99',           true,  true),
          (   7, 'P1Y-P1D-per99',           true,  true),
          (   5, 'P1Y-P1D-per99',           true,  true),
          (   8, 'P1Y-P1D-per99',           true,  true),
          (  10, 'P1Y-P1D-per99',           true,  true),
          (6001, 'P1Y-P1D-per99',           true,  true),
          (6001, 'P1Y-3daysAbove50',       false,  true),
          (   5, 'P1Y-3daysAbove90',       false,  true),
          (   1, 'P1Y-daysAbove125',        true, false),
          (6001, 'P1Y-daysAbove25',        false,  true),
          (  10, 'P1Y-daysAbove4',         false,  true),
          (   5, 'P1Y-daysAbove45',        false,  true),
          (   5, 'P1Y-daysAbove50',         true, false),
          (   8, 'P1Y-daysAbove50',        false,  true),
          (   1, 'P1Y-daysAbove50',        false,  true),
          (6001, 'P1Y-daysAbove50',        false,  true),
          (   5, 'P1Y-daysAbove90',        false,  true),
          (   7, 'P1Y-dmaxAbove100',       false,  true),
          (   7, 'P1Y-dmaxAbove120',        true, false),
          (   8, 'P1Y-3hAbove200',         false,  true),
          (   1, 'P1Y-3hAbove350',         false,  true),
          (   8, 'P1Y-3hAbove400',          true, false),
          (   1, 'P1Y-3hAbove500',          true, false),
          (  10, 'P1Y-8hdmxAbove10',        true,  true),
          (   8, 'P1Y-hrsAbove150',        false,  true),
          (   7, 'P1Y-hrsAbove180',         true,  true),
          (   8, 'P1Y-hrsAbove200',         true,  true),
          (   7, 'P1Y-hrsAbove240',         true,  true),
          (   1, 'P1Y-hrsAbove275',        false,  true),
          (   1, 'P1Y-hrsAbove350',         true,  true),
          (   7, 'P1Y-dmax-per99',         false,  true),
          (   7, 'P3Y-dmaxAbove120',        true,  true),
          (   7, 'SOMO10',                  true,  true),
          (   7, 'SOMO35',                  true,  true)
       ) as v(pollutant_id, aggregation_process_id, directive_2008_50, directive_2024_2881)
 -- Only pairs whose vocabulary rows exist: a missing pollutant or aggregation process
 -- would otherwise fail the whole statement on its foreign key.
 where exists (select 1 from eea_pollutants p where p.id = v.pollutant_id)
   and exists (select 1 from eea_aggregationprocess a where a.id = v.aggregation_process_id)
   and not exists (select 1 from statistics s
                    where s.pollutant_id = v.pollutant_id
                      and s.aggregation_process_id = v.aggregation_process_id)
   and not exists (select 1 from statistics);

insert into schema_version (version, description)
values ('4.502.32', 'statistics seeded with the 77 default pollutant/aggregation pairs '
                    'where the table was empty -- the Statistics page listed no pollutants')
on conflict (version) do nothing;

commit;
