-- The European Air Quality Index bands (calculation_type 'EEA'), in the v4 shape.
--
-- sql/schema.sql creates the table: the numeric pollutant id (eea_pollutants.id) and the
-- eea_times id ('hour'). This seed used to be the v3 script: it dropped the table and
-- recreated it with a text `pollutant_uri` column referencing eea_pollutants, whose id is
-- an integer in v4, so on a v4 database it failed with
--   ERROR: foreign key constraint "aqi_eea_pollutants_uri_fk" cannot be implemented
-- after the drop had already removed the table schema.sql created.
--
-- Idempotent and non-destructive: the table is created only if missing, LOCAL bands are
-- left alone, and a band already present is not overwritten.

create table if not exists aqi
(
    calculation_type text         not null
        constraint aqi_calculation_type_check
            check (calculation_type = ANY (ARRAY ['EEA'::text, 'LOCAL'::text])),
    level            integer      not null,
    description      text         not null,
    color            text         not null,
    range            numrange     not null,
    pollutant_id     integer      not null
        references eea_pollutants
            on update cascade on delete cascade,
    timestep         varchar(100) not null
        references eea_times
            on update cascade on delete cascade,
    primary key (pollutant_id, level, timestep, calculation_type)
);

create index if not exists aqi_range_idx
    on aqi using gist (range);

create index if not exists aqi_pollutant_timestep_idx
    on aqi (pollutant_id, timestep, calculation_type);

insert into aqi (calculation_type, level, description, color, range, pollutant_id, timestep)
values
    ('EEA', 1, 'Good', '#50F0E6', '[0,5]', 6001, 'hour'),
    ('EEA', 2, 'Fair', '#50CCAA', '[6,15]', 6001, 'hour'),
    ('EEA', 3, 'Moderate', '#F0E641', '[16,50]', 6001, 'hour'),
    ('EEA', 4, 'Poor', '#FF5050', '[51,90]', 6001, 'hour'),
    ('EEA', 5, 'Very poor', '#960032', '[91,140]', 6001, 'hour'),
    ('EEA', 6, 'Extremely poor', '#7D2181', '[141,999999]', 6001, 'hour'),
    ('EEA', 1, 'Good', '#50F0E6', '[0,15]', 5, 'hour'),
    ('EEA', 2, 'Fair', '#50CCAA', '[16,45]', 5, 'hour'),
    ('EEA', 3, 'Moderate', '#F0E641', '[46,120]', 5, 'hour'),
    ('EEA', 4, 'Poor', '#FF5050', '[121,195]', 5, 'hour'),
    ('EEA', 5, 'Very poor', '#960032', '[196,270]', 5, 'hour'),
    ('EEA', 6, 'Extremely poor', '#7D2181', '[271,999999]', 5, 'hour'),
    ('EEA', 1, 'Good', '#50F0E6', '[0,60]', 7, 'hour'),
    ('EEA', 2, 'Fair', '#50CCAA', '[61,100]', 7, 'hour'),
    ('EEA', 3, 'Moderate', '#F0E641', '[101,120]', 7, 'hour'),
    ('EEA', 4, 'Poor', '#FF5050', '[121,160]', 7, 'hour'),
    ('EEA', 5, 'Very poor', '#960032', '[161,180]', 7, 'hour'),
    ('EEA', 6, 'Extremely poor', '#7D2181', '[181,999999]', 7, 'hour'),
    ('EEA', 1, 'Good', '#50F0E6', '[0,10]', 8, 'hour'),
    ('EEA', 2, 'Fair', '#50CCAA', '[11,25]', 8, 'hour'),
    ('EEA', 3, 'Moderate', '#F0E641', '[26,60]', 8, 'hour'),
    ('EEA', 4, 'Poor', '#FF5050', '[61,100]', 8, 'hour'),
    ('EEA', 5, 'Very poor', '#960032', '[101,150]', 8, 'hour'),
    ('EEA', 6, 'Extremely poor', '#7D2181', '[151,999999]', 8, 'hour'),
    ('EEA', 1, 'Good', '#50F0E6', '[0,20]', 1, 'hour'),
    ('EEA', 2, 'Fair', '#50CCAA', '[21,40]', 1, 'hour'),
    ('EEA', 3, 'Moderate', '#F0E641', '[41,125]', 1, 'hour'),
    ('EEA', 4, 'Poor', '#FF5050', '[126,190]', 1, 'hour'),
    ('EEA', 5, 'Very poor', '#960032', '[191,275]', 1, 'hour'),
    ('EEA', 6, 'Extremely poor', '#7D2181', '[276,999999]', 1, 'hour')
on conflict do nothing;
