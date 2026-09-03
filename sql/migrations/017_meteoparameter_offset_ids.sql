-- ===========================================================================
-- 017 — aq/meteoparameter pollutants move off the NILU 999900 offset
--
-- sql/meteo.sql used to seed the 21 EEA meteoparameter concepts under
-- `id = 999900 + N`, a NILU offset standing for meteoparameter N. The convention
-- for eea_pollutants is id = int(the URI's last segment) -- `numeric_uri_suffix`
-- in sql/vocabularies.py -- because aq/pollutant and aq/meteoparameter
-- deliberately share one id space. So a database that followed the documented
-- install order holds 21 rows keyed by an id EEA has never issued, for concepts
-- whose URI is nevertheless correct.
--
-- The rule, recorded in migration 012, is that eea_* tables contain the EEA
-- vocabulary and nothing else. meteo.sql is fixed in the same commit as this
-- migration, so a fresh install no longer takes the defect, and this moves the
-- databases that already did.
--
-- Two cases per offset row, decided by whether the real id is already present
-- (it is on any database where sql/populate_vocabularies.py has run):
--
--   * present -> the offset row is a second copy of the same concept. Every
--                referrer is repointed to the real id and the offset row deleted.
--   * absent  -> the offset row IS the concept, just under the wrong key, and its
--                `uri` already says so. It is rekeyed in place, which every
--                foreign key follows: all of them are ON UPDATE CASCADE.
--
-- Unlike nilu-private-migration/cleanup_invented_vocabulary.py, which handled the
-- first case only and refused to run until the vocabulary had been loaded, this
-- needs no precondition -- the second case creates the missing row rather than
-- leaving those components with no EEA identity.
--
-- WHY THE DELETE IS GUARDED. sampling_points.pollutant_id, aqi.pollutant_id,
-- directives.pollutant_id and three more reference eea_pollutants ON DELETE
-- CASCADE, and sampling_points cascades on to observations. Deleting an offset row
-- that anything still referenced would take 513 wind-velocity series and their
-- observations with it, silently. So: repoint, re-count, raise if anything is
-- left, only then delete. Referrers come from pg_constraint for the same reason as
-- in migration 016 -- a hardcoded list goes stale as foreign keys are added.
--
-- Idempotent, and a no-op on a database that never ran the old meteo.sql.
-- ===========================================================================

begin;

do $$
declare
    NILU_METEO_OFFSET constant integer := 999900;
    row_        record;
    ref         record;
    real_id     integer;
    suffix      text;
    remaining   bigint;
    updated     bigint;
    repointed   int    := 0;
    rekeyed     int    := 0;
    moved       bigint := 0;
begin
    for row_ in
        select id, uri from eea_pollutants
         where id >= NILU_METEO_OFFSET
         order by id
    loop
        -- Derived from the URI rather than from `id - 999900`, and then checked
        -- against it. The URI is the concept's identity; the arithmetic is only a
        -- NILU convention, and if the two disagree the row is something else
        -- entirely and must not be folded into a real vocabulary term.
        suffix := regexp_replace(coalesce(row_.uri, ''), '^.*/', '');
        if suffix !~ '^[0-9]+$' then
            -- raise takes % only; %L is format()'s and would print a stray L.
            raise exception
                '017: eea_pollutants row % has uri "%", whose last segment is not a '
                'number, so the aq/meteoparameter concept it stands for cannot be '
                'determined. Investigate before re-running.', row_.id, row_.uri;
        end if;
        real_id := suffix::integer;
        if row_.id <> NILU_METEO_OFFSET + real_id then
            raise exception
                '017: eea_pollutants row % points at meteoparameter %, but % + % is '
                '%. The row does not follow the NILU offset convention, so this '
                'migration will not touch it.',
                row_.id, real_id, NILU_METEO_OFFSET, real_id,
                NILU_METEO_OFFSET + real_id;
        end if;

        if not exists (select 1 from eea_pollutants p where p.id = real_id) then
            -- The concept exists only under the wrong key. Rekey in place; ON UPDATE
            -- CASCADE carries every referrer across, and `uri` is already right.
            update eea_pollutants set id = real_id where id = row_.id;
            rekeyed := rekeyed + 1;
            raise notice '017: pollutant % rekeyed to % (no real row existed)',
                row_.id, real_id;
            continue;
        end if;

        for ref in
            select rel.relname::text as child, att.attname::text as col
              from pg_constraint con
              join pg_class rel    on rel.oid  = con.conrelid
              join pg_class frel   on frel.oid = con.confrelid
              join pg_namespace fn on fn.oid   = frel.relnamespace
              join pg_attribute att on att.attrelid = rel.oid
                                   and att.attnum = con.conkey[1]
             where con.contype = 'f'
               and fn.nspname = 'public'
               and frel.relname = 'eea_pollutants'
               and array_length(con.conkey, 1) = 1
             order by rel.relname, att.attname
        loop
            execute format('update %I set %I = $1 where %I = $2',
                           ref.child, ref.col, ref.col)
                using real_id, row_.id;
            get diagnostics updated = row_count;
            if updated > 0 then
                raise notice '017: %.% -- % row(s) moved from pollutant % to %',
                    ref.child, ref.col, updated, row_.id, real_id;
            end if;
            moved := moved + updated;
        end loop;

        -- Re-counted in a second pass, so a foreign key visited earlier cannot be
        -- re-populated by one visited later, and so a referrer this migration does
        -- not expect stops the run instead of being cascaded away.
        for ref in
            select rel.relname::text as child, att.attname::text as col
              from pg_constraint con
              join pg_class rel    on rel.oid  = con.conrelid
              join pg_class frel   on frel.oid = con.confrelid
              join pg_namespace fn on fn.oid   = frel.relnamespace
              join pg_attribute att on att.attrelid = rel.oid
                                   and att.attnum = con.conkey[1]
             where con.contype = 'f'
               and fn.nspname = 'public'
               and frel.relname = 'eea_pollutants'
               and array_length(con.conkey, 1) = 1
        loop
            execute format('select count(*) from %I where %I = $1',
                           ref.child, ref.col)
                into remaining using row_.id;
            if remaining > 0 then
                raise exception
                    '017: eea_pollutants row % still has % reference(s) from %.% '
                    'after repointing to %. Refusing to delete it -- that foreign '
                    'key may cascade to the observations.',
                    row_.id, remaining, ref.child, ref.col, real_id;
            end if;
        end loop;

        delete from eea_pollutants where id = row_.id;
        repointed := repointed + 1;
    end loop;

    raise notice '017: % offset row(s) collapsed onto the real id, % rekeyed, '
                 '% reference(s) repointed', repointed, rekeyed, moved;

    -- The two branches above are exhaustive, so this can be absolute.
    select count(*) into remaining
      from eea_pollutants where id >= NILU_METEO_OFFSET;
    if remaining > 0 then
        raise exception '017: % eea_pollutants row(s) remain at or above the NILU '
                        'offset.', remaining;
    end if;
end $$;

insert into schema_version (version, description)
values ('4.502.17',
        'aq/meteoparameter pollutants move off the NILU 999900 offset onto id = int(the '
        'URI last segment), the convention aq/pollutant already follows. sql/meteo.sql '
        'seeded 21 rows under keys EEA never issued; they are now either collapsed onto '
        'the real id (repointing every referrer first, since several cascade on delete) '
        'or rekeyed in place where the real row was absent')
on conflict (version) do nothing;

commit;
