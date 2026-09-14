-- ===========================================================================
-- 023 — one AttainmentId per assessment regime per reporting year, and an
--       SRSId that points at something real
--
-- AQR3 CAM_15 AttainmentId is fully mandatory and composed, per the reporting
-- guide, as
--
--     "ATT" + "_" + Zone Id + "_" + Pollutant Id + "_" + Objective Type + "_"
--           + Protection Target + "_" + Reporting Metric + "_" + Reporting Year
--           + "_" + ordering index      (max length 2 - numeric)
--
-- which is the row's own AssessmentRegimeId with the classification year swapped
-- for the reporting year. The guide is explicit about what the index means:
--
--     "AttainmentId distinguishes each compliance situation. If there is no
--      exceedance in the zone/assessment regime, there will be only one
--      AttainmentId. [...] if single exceedance (caused by the same reason) does
--      not cover the whole zone, there will be 2 AttainmentIds - one for the
--      exceedance situation and one for the non-exceedance situation in the same
--      zone/assessment regime."
--
-- So: ONE attainment per regime per year, shared by every assessment method that
-- assesses it, and more only when somebody decides there is more than one
-- compliance situation.
--
-- WHAT WAS HAPPENING INSTEAD. core/data/plans_programs_export.py passed a running
-- row counter as the ordering index. The 2026-09-09 export therefore carried 543
-- distinct AttainmentIds for 543 rows covering 166 regimes -- up to 21 for a
-- single regime -- and 444 of them had a three-digit index, which the guide
-- forbids and which PATTERNS['AttainmentId'] in core/eea/id_generator.py rejects.
-- Nothing validated the generated value, so it reached Reportnet3 instead of the
-- caller. Worse, being a row ordinal made it unstable: adding one sampling point
-- renumbered every row after it, and since a recalculation restates attainment_id
-- unconditionally, any PollutionLevelAdjustment (ADJ_02) an operator had typed
-- against the old value silently stopped referring to anything.
--
-- THE MAPPING EXISTS ONLY NOW. The old identifier cannot be recomputed from
-- anything once it is gone, so nulling the column and asking for a recalculation
-- would leave pollution_level_adjustment pointing at values that exist nowhere --
-- committing the orphaning defect deliberately. Both tables are therefore remapped
-- here, in one transaction, ADJ first while the mapping still resolves.
--
-- SRSId. CAM_16 was set to the assessment method id, which is not what it means:
-- SRS_02 identifies a spatial representativeness area an operator uploads, and
-- SRS_06 points from that area at the model which assessed it. All 214 distinct
-- SRSIds in the 2026-09-09 export referred to a SpatialRepresentativeness table
-- with no rows in it. The fabricated values are cleared and a foreign key stops
-- them coming back; the column is entered on the CAM screen from now on.
--
-- WHAT THIS MIGRATION DOES NOT DO. It makes the stored rows conformant. It does
-- not change which rows exist -- the sampling points whose pollutant contradicts
-- their regime, and those now out of EEA reporting scope, are removed by the next
-- "Recalculate compliance" on the Dataflow page, not by this file.
--
-- No CHECK ties attainment_id to attainment_index. apply_migrations.py runs at pod
-- boot and raven-v4 runs two replicas, so during a rolling deploy a pod on the old
-- image would still write a row-ordinal identifier against the default index and
-- violate it. Left for a later release, once no such pod can exist.
--
-- Idempotent; a no-op on a fresh install, where schema.sql already declares both
-- changes and seeds this version, and where there are no CAM rows to restate.
-- ===========================================================================

begin;

alter table compliance_assessment_method
    add column if not exists attainment_index integer default 1 not null;

do $$
begin
    if not exists (select 1 from pg_constraint where conname = 'cam_attainment_index_range') then
        alter table compliance_assessment_method
            add constraint cam_attainment_index_range
            check (attainment_index between 1 and 99);
    end if;
end $$;

-- Data steps run once. The guard is this migration's own presence in
-- schema_version, which apply_migrations.py checks before executing this file at
-- all; belt and braces here because the file is also runnable by hand.
do $$
declare
    remapped   integer := 0;
    collapsed  integer := 0;
    orphaned   integer := 0;
    unmappable integer := 0;
    fabricated integer := 0;
begin
    if exists (select 1 from schema_version where version = '4.502.23') then
        raise notice '023: already applied, leaving the stored identifiers as they stand';
        return;
    end if;

    -- The old -> new mapping, while both are still knowable. Many CAM rows share one
    -- new identifier, so it is de-duplicated on the old value.
    create temporary table cam_attainment_map on commit drop as
    select distinct
           c.attainment_id as old_id,
           'ATT_' || regexp_replace(c.assessment_regime_id, '^ARE_(.*)_[^_]+_[^_]+$', '\1')
                  || '_' || c.reporting_year
                  || '_' || c.attainment_index as new_id
      from compliance_assessment_method c
     where c.attainment_id is not null
       and c.assessment_regime_id ~ '^ARE_.+_[^_]+_[^_]+$';

    -- ADJ_02 keys on (attainment_id, adjustment_source_id), and the remap collapses
    -- many old identifiers onto one, so two deductions for the same source under one
    -- regime would now collide. Nothing is destroyed silently: the losers, and any row
    -- whose attainment no longer exists, are archived with the reason.
    create table if not exists pollution_level_adjustment_023_superseded (
        attainment_id                   varchar(100),
        adjustment_source_id            varchar(100),
        adjustment_assessment_method_id varchar(100),
        adjustment_document_id          varchar(255),
        new_attainment_id               varchar(100),
        reason                          text,
        superseded_at                   timestamp default current_timestamp
    );

    with ranked as (
        select a.*, m.new_id,
               row_number() over (partition by m.new_id, a.adjustment_source_id
                                  order by a.attainment_id) as rn
          from pollution_level_adjustment a
          join cam_attainment_map m on m.old_id = a.attainment_id
    )
    insert into pollution_level_adjustment_023_superseded
        (attainment_id, adjustment_source_id, adjustment_assessment_method_id,
         adjustment_document_id, new_attainment_id, reason)
    select attainment_id, adjustment_source_id, adjustment_assessment_method_id,
           adjustment_document_id, new_id,
           'two AttainmentIds collapsed onto one; ADJ_02 keys on '
           '(attainment_id, adjustment_source_id) so only one deduction per source survives'
      from ranked where rn > 1;
    get diagnostics collapsed = row_count;

    delete from pollution_level_adjustment a
     using pollution_level_adjustment_023_superseded s
     where a.attainment_id = s.attainment_id
       and a.adjustment_source_id = s.adjustment_source_id;

    insert into pollution_level_adjustment_023_superseded
        (attainment_id, adjustment_source_id, adjustment_assessment_method_id,
         adjustment_document_id, new_attainment_id, reason)
    select a.attainment_id, a.adjustment_source_id, a.adjustment_assessment_method_id,
           a.adjustment_document_id, null,
           'no ComplianceAssessmentMethod row produces this AttainmentId'
      from pollution_level_adjustment a
     where not exists (select 1 from cam_attainment_map m where m.old_id = a.attainment_id);
    get diagnostics orphaned = row_count;

    delete from pollution_level_adjustment a
     where not exists (select 1 from cam_attainment_map m where m.old_id = a.attainment_id);

    -- ADJ before CAM: while the mapping still resolves.
    update pollution_level_adjustment a
       set attainment_id = m.new_id
      from cam_attainment_map m
     where a.attainment_id = m.old_id
       and a.attainment_id is distinct from m.new_id;
    get diagnostics remapped = row_count;

    update compliance_assessment_method c
       set attainment_id = m.new_id
      from cam_attainment_map m
     where c.attainment_id = m.old_id
       and c.attainment_id is distinct from m.new_id;

    -- A regime that predates ARZ_02 validation cannot yield a conformant AttainmentId,
    -- and a non-conformant one is worse than none: Reportnet3 rejects the submission
    -- either way, but a blank says which rows need the regime fixing.
    update compliance_assessment_method c
       set attainment_id = null
     where c.attainment_id is not null
       and c.assessment_regime_id !~ '^ARE_.+_[^_]+_[^_]+$';
    get diagnostics unmappable = row_count;

    update compliance_assessment_method
       set srs_id = null
     where srs_id is not null
       and srs_id not in (select id from spatial_representativeness);
    get diagnostics fabricated = row_count;

    raise notice '023: % ADJ row(s) remapped, % collapsed, % orphaned (both archived in pollution_level_adjustment_023_superseded)',
        remapped, collapsed, orphaned;
    raise notice '023: % CAM row(s) left without an AttainmentId (assessment regime is not in ARE_ format)', unmappable;
    raise notice '023: % fabricated SRSId(s) cleared - CAM_16 is entered on the Compliance Assessment Method screen', fabricated;
    raise notice '023: identifiers are conformant now; run Recalculate compliance on the Dataflow page to rebuild the ROW SET';
end $$;

-- Outside the guard, and guarded on its own, so a database that got half-way still
-- ends up constrained.
do $$
begin
    if not exists (select 1 from pg_constraint where conname = 'cam_srs_id_fkey') then
        alter table compliance_assessment_method
            add constraint cam_srs_id_fkey foreign key (srs_id)
            references spatial_representativeness on update cascade;
    end if;
end $$;

comment on column compliance_assessment_method.attainment_index is
    'AQR3 CAM_15 ordering index (1-99). The operator''s, never restated by a '
    'recalculation: the guide gives one attainment per zone/assessment regime unless an '
    'exceedance covers only part of the zone, or different exceedances have different '
    'causes. Raise it to split a regime into more than one compliance situation.';

comment on column compliance_assessment_method.attainment_id is
    'AQR3 CAM_15 AttainmentId. Mandatory format: '
    'ATT_<ZoneId>_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>_<ReportingYear>_<idx>. '
    'Derived from this row''s assessment_regime_id, which carries the same five '
    'components: one attainment per regime per reporting year, shared by every '
    'assessment method assessing it, with attainment_index as the trailing <idx>.';

comment on column compliance_assessment_method.srs_id is
    'AQR3 CAM_16 SRSId. Entered, not derived - SRS_02 names a spatial area an operator '
    'uploads and SRS_06 points from that area at the model which assessed it, so nothing '
    'here can infer the link. Was set to the assessment method id until 4.502.23, which '
    'pointed every value at a SpatialRepresentativeness table with no matching row.';

insert into schema_version (version, description)
values ('4.502.23',
        'one AttainmentId per assessment regime per reporting year, with the ordering '
        'index becoming an operator-owned column rather than a row counter. CAM_15 was '
        'built from row position, giving 543 identifiers for 166 regimes, 444 of them '
        'with an index longer than the two digits the guide allows, and changing under '
        'every recalculation - which silently orphaned any PollutionLevelAdjustment '
        'typed against the old value. Both tables are remapped here because the mapping '
        'exists nowhere else. CAM_16 SRSId, which was set to the assessment method id '
        'and referred to nothing, is cleared and given a foreign key')
on conflict (version) do nothing;

commit;
