create sequence converted_series_id_seq;

create sequence group_id_seq;

create sequence users_id_seq;

create sequence zones_id_seq;

create type raven_label_value as
(
    label text,
    value text
);

create type raven_station_timeseries as
(
    label      text,
    value      text,
    timeseries raven_label_value[]
);

create table if not exists eea_adjustmenttypes
(
    id    varchar(250) not null,
    label varchar(100) not null,
    uri   varchar(255) not null,
    constraint eea_adjustmenttype_pkey
        primary key (id)
);

create table if not exists eea_areaclassifications
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eee_areaclassification_pkey
        primary key (id)
);

create table if not exists eea_assessmentthresholdexceedances
(
    id    varchar(250) not null,
    label varchar(100) not null,
    uri   varchar(255) not null,
    constraint eea_assessmentthresholdexceedance_pkey
        primary key (id)
);

create table if not exists eea_assessmenttypes
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_assessmenttype_pkey
        primary key (id)
);

create table if not exists eea_concentrations
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_concentrations_pkey
        primary key (id)
);

create table if not exists eea_equivalencedemonstrated
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_equivalencedemonstrated_pkey
        primary key (id)
);

create table if not exists eea_exceedancedescription
(
    id   integer not null,
    name varchar(10),
    constraint eea_exceedancedescription_pkey
        primary key (id)
);

create table if not exists eea_exceedancereason
(
    id    varchar(250) not null,
    label varchar(100) not null,
    uri   varchar(255) not null,
    constraint eea_exceedancereason_pkey
        primary key (id)
);

create table if not exists eea_exceedancetype
(
    id   numeric     not null,
    name varchar(50) not null,
    constraint exceedancetype_pkey
        primary key (id)
);

create table if not exists eea_measurementequipments
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_measurementequipments_pkey
        primary key (id)
);

create table if not exists eea_measurementmethods
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_measurementmethods_pkey
        primary key (id)
);

create table if not exists eea_measurementregimevalues
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_measurementregimevalues_pkey
        primary key (id)
);

create table if not exists eea_measurementtypes
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_measurementtypes_pkey
        primary key (id)
);

create table if not exists eea_mediavalues
(
    id       varchar(500) not null,
    label    varchar(500) not null,
    notation varchar(500) not null,
    constraint eea_mediavalues_pkey
        primary key (id)
);

create table if not exists eea_objecttypes
(
    id    varchar(250) not null,
    label varchar(100) not null,
    uri   varchar(255) not null,
    constraint eea_objecttype_pkey
        primary key (id)
);

create table if not exists eea_organisationallevels
(
    id       varchar(500) not null,
    label    varchar(500) not null,
    notation varchar(500) not null,
    constraint eea_organisationallevels_pkey
        primary key (id)
);

create table if not exists eea_pollutants
(
    id       integer      not null,
    uri      varchar(500) not null,
    label    varchar(500) not null,
    notation varchar(500) not null,
    constraint eea_pollutants_pkey1
        primary key (uri),
    constraint un_po_id
        unique (id)
);

create table if not exists autovalidated_series
(
    id        serial               not null,
    pollutant varchar(255)         not null,
    max       double precision     not null,
    min       double precision     not null,
    rep       integer              not null,
    enabled   boolean default true not null,
    constraint autovalidate_series_pk
        primary key (id),
    constraint autovalidated_series_eea_pollutants_uri_fk
        foreign key (pollutant) references eea_pollutants
            on update cascade on delete cascade
);

create unique index if not exists autovalidate_series_pollutant_uindex
    on autovalidated_series (pollutant);

create table if not exists eea_processtypevalues
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_processtypevalues_pkey
        primary key (id)
);

create table if not exists eea_protectiontargets
(
    id    varchar(250) not null,
    label varchar(100) not null,
    uri   varchar(255) not null,
    constraint eea_protectiontarget_pkey
        primary key (id)
);

create table if not exists eea_reportingmetrics
(
    id    varchar(250) not null,
    label varchar(100) not null,
    uri   varchar(255) not null,
    constraint eea_reportingmetric_pkey
        primary key (id)
);

create table if not exists eea_resultnaturevalues
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_resultnaturevalues_pkey
        primary key (id)
);

create table if not exists eea_stationclassifications
(
    id       varchar(250) not null,
    label    varchar(100) not null,
    notation varchar(100) not null,
    constraint eea_stationclassification_pkey
        primary key (id)
);

create table if not exists eea_times
(
    id       varchar(250)      not null,
    label    varchar(100)      not null,
    notation varchar(100)      not null,
    timestep integer default 1 not null,
    constraint eea_times_pkey
        primary key (id)
);

create table if not exists eea_timezones
(
    id       varchar(500) not null,
    label    varchar(500) not null,
    notation varchar(500) not null,
    constraint eea_timezones_pkey
        primary key (id)
);

create table if not exists eea_zonetypes
(
    id    varchar(250) not null,
    label varchar(100) not null,
    uri   varchar(255) not null,
    constraint eea_zonetypes_pkey
        primary key (id)
);

comment on column eea_zonetypes.uri is 'AQD zonetype namespace URI';

create table if not exists "group"
(
    id             integer default nextval('group_id_seq'::regclass) not null,
    name           varchar(255)                                      not null,
    management     boolean,
    data           boolean,
    exporting      boolean,
    processing     boolean,
    qualitycontrol boolean,
    users          boolean,
    allnetworks    boolean,
    locked         boolean default false                             not null,
    constraint group_pkey
        primary key (id),
    constraint group_name_key
        unique (name)
);

create table if not exists responsible_authorities
(
    id                      varchar(100)          not null,
    name                    varchar(255)          not null,
    organisation            varchar(255)          not null,
    locator                 varchar(255)          not null,
    postcode                varchar(255)          not null,
    email                   varchar(255)          not null,
    address                 varchar(255)          not null,
    phone                   varchar(255)          not null,
    website                 varchar(255)          not null,
    is_responsible_reporter boolean default false not null,
    constraint responsible_authorities_pkey
        primary key (id)
);

create table if not exists networks
(
    id                       varchar(100)                                                                                  not null,
    name                     varchar(255)                                                                                  not null,
    media_monitored          varchar(255) default 'http://inspire.ec.europa.eu/codelist/MediaValue/air'::character varying not null,
    responsible_authority_id varchar(100)                                                                                  not null,
    organisational           varchar(255)                                                                                  not null,
    begin_position           varchar(25)                                                                                   not null,
    end_position             varchar(25),
    aggregation_timezone     varchar(250)                                                                                  not null,
    constraint networks_pkey
        primary key (id),
    constraint networks_aggregation_timezone_fkey
        foreign key (aggregation_timezone) references eea_timezones
            on update cascade on delete cascade,
    constraint networks_media_monitored_fkey
        foreign key (media_monitored) references eea_mediavalues
            on update cascade on delete cascade,
    constraint networks_organisational_fkey
        foreign key (organisational) references eea_organisationallevels
            on update cascade on delete cascade,
    constraint networks_responsible_authority_id_fkey
        foreign key (responsible_authority_id) references responsible_authorities
            on update cascade on delete cascade
);

create table if not exists groupnetwork
(
    groupid   integer      not null,
    networkid varchar(100) not null,
    constraint groupnetwork_pkey
        primary key (groupid, networkid),
    constraint groupnetwork_group_id_fk
        foreign key (groupid) references "group"
            on update cascade on delete cascade,
    constraint groupnetwork_networks_id_fk
        foreign key (networkid) references networks
            on update cascade on delete cascade
);

create table if not exists processes
(
    id                          varchar(100) not null,
    measurement_type            varchar(255) not null,
    measurement_method          varchar(255),
    other_measurement_method    varchar(255),
    sampling_method             varchar(255),
    other_sampling_method       varchar(255),
    analytical_tech             varchar(255),
    other_analytical_tech       varchar(255),
    sampling_equipment          varchar(255),
    measurement_equipment       varchar(255),
    equiv_demonstration         varchar(255),
    equiv_demonstration_report  varchar(255),
    detection_limit             numeric(32, 5),
    detection_limit_uom         varchar(255),
    uncertainty_estimate        numeric(32, 5),
    documentation               varchar(255),
    qa_report                   varchar(255),
    duration_number             integer      not null,
    duration_unit               varchar(255) not null,
    cadence_number              integer      not null,
    cadence_unit                varchar(255) not null,
    responsible_authority_id    varchar(100) not null,
    other_measurement_equipment varchar(255),
    other_sampling_equipment    varchar(255),
    constraint processes_pkey
        primary key (id),
    constraint processes_cadence_unit_fkey
        foreign key (cadence_unit) references eea_times
            on update cascade on delete cascade,
    constraint processes_duration_unit_fkey
        foreign key (duration_unit) references eea_times
            on update cascade on delete cascade,
    constraint processes_responsible_authority_id_fkey
        foreign key (responsible_authority_id) references responsible_authorities
            on update cascade on delete cascade,
    constraint processes_eea_measurementtypes_id_fk
        foreign key (measurement_type) references eea_measurementtypes
            on update cascade on delete cascade,
    constraint processes_eea_measurementmethods_id_fk
        foreign key (measurement_method) references eea_measurementmethods
            on update cascade on delete cascade,
    constraint processes_eea_equivalencedemonstrated_id_fk
        foreign key (equiv_demonstration) references eea_equivalencedemonstrated
            on update cascade on delete cascade,
    constraint processes_eea_concentrations_id_fk
        foreign key (detection_limit_uom) references eea_concentrations
            on update cascade on delete cascade,
    constraint processes_eea_measurementequipments_id_fk
        foreign key (measurement_equipment) references eea_measurementequipments
            on update cascade on delete cascade
);

create table if not exists samples
(
    id                varchar(100)   not null,
    inlet_height      numeric(32, 3) not null,
    building_distance numeric(32, 3),
    kerb_distance     numeric(32, 3),
    constraint samples_pkey
        primary key (id)
);

create table if not exists settings
(
    id                 serial       not null,
    namespace          varchar(255) not null,
    uom_m              varchar(255) not null,
    observation_prefix varchar(10)  not null,
    language_code      varchar(3)   not null,
    constraint settings_pkey
        primary key (id),
    constraint settings_namespace_key
        unique (namespace)
);

create table if not exists stations
(
    id                    varchar(100)                                                                                                                   not null,
    name                  varchar(255)                                                                                                                   not null,
    begin_position        varchar(25)                                                                                                                    not null,
    end_position          varchar(25),
    network_id            varchar(100)                                                                                                                   not null,
    city                  varchar(255),
    national_station_code varchar(20),
    media_monitored       varchar(255) default 'http://inspire.ec.europa.eu/codelist/MediaValue/air'::character varying                                  not null,
    mobile                boolean      default false                                                                                                     not null,
    measurement_regime    varchar(255) default 'http://inspire.ec.europa.eu/codelist/measurementregimevalue/continuousdatacollection'::character varying not null,
    area_classification   varchar(255)                                                                                                                   not null,
    distance_junction     integer,
    traffic_volume        integer,
    heavy_duty_fraction   numeric(255, 5),
    street_width          integer,
    height_facades        integer,
    geom                  geometry                                                                                                                       not null,
    municipality          varchar(255),
    eoi_code              varchar(20)                                                                                                                    not null,
    constraint stations_pkey
        primary key (id),
    constraint stations_network_id_fkey
        foreign key (network_id) references networks
            on update cascade on delete cascade,
    constraint stations_eea_measurementregimevalues_id_fk
        foreign key (measurement_regime) references eea_measurementregimevalues
            on update cascade on delete cascade,
    constraint stations_eea_mediavalues_id_fk
        foreign key (media_monitored) references eea_mediavalues
            on update cascade on delete cascade,
    constraint stations_eea_areaclassifications_id_fk
        foreign key (area_classification) references eea_areaclassifications
            on update cascade on delete cascade
);

create table if not exists sampling_points
(
    id                     varchar(100)               not null,
    media_monitored        varchar(255) default 'http://inspire.ec.europa.eu/codelist/MediaValue/air'::character varying not null,
    station_id             varchar(100)               not null,
    measurement_regime     varchar(255) default 'http://inspire.ec.europa.eu/codelist/measurementregimevalue/continuousdatacollection'::character varying,
    mobile                 boolean                    not null,
    assessment_type        varchar(255)               not null,
    station_classification varchar(255)               not null,
    used_aqd               boolean      default true,
    main_emission_sources  varchar(255),
    traffic_emissions      varchar(255),
    heating_emissions      varchar(255),
    industrial_emissions   varchar(255),
    distance_source        varchar(255),
    change_aei_stations    varchar(255),
    begin_position         varchar(25)                not null,
    end_position           varchar(25),
    logger_id              varchar(255),
    pollutant              varchar(255)               not null,
    concentration          varchar(255)               not null,
    timestep               varchar(255)               not null,
    from_time              timestamp,
    to_time                timestamp,
    private                boolean      default false not null,
    constraint sampling_points_pkey
        primary key (id),
    constraint sampling_points_eea_concentrations_id_fk
        foreign key (concentration) references eea_concentrations
            on update cascade on delete cascade,
    constraint sampling_points_eea_pollutants_uri_fk
        foreign key (pollutant) references eea_pollutants
            on update cascade on delete cascade,
    constraint sampling_points_eea_times_id_fk
        foreign key (timestep) references eea_times
            on update cascade on delete cascade,
    constraint sampling_points_station_id_fkey
        foreign key (station_id) references stations
            on update cascade on delete cascade,
    constraint sampling_points_eea_assessmenttypes_id_fk
        foreign key (assessment_type) references eea_assessmenttypes
            on update cascade on delete cascade,
    constraint sampling_points_eea_stationclassifications_id_fk
        foreign key (station_classification) references eea_stationclassifications
            on update cascade on delete cascade,
    constraint sampling_points_eea_mediavalues_id_fk
        foreign key (media_monitored) references eea_mediavalues
            on update cascade on delete cascade,
    constraint sampling_points_eea_measurementregimevalues_id_fk
        foreign key (measurement_regime) references eea_measurementregimevalues
            on update cascade on delete cascade
);

create table if not exists calculated_series
(
    id        bigserial    not null,
    "primary" varchar(100) not null,
    secondary varchar(100) not null,
    result    varchar(100) not null,
    operator  char         not null,
    constraint calculated_series_pkey
        primary key (id),
    constraint un_cs_p_s_r
        unique ("primary", secondary, result),
    constraint fk_cs_primary
        foreign key ("primary") references sampling_points
            on update cascade on delete cascade,
    constraint fk_cs_result
        foreign key (result) references sampling_points
            on update cascade on delete cascade,
    constraint fk_cs_secondary
        foreign key (secondary) references sampling_points
            on update cascade on delete cascade
);

create table if not exists converted_series
(
    id                bigint default nextval('converted_series_id_seq'::regclass) not null,
    sampling_point_id varchar(100)                                                not null,
    source            varchar(255)                                                not null,
    target            varchar(255)                                                not null,
    factor            numeric(255, 3)                                             not null,
    createdby         varchar(255)                                                not null,
    constraint converted_series_pkey
        primary key (id),
    constraint un_con_oc_id
        unique (sampling_point_id),
    constraint fc_converted_source
        foreign key (source) references eea_concentrations
            on update cascade on delete cascade,
    constraint fc_converted_target
        foreign key (target) references eea_concentrations
            on update cascade on delete cascade,
    constraint fk_converted_oc_id
        foreign key (sampling_point_id) references sampling_points
            on update cascade on delete cascade
);

create table if not exists observations
(
    id                bigserial       not null,
    sampling_point_id varchar(100)    not null,
    begin_position    varchar(25)     not null,
    end_position      varchar(25)     not null,
    value             numeric(255, 5) not null,
    verification_flag integer         not null,
    validation_flag   integer         not null,
    touched           timestamp(6)    not null,
    from_time         timestamp       not null,
    to_time           timestamp       not null,
    import_value      numeric(255, 5) not null,
    scaled_value      numeric(255, 5),
    constraint observations_pkey
        primary key (id),
    constraint un_obs_spoid_begin_end
        unique (sampling_point_id, begin_position, end_position, from_time, to_time),
    constraint observations_sampling_point_id_fkey
        foreign key (sampling_point_id) references sampling_points
            on update cascade on delete cascade
);

create index if not exists idx_observations_spid_ft
    on observations (sampling_point_id, from_time);

create index if not exists idx_tt
    on observations (sampling_point_id);

create table if not exists observing_capabilities
(
    id                varchar(100)                                                                                             not null,
    begin_position    varchar(25)                                                                                              not null,
    end_position      varchar(25),
    process_type      varchar(255) default 'http://inspire.ec.europa.eu/codelist/processtypevalue/process'::character varying  not null,
    result_nature     varchar(255) default 'http://inspire.ec.europa.eu/codelist/resultnaturevalue/primary'::character varying not null,
    sampling_point_id varchar(100)                                                                                             not null,
    process_id        varchar(100)                                                                                             not null,
    sample_id         varchar(100)                                                                                             not null,
    constraint observing_capabilities_pkey
        primary key (id),
    constraint observing_capabilities_process_id_fkey
        foreign key (process_id) references processes
            on update cascade on delete cascade,
    constraint observing_capabilities_sample_id_fkey
        foreign key (sample_id) references samples
            on update cascade on delete cascade,
    constraint observing_capabilities_sampling_point_id_fkey
        foreign key (sampling_point_id) references sampling_points
            on update cascade on delete cascade,
    constraint observing_capabilities_eea_resultnaturevalues_id_fk
        foreign key (result_nature) references eea_resultnaturevalues
            on update cascade on delete cascade,
    constraint observing_capabilities_eea_processtypevalues_id_fk
        foreign key (process_type) references eea_processtypevalues
            on update cascade on delete cascade
);

create index if not exists sampling_points_station_id_pollutant_timestep_concentration_ind
    on sampling_points (station_id, pollutant, timestep, concentration);

create table if not exists scaling_points
(
    id                bigserial       not null,
    sampling_point_id varchar(100)    not null,
    zero_point        numeric(255, 5) not null,
    span_value        numeric(255, 5) not null,
    gas_concentration numeric(255, 5) not null,
    timestamp         timestamp(6)    not null,
    createdby         varchar(255)    not null,
    constraint scaling_points_pkey
        primary key (id),
    constraint un_scaling_points_oc_id_timestamp
        unique (sampling_point_id, timestamp),
    constraint fk_scaling_oc_id
        foreign key (sampling_point_id) references sampling_points
            on update cascade on delete cascade
);

create table if not exists users
(
    username  varchar(255)                                      not null,
    password  varchar(255)                                      not null,
    created   timestamp,
    createdby varchar(255),
    id        integer default nextval('users_id_seq'::regclass) not null,
    name      varchar(255),
    locked    boolean default false                             not null,
    constraint users_pkey
        primary key (id),
    constraint users_username_key
        unique (username)
);

create table if not exists usergroup
(
    userid  integer not null,
    groupid integer not null,
    constraint usergroup_pkey
        primary key (userid, groupid),
    constraint usergroup_group_id_fk
        foreign key (groupid) references "group"
            on update cascade on delete cascade,
    constraint usergroup_users_id_fk
        foreign key (userid) references users
            on update cascade on delete cascade
);

create table if not exists zones
(
    id                       varchar(100)                                                                                                         not null,
    area                     numeric                                                                                                              not null,
    name                     varchar(254)                                                                                                         not null,
    code                     varchar(100)                                                                                                         not null,
    population               integer                                                                                                              not null,
    population_year          integer                                                                                                              not null,
    type                     varchar(255)                                                                                                         not null,
    geom                     geometry                                                                                                             not null,
    year                     integer                                                                                                              not null,
    zone_type_uri            varchar(255) default 'http://inspire.ec.europa.eu/codelist/ZoneTypeCode/airQualityManagementZone'::character varying not null,
    responsible_authority_id varchar(100)                                                                                                         not null,
    constraint zones_pkey
        primary key (id),
    constraint zones_reporing_auth_id_fkey
        foreign key (responsible_authority_id) references responsible_authorities,
    constraint zones_type_id_fkey
        foreign key (type) references eea_zonetypes
            on update cascade
);

comment on column zones.zone_type_uri is 'AM zonetype namespace URI';

create table if not exists assessmentregimes
(
    id                            varchar(100)         not null,
    name                          varchar(100)         not null,
    zoneid                        varchar(100),
    pollutant                     varchar(255)         not null,
    objecttype                    varchar(255)         not null,
    reportingmetric               varchar(255)         not null,
    protectiontarget              varchar(255)         not null,
    assessmentthresholdexceedance varchar(255)         not null,
    include                       boolean default true not null,
    thresholdclassificationyear   integer              not null,
    thresholdclassificationreport varchar(255)         not null,
    constraint assessmentregimes_pkey
        primary key (id),
    constraint assessmentregimes_assessmentthresholdexceedance_fkey
        foreign key (assessmentthresholdexceedance) references eea_assessmentthresholdexceedances,
    constraint assessmentregimes_objecttype_fkey
        foreign key (objecttype) references eea_objecttypes,
    constraint assessmentregimes_pollutant_fkey
        foreign key (pollutant) references eea_pollutants
            on update cascade on delete cascade,
    constraint assessmentregimes_protectiontarget_fkey
        foreign key (protectiontarget) references eea_protectiontargets,
    constraint assessmentregimes_reportingmetric_fkey
        foreign key (reportingmetric) references eea_reportingmetrics,
    constraint assessmentregimes_zones_id_fk
        foreign key (zoneid) references zones
            on update cascade on delete cascade
);

create table if not exists assessmentdata
(
    assessmentregime_id          varchar(100) not null,
    assessmentlocal_id           varchar(100) not null,
    assessmenttype               varchar(255) not null,
    assessmentmethodedescription varchar(500),
    id                           varchar(100) not null,
    constraint assessmentdata_pkey
        primary key (id),
    constraint assessmentdata_assessmentregime_id_fkey
        foreign key (assessmentregime_id) references assessmentregimes
            on update cascade on delete cascade,
    constraint assessmentdata_sampling_point_id_fkey
        foreign key (assessmentlocal_id) references sampling_points
            on update cascade on delete cascade,
    constraint assessmentdata_eea_assessmenttypes_id_fk
        foreign key (assessmenttype) references eea_assessmenttypes
            on update cascade on delete cascade
);

comment on table assessmentdata is 'Contains samplinpoint(s) and/or model to be used for assessmentregime';

comment on column assessmentdata.assessmentlocal_id is 'This will either be samplingpointid or modelid';

create table if not exists attainments
(
    id                  varchar(100) not null,
    name                varchar(100) not null,
    assessmentregime_id varchar(100) not null,
    comment             varchar(500),
    constraint attainments_pkey
        primary key (id),
    constraint attainments_assessmentregime_fkey
        foreign key (assessmentregime_id) references assessmentregimes
            on update cascade on delete cascade
);

create index if not exists "Zones_the_geom_gist"
    on zones using gist (geom);

alter table zones
    add constraint enforce_dims_geom
        check (st_ndims(geom) = 2);

alter table zones
    add constraint enforce_geotype_geom
        check ((geometrytype(geom) = 'MULTIPOLYGON'::text) OR (geom IS NULL));

alter table zones
    add constraint enforce_srid_geom
        check (st_srid(geom) = 4326);

create table if not exists eea_adjustmentsourcetype
(
    id    varchar(250) not null,
    label varchar(100) not null,
    uri   varchar(100) not null,
    constraint eea_adjustmentsourcetype_pkey
        primary key (id)
);

create table if not exists exceedancedescriptions
(
    id                            varchar(100) not null,
    attainment_id                 varchar(100) not null,
    exceedances                   boolean      not null,
    excedance_type                integer      not null,
    max_value                     numeric      not null,
    adjustment_type               varchar(255),
    surface_area                  numeric,
    exposed_population            integer,
    population_reference_year     integer,
    vegetation_area               numeric,
    area_classification           varchar(255),
    exceedance_reason             varchar(255),
    other_exceedance_reason       varchar(500),
    exceedancedescription_element integer      not null,
    adjustment_source             varchar(255),
    modelassessmentmetadata       varchar(255),
    constraint exceedancedescriptions_pkey
        primary key (id),
    constraint exceedancedescriptions_adjustmenttype_fkey
        foreign key (adjustment_type) references eea_adjustmenttypes,
    constraint exceedancedescriptions_area_classification_fkey
        foreign key (area_classification) references eea_areaclassifications
            on update cascade on delete cascade,
    constraint exceedancedescriptions_attainment_fkey
        foreign key (attainment_id) references attainments
            on update cascade on delete cascade,
    constraint exceedancedescriptions_eea_exceedancedescription_fkey
        foreign key (exceedancedescription_element) references eea_exceedancedescription
            on update cascade on delete cascade,
    constraint exceedancedescriptions_exceedancereason_fkey
        foreign key (exceedance_reason) references eea_exceedancereason,
    constraint exceedancedescriptions_exceedancetype_fkey
        foreign key (excedance_type) references eea_exceedancetype,
    constraint exceedancedescriptions_eea_adjustmentsourcetype_id_fk
        foreign key (adjustment_source) references eea_adjustmentsourcetype
            on update cascade on delete cascade
);

alter table exceedancedescriptions
    add constraint if_exceed_rea_is_other_then_other_exceed_rea_is_not_null
        check ((NOT ((exceedance_reason)::text = 'other'::text)) OR (other_exceedance_reason IS NOT NULL));

alter table exceedancedescriptions
    add constraint if_exceedances_then_area_classification_is_not_null
        check ((NOT exceedances) OR (area_classification IS NOT NULL));

alter table exceedancedescriptions
    add constraint if_exceedances_then_exceedance_reason_is_not_null
        check ((NOT exceedances) OR (exceedance_reason IS NOT NULL));

alter table exceedancedescriptions
    add constraint if_exceedances_then_exposed_population_is_not_null
        check ((NOT exceedances) OR (exposed_population IS NOT NULL));

alter table exceedancedescriptions
    add constraint if_exceedances_then_population_reference_year_is_not_null
        check ((NOT exceedances) OR (population_reference_year IS NOT NULL));

alter table exceedancedescriptions
    add constraint if_exceedances_then_adjustment_type_is_not_null
        check ((NOT exceedances) OR (adjustment_type IS NOT NULL));

alter table exceedancedescriptions
    add constraint if_exceedances_then_surface_area_is_not_null
        check ((NOT exceedances) OR (surface_area IS NOT NULL));

create table if not exists exceedingmethods
(
    exceedancedescription_id varchar(100) not null,
    id                       varchar(100) not null,
    assessmentdata_id        varchar(100) not null,
    constraint exceedingmethods_pkey
        primary key (id),
    constraint exceedingmethods_unique
        unique (exceedancedescription_id, assessmentdata_id),
    constraint exceedingmethods_assessmentdata_id_fkey
        foreign key (assessmentdata_id) references assessmentdata
            on update cascade on delete cascade,
    constraint exceedingmethods_exceedancedescription_id_fkey
        foreign key (exceedancedescription_id) references exceedancedescriptions
            on update cascade on delete cascade
);

create or replace function raven_observations_check_verification() returns trigger
    language plpgsql
as
$$
BEGIN
    IF OLD.verification_flag = 1 AND (OLD.value <> NEW.value OR OLD.validation_flag <> NEW.validation_flag)
    THEN
        RAISE EXCEPTION 'Cannot change data when verification flag is set to 1 (verified)';
    END IF;
    RETURN NEW;
END;
$$;

create trigger raven_observations_check_verification_trigger
    before update
    on observations
    for each row
execute procedure raven_observations_check_verification();

create or replace function raven_observations_set_timestamp() returns trigger
    language plpgsql
as
$$
BEGIN
    NEW.from_time = NEW.begin_position::timestamp;
    NEW.to_time = NEW.end_position::timestamp;
    RETURN NEW;
END;
$$;

create trigger raven_observations_set_timestamp_trigger
    before insert or update
    on observations
    for each row
execute procedure raven_observations_set_timestamp();

create or replace function raven_scale_value(zero double precision, span double precision, gas double precision,
                                             value double precision) returns double precision
    language plpgsql
as
$$
BEGIN
    RETURN ROUND(((gas / (span - zero)) * (value - zero))::numeric, 3);
END;
$$;

create or replace function raven_scale_value(prev_zero double precision, prev_span double precision,
                                             prev_gas double precision, prev_timestamp timestamp without time zone,
                                             next_zero double precision, next_span double precision,
                                             next_gas double precision, next_timestamp timestamp without time zone,
                                             value double precision,
                                             value_timestamp timestamp without time zone) returns double precision
    language plpgsql
as
$$
DECLARE
    prev_epoch       DOUBLE PRECISION;
    next_epoch       DOUBLE PRECISION;
    value_epoch      DOUBLE PRECISION;
    zero_diff        DOUBLE PRECISION;
    epoch_diff       DOUBLE PRECISION;
    epoch_value_diff DOUBLE PRECISION;
    span_diff        DOUBLE PRECISION;
    zero             DOUBLE PRECISION;
    span             DOUBLE PRECISION;
BEGIN
    prev_epoch = extract(epoch from prev_timestamp);
    next_epoch = extract(epoch from next_timestamp);
    value_epoch = extract(epoch from value_timestamp);

    zero_diff = next_zero - prev_zero;
    epoch_diff = next_epoch - prev_epoch;
    epoch_value_diff = value_epoch - prev_epoch;
    span_diff = next_span - prev_span;

    zero = prev_zero + (zero_diff / epoch_diff) * epoch_value_diff;
    span = prev_span + (span_diff / epoch_diff) * epoch_value_diff;

    RETURN raven_scale_value(zero, span, prev_gas, value);
END;
$$;

create or replace function raven_timeserie_update_time() returns trigger
    language plpgsql
as
$$
DECLARE
    fromtime timestamp without time zone;
    totime   timestamp without time zone;

BEGIN
    SELECT sp.from_time, sp.to_time
    INTO fromtime, totime
    FROM sampling_points sp
    WHERE id = NEW.sampling_point_id;

    -- UPDATE FROMTIME IN THE OBSERVING CAPABILITIES TABLE
    IF fromtime IS NULL OR NEW.from_time < fromtime THEN
        UPDATE sampling_points SET from_time = NEW.from_time WHERE id = NEW.sampling_point_id;
    END IF;

    -- UPDATE TOTIME IN THE OBSERVING CAPABILITIES TABLE
    IF totime IS NULL OR NEW.to_time > totime THEN
        UPDATE sampling_points SET to_time = NEW.to_time WHERE id = NEW.sampling_point_id;
    END IF;

    RETURN NEW;
END;
$$;

create trigger raven_timeserie_update_time_trigger
    after insert
    on observations
    for each row
execute procedure raven_timeserie_update_time();
