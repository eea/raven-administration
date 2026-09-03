-- ===========================================================================
-- 016 — one id convention for the eea_* vocabulary tables
--
-- The convention is stated in sql/data.sql: `id` holds the short EEA code and
-- `uri` holds the full http://dd.eionet.europa.eu/vocabulary/... URI. It is what
-- populate_vocabularies.py produces (derive_id, sql/populate_vocabularies.py) and
-- what data.sql seeds. Databases migrated in place from v3 carry the older
-- spelling as well: the retired loader raven-rn3-db/populate_lookups_v4.py used
-- `'id': uri` and left `uri` NULL, so the same concept exists twice — once keyed
-- 'UTC', once keyed '.../aq/timezone/UTC'. sql/statistics.sql still seeds all 93
-- aggregation processes that way (fixed in the same commit as this migration).
--
-- Measured on the AirQUIS production database: 486 rows across 15 tables.
--
--   366  a canonical short twin already exists           -> step 1, collapse
--    10  eea_concentrations rows from uom/meteo, a
--        vocabulary that is not the one the column
--        reports (AQR3 uses uom/concentration)           -> step 2, delete
--   110  the only copy of their concept                  -> step 3, rekey
--
-- Two spellings for one concept is not merely untidy. It makes the AirQUIS
-- migration's alias index (migrate_master_data.py:vocab_aliases) ambiguous —
-- 'rural' resolves to whichever row PostgreSQL returns first, so a station's
-- area classification could be stored as a URL. And core/data/processing/
-- common.py parses eea_timezones.id by string surgery: it happens to read
-- '.../timezone/UTC+01' correctly because the URI ends in '+01', and raises
-- ValueError on '.../timezone/UTC', where there is no '-' to split on.
--
-- WHY EVERY DELETE IS GUARDED. networks.aggregation_timezone references
-- eea_timezones ON DELETE CASCADE, and stations.network_id -> networks and
-- sampling_points.station_id -> stations are ON DELETE CASCADE too. A bare
-- `delete from eea_timezones where id like 'http%'` therefore removes 32
-- networks, 714 stations, 3580 sampling points and ~6.9M observations without
-- an error. So: repoint every referrer, re-count, raise if anything is left,
-- and only then delete. Same discipline as
-- nilu-private-migration/cleanup_invented_vocabulary.py, generalised.
--
-- Referrers are discovered from pg_constraint rather than listed here. A
-- hardcoded list goes stale as foreign keys are added, and the two columns most
-- likely to be forgotten (settings.timezone_id, networks.aggregation_timezone)
-- are exactly the ones the existing private-script list misses. All 62 foreign
-- keys into eea_* are ON UPDATE CASCADE, which is what lets step 3 rekey a row
-- in place and have every referrer follow.
--
-- URIs are detected with strpos(id, '://'), never LIKE 'http%': inside
-- format() a literal % must be doubled, and one missed %% is a silent
-- mis-selection rather than an error. For the same reason every dynamic
-- statement passes its literals with USING instead of interpolating them.
--
-- Idempotent, and a no-op on a database that already uses short ids.
-- ===========================================================================

begin;

-- ---------------------------------------------------------------------------
-- Step 1 — collapse a URI-keyed row onto its canonical short twin.
--
-- Paired on `s.uri = u.id`, NOT on the URI's last path segment. The suffix looks
-- equivalent and is not: uom/meteo/mm and uom/concentration/mm both reduce to
-- 'mm', so a suffix match would fold one unit into a different concept that
-- merely shares a spelling. Comparing the canonical row's own uri to the
-- duplicate's id proves they are the same concept.
--
-- The direction rule (u is a URI, s is not) is load-bearing. On the AirQUIS
-- database eea_zonetypes is inverted — the URI-keyed row carries uri = 'agg'
-- while the short row carries the URI — so `s.uri = u.id` matches BOTH ways and
-- an undirected query would delete both rows of the pair.
-- ---------------------------------------------------------------------------
do $$
declare
    tbl       text;
    pair      record;
    ref       record;
    remaining bigint;
    updated   bigint;
    collapsed int    := 0;
    moved     bigint := 0;
begin
    for tbl in
        select c.relname::text
          from pg_class c
          join pg_namespace n on n.oid = c.relnamespace
         where n.nspname = 'public'
           and c.relkind = 'r'
           and c.relname like 'eea/_%' escape '/'
           and exists (select 1 from pg_attribute a
                        where a.attrelid = c.oid and a.attname = 'id'
                          and a.attnum > 0 and not a.attisdropped
                          and a.atttypid in ('text'::regtype, 'varchar'::regtype))
           and exists (select 1 from pg_attribute a
                        where a.attrelid = c.oid and a.attname = 'uri'
                          and a.attnum > 0 and not a.attisdropped)
         order by c.relname
    loop
        for pair in execute format(
                'select u.id as uri_id, s.id as short_id'
                '  from %I u'
                '  join %I s on s.uri = u.id and s.id <> u.id'
                ' where strpos(u.id, $1) > 0 and strpos(s.id, $1) = 0'
                ' order by u.id', tbl, tbl)
            using '://'
        loop
            -- Repoint first.
            for ref in
                select rel.relname::text as child, att.attname::text as col
                  from pg_constraint con
                  join pg_class rel   on rel.oid  = con.conrelid
                  join pg_class frel  on frel.oid = con.confrelid
                  join pg_namespace fn on fn.oid  = frel.relnamespace
                  join pg_attribute att on att.attrelid = rel.oid
                                       and att.attnum = con.conkey[1]
                 where con.contype = 'f'
                   and fn.nspname = 'public'
                   and frel.relname = tbl
                   and array_length(con.conkey, 1) = 1
                 order by rel.relname, att.attname
            loop
                execute format('update %I set %I = $1 where %I = $2',
                               ref.child, ref.col, ref.col)
                    using pair.short_id, pair.uri_id;
                get diagnostics updated = row_count;
                moved := moved + updated;
            end loop;

            -- Then re-count, in a second pass so a foreign key visited earlier
            -- cannot be re-populated by one visited later. Trusting the UPDATEs
            -- above is not enough: a referrer this migration does not expect
            -- must stop the run, not be cascaded away.
            for ref in
                select rel.relname::text as child, att.attname::text as col
                  from pg_constraint con
                  join pg_class rel   on rel.oid  = con.conrelid
                  join pg_class frel  on frel.oid = con.confrelid
                  join pg_namespace fn on fn.oid  = frel.relnamespace
                  join pg_attribute att on att.attrelid = rel.oid
                                       and att.attnum = con.conkey[1]
                 where con.contype = 'f'
                   and fn.nspname = 'public'
                   and frel.relname = tbl
                   and array_length(con.conkey, 1) = 1
            loop
                execute format('select count(*) from %I where %I = $1',
                               ref.child, ref.col)
                    into remaining using pair.uri_id;
                if remaining > 0 then
                    raise exception
                        '016: % row % still has % reference(s) from %.% after '
                        'repointing to %. Refusing to delete it — the foreign key '
                        'may cascade.',
                        tbl, pair.uri_id, remaining, ref.child, ref.col,
                        pair.short_id;
                end if;
            end loop;

            execute format('delete from %I where id = $1', tbl) using pair.uri_id;
            collapsed := collapsed + 1;
        end loop;
    end loop;

    raise notice '016 step 1: collapsed % URI-keyed duplicate row(s), repointed % reference(s)',
        collapsed, moved;
end $$;

-- ---------------------------------------------------------------------------
-- Step 2 — drop the uom/meteo rows from eea_concentrations.
--
-- sql/meteo_concentration.sql seeded ten units from uom/meteo. eea_concentrations
-- reports uom/concentration (AQR3 OMR_11), so these are the wrong vocabulary in
-- the right table — the same violation cleanup_invented_vocabulary.py already
-- removed from eea_times for uom/time. They also cannot be rekeyed: uom/meteo/mm
-- would want the id 'mm', which the real uom/concentration millimetre owns.
--
-- Non-concentration units are not lost. Since core migration 012 a series with
-- no vocabulary unit carries unit_id = NULL and the true unit as text in
-- plugin_sp_extended.unit, which raven-sp-extended >= 1.3.0 feeds back into
-- core's queries through the series metadata registry.
--
-- Runs before the rekey so the 'mm' collision is gone rather than skipped, which
-- is what lets step 5 assert absolutely.
-- ---------------------------------------------------------------------------
do $$
declare
    ref     record;
    n       bigint;
    victims text[];
begin
    select array_agg(id order by id) into victims
      from eea_concentrations
     where strpos(id, '/uom/meteo/') > 0;

    if victims is null then
        raise notice '016 step 2: no uom/meteo rows in eea_concentrations';
        return;
    end if;

    for ref in
        select rel.relname::text as child, att.attname::text as col
          from pg_constraint con
          join pg_class rel   on rel.oid  = con.conrelid
          join pg_class frel  on frel.oid = con.confrelid
          join pg_namespace fn on fn.oid  = frel.relnamespace
          join pg_attribute att on att.attrelid = rel.oid
                               and att.attnum = con.conkey[1]
         where con.contype = 'f'
           and fn.nspname = 'public'
           and frel.relname = 'eea_concentrations'
           and array_length(con.conkey, 1) = 1
         order by rel.relname, att.attname
    loop
        execute format('select count(*) from %I where %I = any($1)',
                       ref.child, ref.col)
            into n using victims;
        if n > 0 then
            raise exception
                '016: % uom/meteo unit(s) are still referenced by %.%. Move those '
                'series onto a uom/concentration term, or onto '
                'plugin_sp_extended.unit with unit_id = NULL, before re-running.',
                n, ref.child, ref.col;
        end if;
    end loop;

    delete from eea_concentrations where id = any(victims);
    raise notice '016 step 2: deleted % uom/meteo row(s) from eea_concentrations',
        array_length(victims, 1);
end $$;

-- ---------------------------------------------------------------------------
-- Step 3 — rekey the rows that are the only copy of their concept.
--
-- No twin to collapse onto, so the row itself moves to the short id and keeps
-- the URI in `uri`. Every foreign key into eea_* is ON UPDATE CASCADE, so
-- referrers follow without being touched here — including the 77 statistics
-- rows and the 32 networks.media_monitored values.
--
-- The short id is the URI's last path segment. That is the id convention for
-- eea_concentrations and eea_datatable (vocabularies.py id_from='uri_suffix'),
-- and for the tables reached here it agrees with the notation convention too:
-- notation equals the last segment for all 93 aggregation processes, and the
-- segment is what data.sql seeds for the four INSPIRE codelists.
--
-- Three guards, all in the WHERE clause: something to strip, no twin (step 1
-- owns those), and the target id free. Two rows deriving the same new id inside
-- one statement would slip past the last guard — the subquery sees the
-- pre-statement snapshot — and then fail the primary key, which aborts the
-- migration rather than corrupting anything.
-- ---------------------------------------------------------------------------
do $$
declare
    tbl     text;
    rekeyed bigint := 0;
    n       bigint;
begin
    for tbl in
        select c.relname::text
          from pg_class c
          join pg_namespace n on n.oid = c.relnamespace
         where n.nspname = 'public'
           and c.relkind = 'r'
           and c.relname like 'eea/_%' escape '/'
           and exists (select 1 from pg_attribute a
                        where a.attrelid = c.oid and a.attname = 'id'
                          and a.attnum > 0 and not a.attisdropped
                          and a.atttypid in ('text'::regtype, 'varchar'::regtype))
           and exists (select 1 from pg_attribute a
                        where a.attrelid = c.oid and a.attname = 'uri'
                          and a.attnum > 0 and not a.attisdropped)
         order by c.relname
    loop
        execute format(
                'update %I t'
                '   set uri = coalesce(t.uri, t.id),'
                '       id  = regexp_replace(t.id, $1, $2)'
                ' where strpos(t.id, $3) > 0'
                '   and regexp_replace(t.id, $1, $2) <> $2'
                '   and not exists (select 1 from %I s'
                '                    where s.uri = t.id and s.id <> t.id)'
                '   and not exists (select 1 from %I o'
                '                    where o.id = regexp_replace(t.id, $1, $2))',
                tbl, tbl, tbl)
            using '^.*/', '', '://';
        get diagnostics n = row_count;
        if n > 0 then
            raise notice '016 step 3: % — % row(s) rekeyed to the URI''s last segment',
                tbl, n;
            rekeyed := rekeyed + n;
        end if;
    end loop;

    raise notice '016 step 3: rekeyed % row(s) in total', rekeyed;
end $$;

-- ---------------------------------------------------------------------------
-- Step 4 — networks.media_monitored's column default.
--
-- The only column default in the schema holding a vocabulary URI. ON UPDATE
-- CASCADE moved the stored values in step 3 but a default is not a reference, so
-- it now names an id that no longer exists and the next INSERT that omits the
-- column would fail the foreign key. migrate_master_data.py relies on exactly
-- that default (required_legacy() skips a NOT NULL column that has one), so this
-- is what keeps the AirQUIS migration working.
--
-- The replacement is looked up through the old default's own URI rather than
-- hardcoded, so this stays correct whether the row was rekeyed or collapsed.
-- networks is a v3 leftover shape: the column does not exist on a database built
-- from schema.sql, hence the guard.
-- ---------------------------------------------------------------------------
do $$
declare
    current_default text;
    old_uri         text;
    new_default     text;
begin
    select column_default into current_default
      from information_schema.columns
     where table_schema = 'public'
       and table_name = 'networks'
       and column_name = 'media_monitored';

    if current_default is null or strpos(current_default, '://') = 0 then
        return;
    end if;

    -- column_default reads as '<literal>'::character varying. Split on '::',
    -- which cannot appear inside the URI ('http://' is ':' then '//').
    old_uri := btrim(split_part(current_default, '::', 1), '''');

    select m.id into new_default from eea_mediavalues m where m.uri = old_uri;
    if new_default is null then
        raise exception
            '016: networks.media_monitored defaults to %, but no eea_mediavalues '
            'row carries that uri, so the default cannot be retargeted. Load the '
            'vocabulary (sql/populate_vocabularies.py) and re-run.', old_uri;
    end if;

    execute format('alter table networks alter column media_monitored set default %L',
                   new_default);
    raise notice '016 step 4: networks.media_monitored default % -> %',
        old_uri, new_default;
end $$;

-- ---------------------------------------------------------------------------
-- Step 5 — assert. The three steps above account for every URI-keyed row, so
-- this is absolute rather than a spot check. A survivor means a table shape this
-- migration did not anticipate; failing here leaves the transaction rolled back
-- and the database as it was.
--
-- Only `id` columns. eea_environmentalobjective.protection_target,
-- reporting_metric and assessment_threshold legitimately hold URIs — they are
-- joined to eea_*.uri, not to eea_*.id.
-- ---------------------------------------------------------------------------
do $$
declare
    tbl       text;
    n         bigint;
    offenders text := '';
begin
    for tbl in
        select c.relname::text
          from pg_class c
          join pg_namespace n on n.oid = c.relnamespace
         where n.nspname = 'public'
           and c.relkind = 'r'
           and c.relname like 'eea/_%' escape '/'
           and exists (select 1 from pg_attribute a
                        where a.attrelid = c.oid and a.attname = 'id'
                          and a.attnum > 0 and not a.attisdropped
                          and a.atttypid in ('text'::regtype, 'varchar'::regtype))
         order by c.relname
    loop
        execute format('select count(*) from %I where strpos(id, $1) > 0', tbl)
            into n using '://';
        if n > 0 then
            offenders := offenders || format('%s (%s rows), ', tbl, n);
        end if;
    end loop;

    if offenders <> '' then
        raise exception
            '016: URI-keyed ids survive in %. Each is either a duplicate whose '
            'canonical twin is missing (load the vocabulary with '
            'sql/populate_vocabularies.py) or a row whose short id is already '
            'taken by a different concept.', rtrim(offenders, ', ');
    end if;

    raise notice '016 step 5: no eea_* id contains a URI';
end $$;

insert into schema_version (version, description)
values ('4.502.16',
        'One id convention for the eea_* vocabulary tables: id is the short EEA code and uri '
        'the full URI. Databases migrated in place from v3 carried a second, URI-keyed copy of '
        '486 concepts across 15 tables (366 collapsed onto their short twin, 110 rekeyed, and '
        '10 uom/meteo rows dropped from eea_concentrations, which reports uom/concentration). '
        'Two spellings made the AirQUIS migration''s alias index ambiguous and left '
        'settings.timezone_id parsed by luck')
on conflict (version) do nothing;

commit;
