-- ===========================================================================
-- 019 — eea_authorityinstance keys on the concept name, not on skos:notation
--
-- aq/authorityinstance is unlike almost every other aq/* vocabulary: its
-- skos:notation is not a code for the concept, it is a cross-reference to the AQR3
-- attribute that carries the id. So the nine published concepts
--
--     .../nuts0                     notation AUTH_01
--     .../nuts1                     notation ARZ_05
--     .../nuts2                     notation ARZ_05
--     .../nuts3                     notation ARZ_05
--     .../zone                      notation ZOG_02
--     .../AirQualityNetwork         notation STA_03
--     .../AirQualityStationEoICode  notation STA_07
--     .../SamplingPoint             notation SPO_02
--     .../Model                     notation MOD_02
--
-- have only seven distinct notations, and ARZ_05 stands for three different NUTS
-- levels at once. sql/populate_vocabularies.py used the default id_from='notation'
-- here, so nuts1 and nuts2 were merged into whichever ARZ_05 row was written last
-- and simply do not exist -- a country cannot report an authority at NUTS level 1
-- or 2 at all.
--
-- sql/vocabularies.py already names this case in its own docstring: uri_suffix is
-- for "where the notation is not URL-safe ... or is a short code". The registry is
-- switched to id_from='uri_suffix' in the same commit, so a fresh install now
-- loads all nine, and this moves the databases that took the old shape.
--
-- The reporting guide's Authority example writes AuthorityInstance as `nuts0`, so
-- the concept name is also the value AUT_05 has to export -- core/reporting/aqr3/
-- spec.py is changed alongside. (DOC_02 has the same defect: eea_datatable is
-- already uri_suffix, but DOC exports dt.notation, giving `STA` where the guide's
-- Documentation sheet writes the concept name. Not touched here -- it changes an
-- existing dataflow's output and deserves its own change.)
--
-- A SECOND, OVERLAPPING SET. raven-rn3-db/populate_lookups_v4_2.py -- out of tree,
-- and what sql/data.sql used to point operators at -- seeded eight of these
-- concepts by hand under `urn:raven:authority:*` URIs it invented, using the
-- guide's prose spelling rather than the published concept names. So an AirQUIS
-- database holds up to two rows per concept: one loader-produced row keyed by
-- notation with the real URI, and one hand-seeded row keyed by a name with an
-- invented URI. Three of the invented names are not concept names at all and have
-- no derivable relation to the real ones, so that mapping is stated explicitly
-- below; it is the only hardcoded thing here.
--
-- Referrers come from pg_constraint rather than a list, as in migrations 016 and
-- 017. Today there is exactly one -- authorities.authority_instance_id, ON UPDATE
-- CASCADE -- so every rekey carries its referrers for free, and every delete is
-- preceded by an explicit repoint, a re-count and a raise if anything is left.
--
-- `notation` and `label` are deliberately left alone: populate_vocabularies.py
-- owns them and will restate them from the RDF on the next refresh. This migration
-- only moves ids and replaces invented URIs, which is what no loader run can undo.
--
-- Idempotent, and a no-op on a fresh install -- sql/data.sql leaves this
-- vocabulary deliberately unseeded, so there is nothing to move.
-- ===========================================================================

begin;

do $$
declare
    row_        record;
    ref         record;
    pair        record;
    target      text;
    base        text;
    remaining   bigint;
    updated     bigint;
    collapsed   int    := 0;
    rekeyed     int    := 0;
    retargeted  int    := 0;
    moved       bigint := 0;
    fixed_uris  int    := 0;
begin
    if not exists (select 1 from eea_authorityinstance) then
        raise notice '019: eea_authorityinstance is empty -- nothing to normalise';
    else

    -- The stored URIs come from the RDF's rdf:about, which is http: rather than the
    -- https: of DD_BASE, so the base is taken from a sibling row instead of being
    -- written here. Null only if no row has a real URI at all.
    select regexp_replace(uri, '/[^/]+$', '/') into base
      from eea_authorityinstance
     where strpos(uri, '://') > 0
     order by id
     limit 1;

    -- ------------------------------------------------------------------
    -- Step 1. Move every loader-produced row from its notation onto its own
    -- concept name, collapsing onto a hand-seeded twin where one is in the way.
    -- ------------------------------------------------------------------
    for row_ in
        select id, uri from eea_authorityinstance
         where strpos(uri, '://') > 0
         order by id
    loop
        target := regexp_replace(row_.uri, '^.*/', '');
        if target = '' or target = row_.id then
            continue;
        end if;

        if exists (select 1 from eea_authorityinstance t where t.id = target) then
            -- The twin holds the right id and the wrong URI; this row holds the
            -- wrong id and the right URI. Referrers move onto this row first, then
            -- the twin goes, then this row takes its id -- so the referrers end up
            -- on the surviving row without ever pointing at nothing.
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
                execute format('update %I set %I = $1 where %I = $2',
                               ref.child, ref.col, ref.col)
                    using row_.id, target;
                get diagnostics updated = row_count;
                if updated > 0 then
                    raise notice '019: %.% -- % row(s) moved from % to %',
                        ref.child, ref.col, updated, target, row_.id;
                end if;
                moved := moved + updated;
            end loop;

            -- Second pass, so a foreign key visited earlier cannot have been
            -- re-populated by one visited later.
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
            loop
                execute format('select count(*) from %I where %I = $1',
                               ref.child, ref.col)
                    into remaining using target;
                if remaining > 0 then
                    raise exception
                        '019: eea_authorityinstance row "%" still has % reference(s) '
                        'from %.% after repointing to "%". Refusing to delete it.',
                        target, remaining, ref.child, ref.col, row_.id;
                end if;
            end loop;

            delete from eea_authorityinstance where id = target;
            collapsed := collapsed + 1;
        end if;

        update eea_authorityinstance set id = target where id = row_.id;
        rekeyed := rekeyed + 1;
        raise notice '019: % rekeyed to % (the last segment of its own URI)',
            row_.id, target;
    end loop;

    -- ------------------------------------------------------------------
    -- Step 2. The hand-seeded rows whose id is not a concept name. There is no rule
    -- to derive these from -- the names are the guide's prose ("zone, network,
    -- nuts0 ... station, SPO") while the vocabulary spells the same three concepts
    -- AirQualityNetwork, AirQualityStationEoICode and SamplingPoint -- so the
    -- mapping is stated. nuts0-3 and zone need no entry: the prose and the
    -- vocabulary agree on those, and step 1 has already dealt with them.
    -- ------------------------------------------------------------------
    for pair in
        select * from (values ('network', 'AirQualityNetwork'),
                              ('station', 'AirQualityStationEoICode'),
                              ('SPO',     'SamplingPoint')) as v(invented, concept)
    loop
        if not exists (select 1 from eea_authorityinstance where id = pair.invented) then
            continue;
        end if;

        if not exists (select 1 from eea_authorityinstance where id = pair.concept) then
            -- The published concept is absent, so this row is the only carrier of it.
            -- Rekey rather than delete; step 3 then gives it the real URI.
            update eea_authorityinstance set id = pair.concept where id = pair.invented;
            retargeted := retargeted + 1;
            raise notice '019: % rekeyed to the published concept name %',
                pair.invented, pair.concept;
            continue;
        end if;

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
            execute format('update %I set %I = $1 where %I = $2',
                           ref.child, ref.col, ref.col)
                using pair.concept, pair.invented;
            get diagnostics updated = row_count;
            if updated > 0 then
                raise notice '019: %.% -- % row(s) moved from % to %',
                    ref.child, ref.col, updated, pair.invented, pair.concept;
            end if;
            moved := moved + updated;
        end loop;

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
        loop
            execute format('select count(*) from %I where %I = $1',
                           ref.child, ref.col)
                into remaining using pair.invented;
            if remaining > 0 then
                raise exception
                    '019: eea_authorityinstance row "%" still has % reference(s) from '
                    '%.% after repointing to "%". Refusing to delete it.',
                    pair.invented, remaining, ref.child, ref.col, pair.concept;
            end if;
        end loop;

        delete from eea_authorityinstance where id = pair.invented;
        collapsed := collapsed + 1;
        raise notice '019: invented row % dropped -- % carries that concept',
            pair.invented, pair.concept;
    end loop;

    -- ------------------------------------------------------------------
    -- Step 3. Whatever still holds an invented URI is a real concept that no loader
    -- run has reached (nuts1 and nuts2 on an AirQUIS database, because the notation
    -- convention merged them). The id is already the concept name, so the URI is
    -- derivable from a sibling.
    -- ------------------------------------------------------------------
    if base is null then
        if exists (select 1 from eea_authorityinstance where strpos(uri, '://') = 0) then
            raise warning
                '019: no row carries a real vocabulary URI, so the invented ones cannot '
                'be corrected by derivation. Run sql/populate_vocabularies.py to load '
                'aq/authorityinstance, then re-run this migration.';
        end if;
    else
        update eea_authorityinstance
           set uri = base || id
         where strpos(uri, '://') = 0;
        get diagnostics fixed_uris = row_count;
        if fixed_uris > 0 then
            raise notice '019: % row(s) given their real vocabulary URI under %',
                fixed_uris, base;
        end if;
    end if;

    raise notice '019: % row(s) rekeyed onto their concept name, % retargeted, '
                 '% duplicate(s) collapsed, % reference(s) repointed',
        rekeyed, retargeted, collapsed, moved;

    -- Absolute: every surviving row must be keyed by a concept name and carry a real
    -- URI, or the vocabulary is still in two conventions.
    select count(*) into remaining
      from eea_authorityinstance
     where strpos(id, '://') > 0
        or id ~ '^(AUTH|ARZ|ZOG|STA|SPO|MOD)_[0-9]+$';
    if remaining > 0 then
        raise exception
            '019: % eea_authorityinstance row(s) are still keyed by an AQR3 attribute '
            'code rather than a concept name.', remaining;
    end if;

    raise notice '019: notation and label are left as they are -- '
                 'sql/populate_vocabularies.py owns them and restates them from the '
                 'RDF on the next refresh, which will also add any concept missing '
                 'here (nuts1 / nuts2 on a database that never had them)';
    end if;
end $$;

comment on table eea_authorityinstance is
    'AQR3 AUT_05 AuthorityInstance. Keyed by the concept name (nuts0 ... nuts3, zone, '
    'AirQualityNetwork, AirQualityStationEoICode, SamplingPoint, Model), not by '
    'skos:notation: the notation of this vocabulary is a cross-reference to the AQR3 '
    'attribute holding the id, and ARZ_05 stands for three NUTS levels at once';

insert into schema_version (version, description)
values ('4.502.19',
        'eea_authorityinstance keys on the concept name rather than skos:notation. This '
        'vocabulary uses the notation as a cross-reference to the AQR3 attribute that '
        'carries the id, so ARZ_05 covers nuts1, nuts2 and nuts3 alike and the notation '
        'convention merged them -- an authority could not be reported at NUTS level 1 '
        'or 2 at all. Any second, hand-seeded copy under an invented urn:raven: URI is '
        'collapsed onto the published concept, repointing referrers first')
on conflict (version) do nothing;

commit;
