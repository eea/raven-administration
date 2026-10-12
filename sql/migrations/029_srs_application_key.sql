-- ===========================================================================
-- 029 — a Spatial representativeness row is one SRS application, as in the guide
--
-- AQR3 v5.02 keys SRS on (CountryCode, SRSId, SRSApplicationId). SRS_02 SRSId
-- names an AREA, and is what ComplianceAssessmentMethod points at (CAM_16).
-- SRS_03 SRSApplicationId names one USE of it -- SRS_04 says which: SPO
-- representativeness (spo_sr) or exceedance extent (exc_sr) -- and "the same
-- SRSId can have several SRSApplication_Id". The grid cells (SRI) and the
-- GeoTIFF (SRE) are keyed on SRSApplicationId alone: they belong to the use.
--
-- Raven had it the other way round: spatial_representativeness.id was the SRSId
-- and the primary key, srs_inline and srs_external hung off it, and
-- srs_application_id was free text nothing kept unique. So an area could have
-- only one application, and two rows with the same application id exported
-- clashing SRI/SRE keys.
--
-- Now:
--   * srs_application_id is the primary key, and srs_inline / srs_external
--     reference it in a column of the same name;
--   * srs_id is an ordinary column, unique together with srs_application;
--   * compliance_assessment_method.srs_id keeps its values -- they were SRSIds and
--     still are -- but loses cam_srs_id_fkey, as an SRSId is no longer unique.
--     The API checks that a CAM's SRSId exists.
--
-- Each existing row keeps its SRSId and becomes its own application. Its key is
-- its old srs_application_id where that is set and unique, and its old id
-- otherwise; the cells and the GeoTIFF row follow by ON UPDATE CASCADE.
--
-- The guide types both ids varchar(50). They are narrowed only when every stored
-- value fits, so this cannot stop a pod from starting; the API refuses longer
-- values either way.
--
-- Idempotent: guarded on spatial_representativeness.srs_id.
-- ===========================================================================

begin;

do $$
declare
    too_long integer;
begin
    if exists (select 1 from information_schema.columns
                where table_schema = 'public'
                  and table_name = 'spatial_representativeness'
                  and column_name = 'srs_id') then
        raise notice '029: spatial_representativeness already keyed on srs_application_id';
        return;
    end if;

    -- First, so rewriting the keys below cannot cascade into CAM_16.
    alter table compliance_assessment_method drop constraint if exists cam_srs_id_fkey;

    alter table spatial_representativeness add column srs_id varchar(255);
    update spatial_representativeness set srs_id = id;

    -- The new key: the stated application id when it is set, unique among the
    -- candidates and not another row's id; the old id otherwise. Through a
    -- temporary value, so swapping two rows' keys cannot collide half-way.
    create temporary table srs_029_keys on commit drop as
    with c as (
        select id, coalesce(nullif(btrim(srs_application_id), ''), id) as candidate
        from spatial_representativeness
    )
    select c.id,
           case when (select count(*) from c c2 where c2.candidate = c.candidate) = 1
                 and not exists (select 1 from spatial_representativeness o
                                  where o.id = c.candidate and o.id <> c.id)
                then c.candidate else c.id end as new_id
    from c;

    update spatial_representativeness sr set id = '~029~' || sr.id
      from srs_029_keys k where k.id = sr.id and k.new_id <> k.id;
    update spatial_representativeness sr set id = k.new_id
      from srs_029_keys k where sr.id = '~029~' || k.id;

    alter table spatial_representativeness drop column srs_application_id;
    alter table spatial_representativeness rename column id to srs_application_id;
    alter table spatial_representativeness alter column srs_id set not null;
    alter table spatial_representativeness
        add constraint spatial_representativeness_srs_id_application_key
        unique (srs_id, srs_application);

    alter table srs_inline rename column spatial_representativeness_id to srs_application_id;
    alter table srs_external rename column spatial_representativeness_id to srs_application_id;
    -- The names schema.sql gives them, so a migrated database matches a fresh one.
    if exists (select 1 from pg_constraint where conname = 'srs_inline_spatial_representativeness_id_fkey') then
        alter table srs_inline rename constraint srs_inline_spatial_representativeness_id_fkey
            to srs_inline_srs_application_id_fkey;
    end if;
    if exists (select 1 from pg_constraint where conname = 'srs_external_spatial_representativeness_id_fkey') then
        alter table srs_external rename constraint srs_external_spatial_representativeness_id_fkey
            to srs_external_srs_application_id_fkey;
    end if;

    select count(*) into too_long from spatial_representativeness
     where length(srs_id) > 50 or length(srs_application_id) > 50;
    if too_long = 0 then
        alter table spatial_representativeness alter column srs_id type varchar(50);
        alter table srs_inline alter column srs_application_id type varchar(50);
        alter table srs_external alter column srs_application_id type varchar(50);
        alter table spatial_representativeness alter column srs_application_id type varchar(50);
    else
        raise notice '029: % row(s) have an SRSId or SRSApplicationId over the 50 characters '
                     'AQR3 allows; the columns stay varchar(255) until they are shortened',
                     too_long;
    end if;
end $$;

comment on table spatial_representativeness is 'AQR3 SRS SpatialRepresentativeness. One row per SRS application: a use (SPO representativeness or exceedance extent) of an area, which CAM_16 links to by its SRSId.';
comment on column spatial_representativeness.srs_id is 'AQR3 SRS_02 SRSId. Names the area; up to one row per SRS_04 application shares it. CAM_16 points here.';
comment on column spatial_representativeness.srs_application_id is 'AQR3 SRS_03 SRSApplicationId. The key: SRI and SRE rows belong to it.';
comment on column spatial_representativeness.srs_application is 'AQR3 SRS_04 SRSApplication -> eea_srapplication (spo_sr | exc_sr)';
comment on column spatial_representativeness.result_encoding_id is 'AQR3 SRS_05 ResultEncoding -> eea_resultencoding: inline (SRI cells) or external (an SRE GeoTIFF)';
comment on column spatial_representativeness.representativeness_assessment_method_id is 'AQR3 SRS_06 RepresentativenessAssessmentMethodId. The model/OBE that defined the area -> models.id, checked by the API.';
comment on table srs_inline is 'AQR3 SRI. Grid cells of an SR application''s area.';
comment on column srs_inline.srs_application_id is 'AQR3 SRI_02 SRSApplicationId';
comment on column srs_external.srs_application_id is 'AQR3 SRE_02 SRSApplicationId';
comment on column compliance_assessment_method.srs_id is 'AQR3 CAM_16 SRSId. Entered, not derived. Matches spatial_representativeness.srs_id, which is not unique (one row per application), so the API checks it rather than a foreign key.';

insert into schema_version (version, description)
values ('4.502.29', 'spatial_representativeness keyed on srs_application_id (SRS_03), with srs_id '
                    '(SRS_02) shared by its applications; SRI/SRE reference the application')
on conflict (version) do nothing;

commit;
