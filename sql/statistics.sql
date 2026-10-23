-- Migration: Statistics and Aggregation Process Configuration
-- Description: Creates tables for managing statistics/aggregations configuration
-- Dependencies: eea_pollutants table must exist

------------------------------------------------------------------------------------
-- EEA Aggregation Process Lookup Table
------------------------------------------------------------------------------------

create table if not exists eea_aggregationprocess
(
    id       text not null
        constraint eea_aggregationprocess_pk
            primary key,
    label    text not null,
    notation text not null
        constraint eea_aggregationprocess_pk2
            unique
);

comment on table eea_aggregationprocess is 'EEA aggregation process types (e.g., P1D, P1Y, 8hMax, etc.)';

------------------------------------------------------------------------------------
-- Statistics Configuration Table
------------------------------------------------------------------------------------

create table if not exists statistics
(
    pollutant_id           integer               not null
        references eea_pollutants
            on update cascade on delete cascade,
    aggregation_process_id varchar(100)          not null
        references eea_aggregationprocess
            on update cascade on delete cascade,
    directive_2008_50      boolean default false not null,
    directive_2024_2881    boolean default false not null
);

comment on table statistics is 'Configuration for which statistics/aggregations apply to which pollutants under which directives';

-- The v4 id convention: `id` is the short EEA code and `uri` the full URI (see the
-- note at the end of sql/data.sql). This seed used to put the URI in `id`, which gave
-- every database a vocabulary keyed differently from every other eea_* table and left
-- the Models dropdown sorting aggregation processes by URL. Migration
-- 016_vocabulary_id_normalisation.sql repairs databases that took the old spelling.
--
-- id and uri are derived from the notation rather than repeated, so they cannot drift
-- apart: for all 93 concepts the notation IS the URI's last segment.
insert into eea_aggregationprocess (id, label, notation, uri)
select v.notation as id, v.label, v.notation,
       'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/' || v.notation as uri
  from (values
          ('AOT40c',               'AOT40 vegetation protection'),
          ('AOT40c-P5Y',           'AOT40 vegetation protection averaged over 5 years'),
          ('AOT40c-nv',            'Number of valid hourly value for AOTc calculations'),
          ('AOT40cmeasured',       'AOT40c UNCORRECTED for data capture'),
          ('AOT40f-nv',            'Number of valid hourly value for AOTf calculations'),
          ('AOT40fmeasured',       'AOT40f UNCORRECTED for data capture'),
          ('AOT40h',               'Preliminary hourly calculation for AOT40 for AOT40c & AOT40f'),
          ('P1D',                  'Daily average (24-hour mean)'),
          ('P1D-dc',               'Data capture of hourly values in 1 day'),
          ('P1D-hr-max',           '1 day hour max'),
          ('P1D-hrsAbove180',      '1 day exceed 180'),
          ('P1D-hrsAbove240',      '1 day exceed 240'),
          ('P1D-mf',               '1 day missing data fractions'),
          ('P1M',                  'Monthly average'),
          ('P1M-dmaxAbove100',     '1 month daymax exceed 100'),
          ('P1M-dmaxAbove120',     '1 month daymax exceed 120'),
          ('P1M-hrsAbove180',      '1 year exceed 180'),
          ('P1M-hrsAbove200',      '1 year exceed 200'),
          ('P1M-hrsAbove240',      '1 year exceed 240'),
          ('P1M-hrsAbove350',      '1 year exceed 350'),
          ('P1M-hrsAbove400',      '1 year exceed 400'),
          ('P1Y',                  'Annual mean / 1 calendar year'),
          ('P1Y-3daysAbove50',     '3 consecutive days in exceedance of 50'),
          ('P1Y-3daysAbove90',     '3 consecutive days in exceedance of 90'),
          ('P1Y-3hAbove200',       '3 consecutive hours in exceedance of 200'),
          ('P1Y-3hAbove350',       '3 consecutive hours in exceedance of 350'),
          ('P1Y-3hAbove400',       '3 consecutive hours in exceedance of 400'),
          ('P1Y-3hAbove500',       '3 consecutive hours in exceedance of 500'),
          ('P1Y-8hdmxAbove10',     '1 year daymax exceed 10'),
          ('P1Y-P1D-per90.4',      '1 year 90.4 percentile - COMPLIANCE'),
          ('P1Y-P1D-per90.41',     '1 year 90.41 percentile'),
          ('P1Y-dx-max',           '1 year P8H-dmax'),
          ('P1Y-P1D-per95.07',     '1 year 95.07 percentile of daily means (P1D) or .../aq/primaryObservation/day'),
          ('P1Y-P1D-per99',        '1 year 99 percentile of daily means (P1D) or .../aq/primaryObservation/day'),
          ('P1Y-P1D-per99.18',     '1 year 99.18 percentile of daily value/mean (see P1Y-day-max-per99.18)'),
          ('P1Y-WA-avg',           'yearly mean weighted average'),
          ('P1Y-WA-dc',            '1 year weighted average data capture'),
          ('P1Y-WA-tc',            '1 year weighted average time coverage'),
          ('P1Y-day-max',          '1 year day max'),
          ('P1Y-day-max-per99.18', '1 year 99.18 percentile of daily MEAN (P1Y-P1D-per99.18)'),
          ('P1Y-day-max36',        '1 year day max 36'),
          ('P1Y-day-max4',         '1 year day max 4'),
          ('P1Y-day-min',          '1 year day min'),
          ('P1Y-day-per50',        '1 year 50 %ile of daily values in a year'),
          ('P1Y-daysAbove100',     '1 year exceed 100'),
          ('P1Y-daysAbove125',     '1 year day exceed 125'),
          ('P1Y-daysAbove25',      '1 year day exceed 25'),
          ('P1Y-daysAbove4',       '1 year day exceed 4'),
          ('P1Y-daysAbove45',      '1 year day exceed 45'),
          ('P1Y-daysAbove50',      '1 year day exceed 50'),
          ('P1Y-daysAbove90',      '1 year day exceed 90'),
          ('P1Y-dc',               'Data capture of reported units in 1 year'),
          ('P1Y-dmax-per93.15',    '1 year 93.15 percentile daily 8h maximum'),
          ('P1Y-dmax-per95.07',    '1 year 95.07 percentile daily 8h maximum'),
          ('P1Y-dmax-per99',       '1 year 99 percentile daily 8h maximum'),
          ('P1Y-dmaxAbove100',     '1 year daymax exceed 100'),
          ('P1Y-dmaxAbove120',     '1 year daymax exceed 120'),
          ('P1Y-dx-avg',           '1 year daymax average'),
          ('P1Y-dx-dc',            'Data capture of daily maximum values in 1 year'),
          ('P1Y-dx-max26',         '1 year daymax max 26'),
          ('P1Y-dx-min',           '1 year day-max min'),
          ('P1Y-dx-nv',            '1 year day-max Nvalid'),
          ('P1Y-hr-max',           '1 year hour max'),
          ('P1Y-hr-max-per99.73',  '1 year 99.73 %ile of hourly values in a given year'),
          ('P1Y-hr-max-per99.79',  '1 year 99.79 %ile of hourly values in a given year'),
          ('P1Y-hr-max-per99.97',  '1 year 99.97 %ile of hourly values in a given year'),
          ('P1Y-hr-max19',         '1 year hour max19'),
          ('P1Y-hr-max25',         '1 year hour max 25'),
          ('P1Y-hr-min',           '1 year hour min'),
          ('P1Y-hr-per50',         '1 year 50 percentile'),
          ('P1Y-hrsAbove150',      '1 year hour exceed 150'),
          ('P1Y-hrsAbove180',      '1 year hour exceed 180'),
          ('P1Y-hrsAbove200',      '1 year hour exceed 200'),
          ('P1Y-hrsAbove240',      '1 year hour exceed 240'),
          ('P1Y-hrsAbove275',      '1 year hour exceed 275'),
          ('P1Y-hrsAbove350',      '1 year hour exceed 350'),
          ('P1Y-hrsAbove400',      '1 year hour exceed 400'),
          ('P1Y-maxP6M-P8H-dmax',  'Yearly highest six monthly average of daily maximum 8-hour mean concentration'),
          ('P1Y-nt',               '1 year Ntotal'),
          ('P1Y-nv',               '1 year Nvalid'),
          ('P1Y-peakP6M-P8H-dmax', 'P1Y-peakP6M-P8H-dmax'),
          ('P3Y',                  '3 subsequent calendar years mean'),
          ('P3Y-dmaxAbove120',     'Daymax exceed 120 averaged over 3 consecutive years'),
          ('P6M',                  '6 monthly average'),
          ('P6M-P8H-dmax',         'Average of the daily maximum eight-hour mean (P8H-dmax) in 6 consecutive months'),
          ('P8H-dmax',             'Maximum daily eight-hour mean'),
          ('P8H-run',              '8-hour running mean'),
          ('SOMO10',               'Sum of Ozone Means Over 10 ppb'),
          ('SOMO35',               'Sum of Ozone Means Over 35 ppb'),
          ('highsummer',           'High summer mean'),
          ('summer-avg',           'Summer mean'),
          ('winter-avg',           'Winter mean'),
          ('AOT40f',               'AOT40 forest protection')
       ) as v(notation, label)
on conflict (id) do nothing;


-- Which statistics the Statistics page offers per pollutant, and under which directive.
--
-- The v4 shape, as sql/schema.sql declares it: the numeric pollutant id, and the short
-- aggregation process id (the convention migration 016 established). This seed used to
-- name a v3 `pollutant_uri` column and pass URIs, so every row failed on a v4 database
-- and the Statistics page listed no pollutants -- dev-raven4 had 0 rows.
--
-- Idempotent: a pair already present is left alone, so running this again, or on a
-- database that curated its own configuration, adds only what is missing. Migration
-- 032_statistics_seed.sql inserts the same rows into a database whose table is empty,
-- and the migrate wizard runs this file when the v3 source had none.
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
                      and s.aggregation_process_id = v.aggregation_process_id);
