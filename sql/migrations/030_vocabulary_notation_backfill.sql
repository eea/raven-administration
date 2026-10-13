-- ===========================================================================
-- 030 — fill an empty eea_*.notation from the id, on databases that never got it
--
-- Every AQR3 CSV reads eea_*.notation, so a codelist row without a notation
-- exports as a blank column even though the row is there and referenced. The
-- screens hide it: they read COALESCE(NULLIF(notation, ''), label) and show the
-- label instead.
--
-- Found on raven_local (a v3 clone migrated to v4): eea_zonetypes held agg and
-- noagg with notation '', so AssessmentRegimeZone.csv had an empty ZoneType for
-- every regime while the Zones page showed "Agglomeration". agg and noagg are the
-- aq/zonetype codes AQR3 expects, which is the id.
--
-- A fresh install already gets this from the backfill at the end of sql/data.sql,
-- and populate_vocabularies.py always writes a notation. A migrated database
-- whose vocabularies were never refreshed got neither, and data.sql's backfill
-- was not in any migration. This is that backfill, with one restriction:
--
-- Tables keyed on a number are left alone. Their id is a URI's numeric segment,
-- not a code. For eea_pollutants that is the defect migration 015 fixed, where
-- meteo parameters exported as '51' instead of "Wind velocity", and filling a
-- notation from the id would bring it back. A blank there is left for
-- populate_vocabularies.py to fill properly.
--
-- Idempotent: only rows with a NULL or empty notation are touched.
-- ===========================================================================

begin;

do $$
declare
    t text;
    n integer;
begin
    for t in
        select c.table_name
        from information_schema.columns c
        join information_schema.columns i
          on i.table_schema = c.table_schema
         and i.table_name   = c.table_name
         and i.column_name  = 'id'
        where c.table_schema = 'public'
          and c.table_name like 'eea\_%'
          and c.column_name = 'notation'
          and i.data_type in ('character varying', 'text')
        order by c.table_name
    loop
        execute format(
            'update %I set notation = id where notation is null or notation = %L', t, '');
        get diagnostics n = row_count;
        if n > 0 then
            raise notice 'notation backfilled from id: % (% rows)', t, n;
        end if;
    end loop;
end
$$;

insert into schema_version (version, description)
values ('4.502.30', 'empty eea_*.notation filled from the (text) id on migrated databases, '
                    'as sql/data.sql does on a fresh install -- eea_zonetypes exported a '
                    'blank AssessmentRegimeZone ZoneType')
on conflict (version) do nothing;

commit;
