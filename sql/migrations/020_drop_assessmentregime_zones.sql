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
-- WHY THIS REFUSES RATHER THAN MIGRATES. There is no faithful row-by-row conversion:
-- an environmental objective resolves to a pollutant, a protection target, an
-- objective type and a reporting metric only when all four vocabularies have the
-- matching term, and inventing a regime where one does not resolve would report a
-- compliance situation that was never assessed. So rows that are not already
-- represented by a regime are counted and the migration aborts, naming the query to
-- run and the page to run it from. Re-run after generating the regimes.
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
    orphaned bigint;
begin
    if to_regclass('public.assessmentregime_zones') is null then
        raise notice '020: assessmentregime_zones is already absent, nothing to drop';
        return;
    end if;

    -- A row is accounted for when a regime already covers the same zone, year and
    -- decomposed objective. Matched on the attributes rather than on ARZ_02 so a
    -- regime whose id was typed by hand still counts.
    select count(*)
      into orphaned
      from assessmentregime_zones arz
      join eea_environmentalobjective eo on eo.id = arz.environmental_objective_id
      left join eea_protectiontargets pt on pt.uri = eo.protection_target
      left join eea_reportingmetrics  rm on rm.uri = eo.reporting_metric
      left join eea_objectivetypes    ot on eo.objective_type in (ot.id, ot.uri, ot.notation)
     where not exists (
             select 1
               from assessment_regimes ar
              where ar.zone_id              = arz.zone_id
                and ar.classification_year  = arz.classification_year
                and ar.pollutant_id         is not distinct from eo.related_pollutant
                and ar.objective_type_id    is not distinct from ot.id
                and ar.protection_target_id is not distinct from pt.id
                and ar.reporting_metric_id  is not distinct from rm.id);

    if orphaned > 0 then
        raise exception using
            message = format('020: %s assessmentregime_zones row(s) have no matching '
                             'assessment regime', orphaned),
            detail  = 'These annotations would be lost. They were never exported -- no '
                      'AQR3 table reads assessmentregime_zones -- but they record which '
                      'threshold and classification document an operator chose.',
            hint    = 'Generate the regimes first: Management > Assessment Regime Zones > '
                      'Generate regimes for a year, once per classification year present. '
                      'To see what is unaccounted for, run the SELECT in the body of this '
                      'migration with count(*) replaced by arz.*. Then re-run this migration.';
    end if;

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
        'real regimes with derived ARZ_02 ids')
on conflict (version) do nothing;

commit;
