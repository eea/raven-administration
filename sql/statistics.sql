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
    pollutant_uri          text                  not null
        constraint statistics_eea_pollutants_uri_fk
            references eea_pollutants
            on update cascade on delete cascade,
    aggregation_process_id text                  not null
        constraint statistics_eea_aggregationprocess_id_fk
            references eea_aggregationprocess
            on update cascade on delete cascade,
    directive_2008_50      boolean default false not null,
    directive_2024_2881    boolean default false not null
);

comment on table statistics is 'Configuration for which statistics/aggregations apply to which pollutants under which directives';

INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40c', 'AOT40 vegetation protection', 'AOT40c');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40c-P5Y', 'AOT40 vegetation protection averaged over 5 years', 'AOT40c-P5Y');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40c-nv', 'Number of valid hourly value for AOTc calculations', 'AOT40c-nv');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40cmeasured', 'AOT40c UNCORRECTED for data capture', 'AOT40cmeasured');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40f-nv', 'Number of valid hourly value for AOTf calculations', 'AOT40f-nv');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40fmeasured', 'AOT40f UNCORRECTED for data capture', 'AOT40fmeasured');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40h', 'Preliminary hourly calculation for AOT40 for AOT40c & AOT40f', 'AOT40h');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1D', 'Daily average (24-hour mean)', 'P1D');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1D-dc', 'Data capture of hourly values in 1 day', 'P1D-dc');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1D-hr-max', '1 day hour max', 'P1D-hr-max');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1D-hrsAbove180', '1 day exceed 180', 'P1D-hrsAbove180');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1D-hrsAbove240', '1 day exceed 240', 'P1D-hrsAbove240');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1D-mf', '1 day missing data fractions', 'P1D-mf');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1M', 'Monthly average', 'P1M');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1M-dmaxAbove100', '1 month daymax exceed 100', 'P1M-dmaxAbove100');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1M-dmaxAbove120', '1 month daymax exceed 120', 'P1M-dmaxAbove120');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1M-hrsAbove180', '1 year exceed 180', 'P1M-hrsAbove180');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1M-hrsAbove200', '1 year exceed 200', 'P1M-hrsAbove200');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1M-hrsAbove240', '1 year exceed 240', 'P1M-hrsAbove240');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1M-hrsAbove350', '1 year exceed 350', 'P1M-hrsAbove350');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1M-hrsAbove400', '1 year exceed 400', 'P1M-hrsAbove400');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', 'Annual mean / 1 calendar year', 'P1Y');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3daysAbove50', '3 consecutive days in exceedance of 50', 'P1Y-3daysAbove50');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3daysAbove90', '3 consecutive days in exceedance of 90', 'P1Y-3daysAbove90');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3hAbove200', '3 consecutive hours in exceedance of 200', 'P1Y-3hAbove200');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3hAbove350', '3 consecutive hours in exceedance of 350', 'P1Y-3hAbove350');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3hAbove400', '3 consecutive hours in exceedance of 400', 'P1Y-3hAbove400');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3hAbove500', '3 consecutive hours in exceedance of 500', 'P1Y-3hAbove500');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-8hdmxAbove10', '1 year daymax exceed 10', 'P1Y-8hdmxAbove10');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per90.4', '1 year 90.4 percentile - COMPLIANCE', 'P1Y-P1D-per90.4');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per90.41', '1 year 90.41 percentile', 'P1Y-P1D-per90.41');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dx-max', '1 year P8H-dmax', 'P1Y-dx-max');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per95.07', '1 year 95.07 percentile of daily means (P1D) or .../aq/primaryObservation/day', 'P1Y-P1D-per95.07');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per99', '1 year 99 percentile of daily means (P1D) or .../aq/primaryObservation/day', 'P1Y-P1D-per99');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per99.18', '1 year 99.18 percentile of daily value/mean (see P1Y-day-max-per99.18)', 'P1Y-P1D-per99.18');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-WA-avg', 'yearly mean weighted average', 'P1Y-WA-avg');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-WA-dc', '1 year weighted average data capture', 'P1Y-WA-dc');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-WA-tc', '1 year weighted average time coverage', 'P1Y-WA-tc');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', '1 year day max', 'P1Y-day-max');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max-per99.18', '1 year 99.18 percentile of daily MEAN (P1Y-P1D-per99.18)', 'P1Y-day-max-per99.18');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max36', '1 year day max 36', 'P1Y-day-max36');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max4', '1 year day max 4', 'P1Y-day-max4');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', '1 year day min', 'P1Y-day-min');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-per50', '1 year 50 %ile of daily values in a year', 'P1Y-day-per50');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove100', '1 year exceed 100', 'P1Y-daysAbove100');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove125', '1 year day exceed 125', 'P1Y-daysAbove125');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove25', '1 year day exceed 25', 'P1Y-daysAbove25');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove4', '1 year day exceed 4', 'P1Y-daysAbove4');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove45', '1 year day exceed 45', 'P1Y-daysAbove45');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove50', '1 year day exceed 50', 'P1Y-daysAbove50');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove90', '1 year day exceed 90', 'P1Y-daysAbove90');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dc', 'Data capture of reported units in 1 year', 'P1Y-dc');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dmax-per93.15', '1 year 93.15 percentile daily 8h maximum', 'P1Y-dmax-per93.15');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dmax-per95.07', '1 year 95.07 percentile daily 8h maximum', 'P1Y-dmax-per95.07');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dmax-per99', '1 year 99 percentile daily 8h maximum', 'P1Y-dmax-per99');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dmaxAbove100', '1 year daymax exceed 100', 'P1Y-dmaxAbove100');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dmaxAbove120', '1 year daymax exceed 120', 'P1Y-dmaxAbove120');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dx-avg', '1 year daymax average', 'P1Y-dx-avg');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dx-dc', 'Data capture of daily maximum values in 1 year', 'P1Y-dx-dc');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dx-max26', '1 year daymax max 26', 'P1Y-dx-max26');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dx-min', '1 year day-max min', 'P1Y-dx-min');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dx-nv', '1 year day-max Nvalid', 'P1Y-dx-nv');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', '1 year hour max', 'P1Y-hr-max');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max-per99.73', '1 year 99.73 %ile of hourly values in a given year', 'P1Y-hr-max-per99.73');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max-per99.79', '1 year 99.79 %ile of hourly values in a given year', 'P1Y-hr-max-per99.79');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max-per99.97', '1 year 99.97 %ile of hourly values in a given year', 'P1Y-hr-max-per99.97');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max19', '1 year hour max19', 'P1Y-hr-max19');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max25', '1 year hour max 25', 'P1Y-hr-max25');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', '1 year hour min', 'P1Y-hr-min');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-per50', '1 year 50 percentile', 'P1Y-hr-per50');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove150', '1 year hour exceed 150', 'P1Y-hrsAbove150');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove180', '1 year hour exceed 180', 'P1Y-hrsAbove180');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove200', '1 year hour exceed 200', 'P1Y-hrsAbove200');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove240', '1 year hour exceed 240', 'P1Y-hrsAbove240');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove275', '1 year hour exceed 275', 'P1Y-hrsAbove275');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove350', '1 year hour exceed 350', 'P1Y-hrsAbove350');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove400', '1 year hour exceed 400', 'P1Y-hrsAbove400');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-maxP6M-P8H-dmax', 'Yearly highest six monthly average of daily maximum 8-hour mean concentration', 'P1Y-maxP6M-P8H-dmax');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-nt', '1 year Ntotal', 'P1Y-nt');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-nv', '1 year Nvalid', 'P1Y-nv');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-peakP6M-P8H-dmax', 'P1Y-peakP6M-P8H-dmax', 'P1Y-peakP6M-P8H-dmax');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P3Y', '3 subsequent calendar years mean', 'P3Y');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P3Y-dmaxAbove120', 'Daymax exceed 120 averaged over 3 consecutive years', 'P3Y-dmaxAbove120');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P6M', '6 monthly average', 'P6M');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P6M-P8H-dmax', 'Average of the daily maximum eight-hour mean (P8H-dmax) in 6 consecutive months', 'P6M-P8H-dmax');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P8H-dmax', 'Maximum daily eight-hour mean', 'P8H-dmax');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P8H-run', '8-hour running mean', 'P8H-run');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/SOMO10', 'Sum of Ozone Means Over 10 ppb', 'SOMO10');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/SOMO35', 'Sum of Ozone Means Over 35 ppb', 'SOMO35');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/highsummer', 'High summer mean', 'highsummer');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/summer-avg', 'Summer mean', 'summer-avg');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/winter-avg', 'Winter mean', 'winter-avg');
INSERT INTO eea_aggregationprocess (id, label, notation) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40f', 'AOT40 forest protection', 'AOT40f');


INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/winter-avg', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40c', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/AOT40c-P5Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/38', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/38', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/38', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hr-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/38', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-max', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/38', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-day-min', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per99', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per99', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per99', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per99', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per99', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-P1D-per99', true, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3daysAbove50', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3daysAbove90', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove125', true, false);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove25', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove4', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove45', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove50', true, false);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove50', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove50', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove50', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-daysAbove90', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dmaxAbove100', false, true);
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dmaxAbove120', true, false);

------------------------------------------------------------------------------------
-- NEW AGGREGATIONS (added Dec 2025)
------------------------------------------------------------------------------------

-- 3 Consecutive Hour Exceedances
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3hAbove200', false, true);  -- NO2
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3hAbove350', false, true);  -- SO2
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3hAbove400', true, false);  -- NO2
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-3hAbove500', true, false);  -- SO2

-- 8-Hour Max Exceedances
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-8hdmxAbove10', true, true);  -- CO

-- Hourly Exceedances
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove150', false, true);  -- NO2
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove180', true, true);  -- O3
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove200', true, true);  -- NO2
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove240', true, true);  -- O3
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove275', false, true);  -- SO2
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-hrsAbove350', true, true);  -- SO2

-- Percentile
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P1Y-dmax-per99', false, true);  -- O3

-- Multi-Year
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/P3Y-dmaxAbove120', true, true);  -- O3

-- SOMO Indicators  
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/SOMO10', true, true);  -- O3
INSERT INTO statistics (pollutant_uri, aggregation_process_id, directive_2008_50, directive_2024_2881) VALUES ('http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess/SOMO35', true, true);  -- O3

