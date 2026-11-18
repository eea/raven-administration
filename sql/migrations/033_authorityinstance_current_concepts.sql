-- ===========================================================================
-- 033 — eea_authorityinstance holds the concepts EEA publishes today
--
-- AQR3 AUT_05 AuthorityInstance is exported as eea_authorityinstance.id
-- (core/reporting/aqr3/spec.py), so the id has to be a concept of
-- aq/authorityinstance. EEA has renamed that vocabulary's concepts since migration
-- 019 was written. As published on 2026-11-18 it has nine, each with
-- id = notation = the last segment of its URI:
--
--     model  network  samplingpoint  station  nuts0  nuts1  nuts2  nuts3  zone
--
-- 019 moved databases onto the names published then -- AirQualityNetwork,
-- AirQualityStationEoICode, SamplingPoint, Model -- and dev-raven4 carries a third
-- spelling (Network, StationEoICode). None of those is a concept any more, so an
-- authority pointing at one exports an AuthorityInstance outside the code list.
-- Re-running populate_vocabularies.py does not repair it: the loader upserts by id,
-- so it adds the lowercase rows beside the old ones and the Authorities page offers
-- every concept twice.
--
-- So: write the nine current rows (verbatim from the EEA CSV, so this works
-- offline), move every reference from an old spelling to its concept, and delete
-- the old rows. The mapping is by name, case-insensitive; it is the only hardcoded
-- thing here, as in 019. A row this migration does not recognise is kept and named
-- in a notice rather than deleted.
--
-- Referrers come from pg_constraint, as in 016, 017 and 019. Today there is one --
-- authorities.authority_instance_id -- and each delete is preceded by a repoint, a
-- re-count and a raise if anything is left.
--
-- Idempotent: on a database that already holds exactly the nine rows it changes
-- nothing. On a fresh install schema.sql records it as applied; vocabularies.py
-- loads the same nine.
-- ===========================================================================

begin;

do $$
declare
    pair      record;
    ref       record;
    updated   bigint;
    remaining bigint;
    moved     bigint := 0;
    dropped   int    := 0;
    unknown   text;
begin
    -- The current concepts.
    create temp table _ai_concept (id text primary key, label text, notation text, uri text)
        on commit drop;
    insert into _ai_concept (id, label, notation, uri) values
        ('model',         'ModelObjectiveEstimation.AssessmentMethodId', 'model',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/model'),
        ('network',       'MeasurementStation.NetworkId',                'network',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/network'),
        ('samplingpoint', 'SamplingPoint.AssessmentMethodId',            'samplingpoint',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/samplingpoint'),
        ('station',       'MeasurementStation.StationEoICode',           'station',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/station'),
        ('nuts0',         'Authority.CountryCode',                       'nuts0',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/nuts0'),
        ('nuts1',         'AssessmentRegimeZone.ZoneId',                 'nuts1',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/nuts1'),
        ('nuts2',         'AssessmentRegimeZone.ZoneId',                 'nuts2',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/nuts2'),
        ('nuts3',         'AssessmentRegimeZone.ZoneId',                 'nuts3',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/nuts3'),
        ('zone',          'AssessmentRegimeZone.ZoneId',                 'zone',
         'http://dd.eionet.europa.eu/vocabulary/aq/authorityinstance/zone');

    -- Every spelling a Raven database has carried, lowercased, -> its concept.
    create temp table _ai_alias (alias text primary key, concept text) on commit drop;
    insert into _ai_alias (alias, concept) values
        ('model', 'model'),
        ('network', 'network'),           ('airqualitynetwork', 'network'),
        ('station', 'station'),           ('stationeoicode', 'station'),
        ('airqualitystationeoicode', 'station'),
        ('samplingpoint', 'samplingpoint'), ('spo', 'samplingpoint'),
        ('nuts0', 'nuts0'), ('nuts1', 'nuts1'), ('nuts2', 'nuts2'), ('nuts3', 'nuts3'),
        ('zone', 'zone');

    -- The rows to move: a known spelling that is not the concept's own id.
    create temp table _ai_move on commit drop as
        select ai.id as old_id, a.concept as new_id
          from eea_authorityinstance ai
          join _ai_alias a on a.alias = lower(ai.id)
         where ai.id <> a.concept;

    -- Free their URIs: one of them may hold the URI the concept row needs, and uri is
    -- unique.
    update eea_authorityinstance ai
       set uri = ai.uri || '#superseded-033'
      from _ai_move m
     where ai.id = m.old_id
       and ai.uri not like '%#superseded-033';

    -- The concept rows, label/notation/uri restated.
    insert into eea_authorityinstance (id, label, notation, uri)
    select id, label, notation, uri from _ai_concept
    on conflict (id) do update
       set label = excluded.label, notation = excluded.notation, uri = excluded.uri
     where (eea_authorityinstance.label, eea_authorityinstance.notation,
            eea_authorityinstance.uri)
           is distinct from (excluded.label, excluded.notation, excluded.uri);

    -- Repoint every reference, then delete the old row.
    for pair in select old_id, new_id from _ai_move order by old_id loop
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
               and frel.relname = 'eea_authorityinstance'
               and array_length(con.conkey, 1) = 1
             order by rel.relname, att.attname
        loop
            execute format('update %I set %I = $1 where %I = $2', ref.child, ref.col, ref.col)
                using pair.new_id, pair.old_id;
            get diagnostics updated = row_count;
            if updated > 0 then
                raise notice '033: %.% -- % row(s) moved from % to %',
                    ref.child, ref.col, updated, pair.old_id, pair.new_id;
            end if;
            moved := moved + updated;

            execute format('select count(*) from %I where %I = $1', ref.child, ref.col)
                into remaining using pair.old_id;
            if remaining > 0 then
                raise exception
                    '033: eea_authorityinstance row "%" still has % reference(s) from '
                    '%.% after repointing to "%". Refusing to delete it.',
                    pair.old_id, remaining, ref.child, ref.col, pair.new_id;
            end if;
        end loop;

        delete from eea_authorityinstance where id = pair.old_id;
        dropped := dropped + 1;
    end loop;

    select string_agg(id, ', ' order by id) into unknown
      from eea_authorityinstance
     where id not in (select id from _ai_concept);
    if unknown is not null then
        raise notice '033: kept rows that are not a current aq/authorityinstance concept: % '
                     '-- check them by hand', unknown;
    end if;

    raise notice '033: % old row(s) replaced, % reference(s) moved', dropped, moved;
end
$$;

insert into schema_version (version, description)
values ('4.502.33', 'eea_authorityinstance holds the nine concepts aq/authorityinstance '
                    'publishes (network, station, samplingpoint, model, nuts0-3, zone); '
                    'authorities moved off the retired spellings')
on conflict (version) do nothing;

commit;
