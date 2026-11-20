-- ===========================================================================
-- 034 — AQR3 review fixes (4sFera, Task #3184, 2026-11-20)
--
-- 4sFera compared the Raven 4 CSV downloads with the v5.02 reporting guide. Three
-- of its findings are data, not code, and are repaired here:
--
-- A. Vocabularies that drifted from what EEA publishes.
--
--    MOE_07 MethodApplication (eea_modelapplication). EEA replaced `sr` with
--    `spatialrepresentativeness` on 2026-10-20 and added `aei` on 2026-11-18.
--    dev-raven4 still holds `sr`, and sql/data.sql seeded an invented
--    `representativeness`. Both are moved to `spatialrepresentativeness`.
--
--    DOC_02 DataTable (eea_datatable). The export now writes the concept id
--    (AssessmentRegimeZone), not the notation (ARZ). vocabularies.py's fallback
--    invented lowercase ids (samplingprocess, model, ...) that are not concepts;
--    they are moved to the concept they stood for. `planscenario` has none and is
--    kept, with a notice.
--
--    DOC_03 DocumentType (eea_documentobject). The loader read aq/documentobject,
--    which returns HTTP 500, so every database carries its invented fallback (AQD,
--    Classificationreport). DOC_03 names aq/documenttype (reporting guide site,
--    tables/Documentation.html), which is published: nine concepts, written below.
--    Each document takes the type of the column that references it, as the guide's
--    Documentation Mapping Specification pairs them: a network's document is a
--    NetworkDocument, a model's method description a MethodDocument, and so on. A
--    document nothing references keeps its type, and a type no document uses any
--    more is deleted.
--
--    CAM_07 AssessmentType, SPL_05 StationArea, SPP_11 EquivalenceDemonstrated.
--    sql/data.sql seeded these three with notation = label, so a database installed
--    from it exports `Fixed measurement` where the code list says `fixed`. Their ids
--    are the EEA notations (id_from=notation), so the notation is set back to the id
--    wherever it holds the label instead.
--
--    Mechanism as in 033: write the concept rows verbatim (works offline), repoint
--    every foreign key found in pg_constraint, re-count, and only then delete.
--
-- B. SPO_03 SamplingPointReferenceId. Fully mandatory format,
--    SPOref_<StationEoICode>_<PollutantId as 4 digits>_<idx>, which nothing built or
--    checked until now: raven_local had it NULL on 609 of 609 reportable points,
--    and 4sFera found hand-typed ones with an unpadded pollutant id. Every point
--    whose station has an EoI code and whose pollutant is an EEA one gets a
--    conforming reference, unless it already has one naming its own station and
--    pollutant. The index is the lowest one free for that station and pollutant.
--    The sampling point routes generate and validate it from now on.
--
-- Idempotent: a second run finds nothing to move and nothing to fill. On a fresh
-- install schema.sql records it as applied; data.sql and vocabularies.py carry the
-- same rows.
-- ===========================================================================

begin;

-- ---------------------------------------------------------------------------
-- A. Vocabularies
-- ---------------------------------------------------------------------------
do $$
declare
    pair      record;
    ref       record;
    updated   bigint;
    remaining bigint;
    moved     bigint := 0;
    dropped   int    := 0;
    unknown   text;
    v         text;
begin
    create temp table _m034_concept (vocab text, id text, label text, notation text, uri text,
                                     primary key (vocab, id)) on commit drop;
    insert into _m034_concept (vocab, id, label, notation, uri) values
        -- aq/modelapplication, verbatim from the EEA CSV of 2026-11-20.
        ('eea_modelapplication', 'adjustment', 'Natural source adjustment', 'adjustment',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/adjustment'),
        ('eea_modelapplication', 'airqualityconcentrations', 'air quality concentrations',
         'airqualityconcentrations',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/airqualityconcentrations'),
        ('eea_modelapplication', 'airqualityforecasting', 'air quality forecasting',
         'airqualityforecasting',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/airqualityforecasting'),
        ('eea_modelapplication', 'assessment', 'Assessment for Compliance', 'assessment',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/assessment'),
        ('eea_modelapplication', 'populationexposure', 'population exposure',
         'populationexposure',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/populationexposure'),
        ('eea_modelapplication', 'scenario', 'Scenario', 'scenario',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/scenario'),
        ('eea_modelapplication', 'sourceapportionment', 'source apportionment',
         'sourceapportionment',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/sourceapportionment'),
        ('eea_modelapplication', 'spatialrepresentativeness', 'spatial representativeness',
         'spatialrepresentativeness',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/spatialrepresentativeness'),
        ('eea_modelapplication', 'aei', 'average exposure indicator', 'aei',
         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/aei'),
        -- aq/datatable, verbatim from the EEA CSV of 2026-11-20 (id = URI suffix).
        ('eea_datatable', 'PollutionLevelAdjustment', 'PollutionLevelAdjustment (ADJ)', 'ADJ',
         'http://dd.eionet.europa.eu/vocabulary/aq/datatable/PollutionLevelAdjustment'),
        ('eea_datatable', 'AssessmentRegimeZone', 'AssessmentRegimeZone (ARZ)', 'ARZ',
         'http://dd.eionet.europa.eu/vocabulary/aq/datatable/AssessmentRegimeZone'),
        ('eea_datatable', 'CompliancePlanLink', 'CompliancePlanLink (CPL)', 'CPL',
         'http://dd.eionet.europa.eu/vocabulary/aq/datatable/CompliancePlanLink'),
        ('eea_datatable', 'ModelObjectiveEstimation', 'ModelObjectiveEstimation (MOE)', 'MOE',
         'http://dd.eionet.europa.eu/vocabulary/aq/datatable/ModelObjectiveEstimation'),
        ('eea_datatable', 'SamplingProcess', 'SamplingProcess (SPP)', 'SPP',
         'http://dd.eionet.europa.eu/vocabulary/aq/datatable/SamplingProcess'),
        ('eea_datatable', 'SourceApportionment', 'SourceApportionment (SAP)', 'SAP',
         'http://dd.eionet.europa.eu/vocabulary/aq/datatable/SourceApportionment'),
        ('eea_datatable', 'MeasurementStation', 'MeasurementStation (STA)', 'STA',
         'http://dd.eionet.europa.eu/vocabulary/aq/datatable/MeasurementStation'),
        -- aq/documenttype, verbatim from the EEA CSV of 2026-11-20. The table is named
        -- after aq/documentobject, which is not the vocabulary DOC_03 names.
        ('eea_documentobject', 'ClassificationDocument', 'Classification Document', 'ClassificationDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/ClassificationDocument'),
        ('eea_documentobject', 'DataQualityDocument', 'Data Quality Document', 'DataQualityDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/DataQualityDocument'),
        ('eea_documentobject', 'EquivalenceDemonstrationDocument', 'Equivalence Demonstration Document', 'EquivalenceDemonstrationDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/EquivalenceDemonstrationDocument'),
        ('eea_documentobject', 'PlanDocument', 'Plan Document', 'PlanDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/PlanDocument'),
        ('eea_documentobject', 'ProcessDocument', 'Process Document', 'ProcessDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/ProcessDocument'),
        ('eea_documentobject', 'NetworkDocument', 'Network Document', 'NetworkDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/NetworkDocument'),
        ('eea_documentobject', 'MethodDocument', 'Method Document', 'MethodDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/MethodDocument'),
        ('eea_documentobject', 'AdjustmentDocument', 'Adjustment Document', 'AdjustmentDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/AdjustmentDocument'),
        ('eea_documentobject', 'SourceApportionmentDocument', 'Source Apportionment Document', 'SourceApportionmentDocument',
         'http://dd.eionet.europa.eu/vocabulary/aq/documenttype/SourceApportionmentDocument');

    -- Every spelling a Raven database has carried, lowercased, -> its concept.
    create temp table _m034_alias (vocab text, alias text, concept text,
                                   primary key (vocab, alias)) on commit drop;
    insert into _m034_alias (vocab, alias, concept)
    select c.vocab, lower(c.id), c.id from _m034_concept c;
    insert into _m034_alias (vocab, alias, concept) values
        ('eea_modelapplication', 'sr',                       'spatialrepresentativeness'),
        ('eea_modelapplication', 'representativeness',       'spatialrepresentativeness'),
        ('eea_datatable',        'model',                    'ModelObjectiveEstimation'),
        ('eea_datatable',        'network',                  'MeasurementStation'),
        ('eea_documentobject',   'classificationreport',     'ClassificationDocument'),
        -- The guide workbook's example spellings, which an earlier draft of this
        -- migration wrote on raven_local.
        ('eea_documentobject',   'processdocumentation',     'ProcessDocument'),
        ('eea_documentobject',   'modeldocument',            'MethodDocument'),
        ('eea_documentobject',   'sourceappdocument',        'SourceApportionmentDocument')
    on conflict do nothing;

    -- Rows to move: a known spelling that is not the concept's own id.
    create temp table _m034_move (vocab text, old_id text, new_id text) on commit drop;
    for v in select distinct c.vocab from _m034_concept c loop
        execute format(
            'insert into _m034_move select %L, t.id, a.concept from %I t '
            'join _m034_alias a on a.vocab = %L and a.alias = lower(t.id) '
            'where t.id <> a.concept', v, v, v);
        -- Free their URIs: one may hold the URI the concept row needs.
        execute format(
            'update %I t set uri = t.uri || ''#superseded-034'' from _m034_move m '
            'where m.vocab = %L and t.id = m.old_id and t.uri not like ''%%#superseded-034''',
            v, v);
        -- The concept rows, restated.
        execute format(
            'insert into %I (id, label, notation, uri) '
            'select id, label, notation, uri from _m034_concept where vocab = %L '
            'on conflict (id) do update set label = excluded.label, '
            'notation = excluded.notation, uri = excluded.uri '
            'where (%I.label, %I.notation, %I.uri) is distinct from '
            '(excluded.label, excluded.notation, excluded.uri)',
            v, v, v, v, v);
    end loop;

    -- Each document takes the type of the column that references it. A document
    -- referenced as two different types keeps the first in this order, with a notice.
    create temp table _m034_doctype on commit drop as
    select distinct on (doc) doc, kind, count(*) over (partition by doc) as kinds
      from (
        select distinct d, k, p from (
            select network_document_id, 'NetworkDocument', 1 from networks
            union all select data_quality_document_id, 'DataQualityDocument', 2 from processes
            union all select data_quality_document_id, 'DataQualityDocument', 2 from models
            union all select equivalence_demonstration_document_id,
                             'EquivalenceDemonstrationDocument', 3 from processes
            union all select process_document_id, 'ProcessDocument', 4 from processes
            union all select method_document_id, 'MethodDocument', 5 from models
            union all select adjustment_document_id, 'AdjustmentDocument', 7
                        from pollution_level_adjustment
            union all select classification_document_id, 'ClassificationDocument', 6
                        from assessment_regimes
        ) r(d, k, p) where d is not null
      ) x(doc, kind, prio)
     order by doc, prio;

    for ref in select doc from _m034_doctype where kinds > 1 order by doc loop
        raise notice '034: document % is referenced as more than one type; given %',
            ref.doc, (select kind from _m034_doctype where doc = ref.doc);
    end loop;

    update documents d set documentobject_id = t.kind
      from _m034_doctype t
     where d.id = t.doc and d.documentobject_id is distinct from t.kind;
    get diagnostics updated = row_count;
    if updated > 0 then
        raise notice '034: % document(s) given the DocumentType of the column referencing them',
            updated;
    end if;

    -- A document nothing references, still on a type that is not a concept, takes the
    -- type its DataTable allows when that table has only one document column.
    -- SamplingProcess and ModelObjectiveEstimation have several, so they are left.
    update documents d set documentobject_id = x.kind
      from (values ('MeasurementStation',       'NetworkDocument'),
                   ('PollutionLevelAdjustment', 'AdjustmentDocument'),
                   ('CompliancePlanLink',       'PlanDocument'),
                   ('SourceApportionment',      'SourceApportionmentDocument'),
                   ('AssessmentRegimeZone',     'ClassificationDocument')) x(tbl, kind)
     where d.datatable_id = x.tbl
       and d.documentobject_id not in
           (select id from _m034_concept where vocab = 'eea_documentobject')
       and lower(d.documentobject_id) not in
           (select alias from _m034_alias where vocab = 'eea_documentobject');
    get diagnostics updated = row_count;
    if updated > 0 then
        raise notice '034: % unreferenced document(s) given the one DocumentType their DataTable allows',
            updated;
    end if;

    -- Repoint every reference, then delete the old row.
    for pair in select vocab, old_id, new_id from _m034_move order by vocab, old_id loop
        for ref in
            select rel.relname::text as child, att.attname::text as col
              from pg_constraint con
              join pg_class rel     on rel.oid  = con.conrelid
              join pg_class frel    on frel.oid = con.confrelid
              join pg_namespace fn  on fn.oid   = frel.relnamespace
              join pg_attribute att on att.attrelid = rel.oid
                                   and att.attnum   = con.conkey[1]
             where con.contype = 'f'
               and fn.nspname = 'public'
               and frel.relname = pair.vocab
               and array_length(con.conkey, 1) = 1
             order by rel.relname, att.attname
        loop
            execute format('update %I set %I = $1 where %I = $2', ref.child, ref.col, ref.col)
                using pair.new_id, pair.old_id;
            get diagnostics updated = row_count;
            if updated > 0 then
                raise notice '034: %.% -- % row(s) moved from % to %',
                    ref.child, ref.col, updated, pair.old_id, pair.new_id;
            end if;
            moved := moved + updated;

            execute format('select count(*) from %I where %I = $1', ref.child, ref.col)
                into remaining using pair.old_id;
            if remaining > 0 then
                raise exception
                    '034: % row "%" still has % reference(s) from %.% after repointing '
                    'to "%". Refusing to delete it.',
                    pair.vocab, pair.old_id, remaining, ref.child, ref.col, pair.new_id;
            end if;
        end loop;

        execute format('delete from %I where id = $1', pair.vocab) using pair.old_id;
        dropped := dropped + 1;
    end loop;

    -- The invented DocumentType fallback no document uses any more.
    delete from eea_documentobject o
     where o.id not in (select id from _m034_concept where vocab = 'eea_documentobject')
       and not exists (select 1 from documents d where d.documentobject_id = o.id);
    get diagnostics updated = row_count;
    dropped := dropped + updated;

    for v in select distinct c.vocab from _m034_concept c order by 1 loop
        execute format(
            'select string_agg(id, '', '' order by id) from %I '
            'where id not in (select id from _m034_concept where vocab = %L)', v, v)
            into unknown;
        if unknown is not null then
            raise notice '034: % keeps rows that are not a current concept: % -- check them by hand',
                v, unknown;
        end if;
    end loop;

    raise notice '034: % old vocabulary row(s) removed, % reference(s) moved', dropped, moved;
end
$$;

-- Notations that hold the label (data.sql seed).
do $$
declare
    t       text;
    updated bigint;
begin
    foreach t in array array['eea_assessmenttypes', 'eea_areaclassifications',
                             'eea_equivalencedemonstrated'] loop
        execute format('update %I set notation = id '
                       'where notation = label and notation is distinct from id', t);
        get diagnostics updated = row_count;
        if updated > 0 then
            raise notice '034: %.notation -- % row(s) set from the label back to the id', t, updated;
        end if;
    end loop;
end
$$;

-- ---------------------------------------------------------------------------
-- B. SPO_03 SamplingPointReferenceId
-- ---------------------------------------------------------------------------
do $$
declare
    r       record;
    n       int;
    filled  int := 0;
    skipped int := 0;
begin
    for r in
        select sp.id, sp.sampling_point_reference_id as old_ref,
               'SPOref_' || btrim(st.station_eoi_code) || '_'
                         || lpad(sp.pollutant_id::text, 4, '0') as prefix
          from sampling_points sp
          join stations st on st.id = sp.station_id
         where st.station_eoi_code is not null
           and btrim(st.station_eoi_code) ~ '^[A-Za-z0-9.+-]+$'
           and sp.pollutant_id > 0
         order by 3, sp.id
    loop
        -- Already conforming and naming this point's own station and pollutant.
        continue when r.old_ref ~ '^SPOref_[A-Za-z0-9.+-]+_[0-9]{4}_[0-9]{1,2}$'
                  and regexp_replace(r.old_ref, '_[^_]+$', '') = r.prefix;

        if length(r.prefix) + 2 > 32 then
            raise notice '034: sampling point % -- % does not fit SPO_03 varchar(32); left as is',
                r.id, r.prefix || '_1';
            skipped := skipped + 1;
            continue;
        end if;

        select min(i) into n
          from generate_series(1, 99) i
         where not exists (select 1 from sampling_points o
                            where o.sampling_point_reference_id = r.prefix || '_' || i
                              and o.id <> r.id);
        if n is null then
            raise notice '034: sampling point % -- all 99 indexes of %_<n> are taken', r.id, r.prefix;
            skipped := skipped + 1;
            continue;
        end if;

        update sampling_points set sampling_point_reference_id = r.prefix || '_' || n
         where id = r.id;
        filled := filled + 1;
    end loop;

    raise notice '034: % SamplingPointReferenceId(s) generated, % left as they were', filled, skipped;
end
$$;

insert into schema_version (version, description)
values ('4.502.34', 'AQR3 review (4sFera): current aq/modelapplication, aq/datatable and '
                    'guide DocumentType concepts; assessmenttype/areaclassification/'
                    'equivalencedemonstrated notations; SamplingPointReferenceId generated in the '
                    'mandatory SPOref_<EoI>_<pollutant 4 digits>_<n> format')
on conflict (version) do nothing;

commit;
