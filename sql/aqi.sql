drop table if exists aqi;

create table if not exists aqi
(
    calculation_type text       not null constraint check_is_eea_or_local check (calculation_type = ANY (ARRAY ['EEA'::text, 'LOCAL'::text])),
    level            integer    not null,
    description      text       not null,
    color            text       not null,
    range            numrange   not null,
    pollutant_uri    text       not null constraint aqi_eea_pollutants_uri_fk references eea_pollutants on update cascade on delete cascade,
    timestep         text       not null constraint aqi_eea_times_id_fk references eea_times on update cascade on delete cascade,
    constraint aqi_pk primary key (pollutant_uri, level, timestep, calculation_type)
);

create index if not exists aqi_range_idx on aqi using gist (range);
create index if not exists aqi_pollutant_uri_timestep_calculation_type_idx on aqi (pollutant_uri, timestep, calculation_type);


INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 1, 'Good', '#50F0E6', '[0,5]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 2, 'Fair', '#50CCAA', '[6,15]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 3, 'Moderate', '#F0E641', '[16,50]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 4, 'Poor', '#FF5050', '[51,90]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 5, 'Very poor', '#960032', '[91,140]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 6, 'Extremely poor', '#7D2181', '[141,999999]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 1, 'Good', '#50F0E6', '[0,15]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 2, 'Fair', '#50CCAA', '[16,45]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 3, 'Moderate', '#F0E641', '[46,120]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 4, 'Poor', '#FF5050', '[121,195]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 5, 'Very poor', '#960032', '[196,270]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 6, 'Extremely poor', '#7D2181', '[271,999999]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 1, 'Good', '#50F0E6', '[0,60]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 2, 'Fair', '#50CCAA', '[61,100]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 3, 'Moderate', '#F0E641', '[101,120]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 4, 'Poor', '#FF5050', '[121,160]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 5, 'Very poor', '#960032', '[161,180]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 6, 'Extremely poor', '#7D2181', '[181,999999]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 1, 'Good', '#50F0E6', '[0,10]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 2, 'Fair', '#50CCAA', '[11,25]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 3, 'Moderate', '#F0E641', '[26,60]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 4, 'Poor', '#FF5050', '[61,100]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 5, 'Very poor', '#960032', '[101,150]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 6, 'Extremely poor', '#7D2181', '[151,999999]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 1, 'Good', '#50F0E6', '[0,20]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 2, 'Fair', '#50CCAA', '[21,40]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 3, 'Moderate', '#F0E641', '[41,125]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 4, 'Poor', '#FF5050', '[126,190]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 5, 'Very poor', '#960032', '[191,275]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO aqi (calculation_type, level, description, color, range, pollutant_uri, timestep) VALUES ('EEA', 6, 'Extremely poor', '#7D2181', '[276,999999]', 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
