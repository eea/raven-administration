-- ===========================================================================
-- 020 — drop assessmentregime_zones, the table that shadowed the ARZ export
--
-- Two tables carried nearly the same name and only one of them reported.
--
--   assessment_regimes      'v4.502 AQR3 AssessmentRegimeZone (ARZ)'. What
--                           core/reporting/aqr3/spec.py exports as ARZ, and what
--                           compliance_assessment_method.assessment_regime_id
--                           references. All 19 ARZ attributes resolve from it, from
--                           `zones` beside it, or from settings.country_code_id.
--
--   assessmentregime_zones  'v4.8.0 zone-level assessment regime classification'.
--                           Added before the v5.02 work, read and written by nothing
--                           but its own blueprint, and absent from every export.
--
-- The second could not become the first. It has no AssessmentRegimeId -- ARZ_02, a
-- primary key attribute with a mandatory seven-segment format -- and it collapses
-- ARZ_09 PollutantId, ARZ_10 ProtectionTarget, ARZ_11 ObjectiveType and ARZ_12
-- ReportingMetric into one environmental_objective_id, which is not an AQR3
-- attribute at all. Five columns against nineteen. It also cannot hold ARZ_14
-- PostponementYear, ARZ_15 FixedMeasurementReduction or the ARZ_16/17 population
-- figures, so a zone with a postponement was unrepresentable.
--
-- Its two columns that did carry AQR3 meaning, document_id and
-- assessment_threshold_exceedance_id, are ARZ_19 and ARZ_13 -- both already on
-- assessment_regimes, and both editable on the page that survives.
--
-- The enumeration it existed for -- zones x eea_environmentalobjective for a
-- classification year -- is not lost: endpoints/management/assessmentregimes now
-- serves it at /candidates and /generate, decomposing each environmental objective
-- into the four separate ARZ attributes and deriving a conformant ARZ_02. That
-- translation is what this table never did.
--
-- WHY THIS ARCHIVES RATHER THAN CONVERTS. There is no faithful row-by-row conversion:
-- an environmental objective resolves to a pollutant, a protection target, an
-- objective type and a reporting metric only when all four vocabularies have the
-- matching term, and inventing a regime where one does not resolve would report a
-- compliance situation that was never assessed. So every row is snapshotted into
-- assessmentregime_zones_dropped_020 first -- marked with whether a regime already
-- covers it, and whether the bulk fill could recreate it -- and the table is then
-- dropped.
--
-- WHY IT NO LONGER REFUSES. The first version raised instead, so that an operator
-- would convert the rows deliberately. That is wrong in a way only a deployment
-- shows: docker-entrypoint.sh runs migrations before gunicorn, so the raise takes the
-- API down, and the page its hint named -- Management > Assessment Regime Zones >
-- Generate regimes for a year -- ships in the very image that then cannot start. It
-- arrived in the same commit as this file. Worse, /candidates offers only objectives
-- with an UAT/LAT/LTO threshold and a related pollutant, so rows outside that set
-- could never be cleared from the UI at all and the environment would have stayed
-- down indefinitely. dev-raven4 hit exactly that, on 14 rows. Preserving the
-- annotations serves the same purpose as refusing to drop them, and cannot brick an
-- environment.
--
-- eea_environmentalobjective stays. It is a published EEA vocabulary, it is what
-- /candidates enumerates, and dropping it would remove the only machine-readable
-- source of which objective applies to which pollutant.
--
-- Idempotent, and a no-op on a fresh install -- schema.sql no longer creates the
-- table in the same commit, so this finds nothing to drop and skips.
-- ===========================================================================

begin;

do $$
declare
    total       bigint;
    unaccounted bigint;
    recreatable bigint;
begin
    if to_regclass('public.assessmentregime_zones') is null then
        raise notice '020: assessmentregime_zones is already absent, nothing to drop';
        return;
    end if;

    select count(*) into total from assessmentregime_zones;

    -- Nothing to preserve, so do not leave behind an empty table whose meaning
    -- someone has to work out.
    if total = 0 then
        drop table assessmentregime_zones;
        raise notice '020: dropped assessmentregime_zones (it was empty)';
        return;
    end if;

    -- A faithful snapshot of what is being dropped -- every row, not only the
    -- unaccounted ones, so the archive answers "what was in there" as well as "what
    -- do I still owe". CREATE TABLE AS copies no constraints, so this carries no
    -- foreign key to zones, documents or the vocabularies and cannot obstruct a
    -- later migration.
    create table assessmentregime_zones_dropped_020 as
    select arz.id,
           arz.zone_id,
           z.zone_national_code,
           z.name                                as zone_name,
           arz.classification_year,
           arz.environmental_objective_id,
           eo.label                              as environmental_objective,
           eo.assessment_threshold,
           arz.document_id,
           arz.assessment_threshold_exceedance_id,
           ate.label                             as assessment_threshold_exceedance,

           -- The decomposition ARZ needs. A null here is the reason the row could
           -- not become a regime, recorded now rather than re-derived later against
           -- vocabularies that will have moved on.
           eo.related_pollutant                  as pollutant_id,
           ot.id                                 as objective_type_id,
           pt.id                                 as protection_target_id,
           rm.id                                 as reporting_metric_id,

           -- Already covered: a regime exists for the same zone, year and decomposed
           -- objective. Matched on the attributes rather than on ARZ_02, so a regime
           -- whose id was typed by hand still counts.
           exists (
               select 1
                 from assessment_regimes ar
                where ar.zone_id              = arz.zone_id
                  and ar.classification_year  = arz.classification_year
                  and ar.pollutant_id         is not distinct from eo.related_pollutant
                  and ar.objective_type_id    is not distinct from ot.id
                  and ar.protection_target_id is not distinct from pt.id
                  and ar.reporting_metric_id  is not distinct from rm.id)
                                                 as accounted_for,

           -- Whether Generate regimes for a year could put this back. The same filter
           -- as _CANDIDATE_SQL in endpoints/management/assessmentregimes/routes.py:
           -- an objective with no related pollutant cannot become a regime at all
           -- (ARZ_09 is NOT NULL and composes ARZ_02), and the bulk fill lists only
           -- the thresholded objectives the retired grid listed. A row that is false
           -- here has to be entered by hand, and knowing that up front is the whole
           -- point of the column.
           coalesce((eo.assessment_threshold like '%UAT%'
                  or eo.assessment_threshold like '%LAT%'
                  or eo.assessment_threshold like '%LTO%')
                and eo.related_pollutant is not null, false)
                                                 as generatable,
           now()                                 as archived_at

      from assessmentregime_zones arz
      -- Left, not inner: a row whose objective no longer resolves is exactly the kind
      -- this has to keep, and an inner join would drop it in silence.
      left join eea_environmentalobjective eo on eo.id  = arz.environmental_objective_id
      left join zones z                       on z.id   = arz.zone_id
      left join eea_assessmentthresholdexceedances ate
                                              on ate.id = arz.assessment_threshold_exceedance_id
      left join eea_protectiontargets pt on pt.uri = eo.protection_target
      left join eea_reportingmetrics  rm on rm.uri = eo.reporting_metric
      left join eea_objectivetypes    ot on eo.objective_type in (ot.id, ot.uri, ot.notation);

    comment on table assessmentregime_zones_dropped_020 is
        'Snapshot taken by migration 020 of assessmentregime_zones before dropping it. '
        'No AQR3 table ever read that table, but each row records a classification '
        'document and an assessment threshold exceedance an operator chose. Rows with '
        'accounted_for = false are the outstanding ones: no assessment_regimes row '
        'covers that zone, year and decomposed objective. Of those, generatable = true '
        'can be recreated from Management > Assessment Regime Zones > Generate regimes '
        'for a year, and generatable = false has to be entered by hand. Drop this table '
        'once the outstanding rows are reconciled.';

    select count(*) filter (where not accounted_for),
           count(*) filter (where not accounted_for and generatable)
      into unaccounted, recreatable
      from assessmentregime_zones_dropped_020;

    raise notice '020: archived % row(s) to assessmentregime_zones_dropped_020 -- '
                 '% not covered by any regime, of which % can be recreated from '
                 'Generate regimes for a year', total, unaccounted, recreatable;

    drop table assessmentregime_zones;
    raise notice '020: dropped assessmentregime_zones';
end $$;

insert into schema_version (version, description)
values ('4.502.20',
        'dropped assessmentregime_zones. A v4.8.0 zone x environmental-objective grid '
        'that no export read and that could not express AQR3 ARZ -- no AssessmentRegimeId, '
        'and pollutant, protection target, objective type and reporting metric collapsed '
        'into one environmental objective. assessment_regimes is and remains the ARZ '
        'table; its /candidates and /generate endpoints took over the bulk fill, writing '
        'real regimes with derived ARZ_02 ids. Any rows present were snapshotted first '
        'into assessmentregime_zones_dropped_020, where accounted_for = false marks the '
        'annotations still owed a regime')
on conflict (version) do nothing;

commit;
