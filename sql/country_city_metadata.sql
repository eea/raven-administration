alter table settings
    add country text default 'To-be-defined' not null;

alter table settings
    add country_code text default 'To-be-defined' not null;

alter table stations
    add city_code varchar(255);