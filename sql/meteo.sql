-- EEA aq/meteoparameter concepts, for an install that does not run
-- sql/populate_vocabularies.py. The rows produced here are identical to the ones that
-- loader writes, so the two compose in either order (`on conflict do nothing`).
--
-- These ids used to be `999900 + N` -- a NILU offset standing for meteoparameter N --
-- which made eea_pollutants hold 21 rows that are not in any EEA vocabulary, under keys
-- EEA has never issued. The convention for this table is id = int(the URI's last
-- segment) (`numeric_uri_suffix` in sql/vocabularies.py), the same as for aq/pollutant:
-- the two vocabularies deliberately share one id space. Migration
-- 017_meteoparameter_offset_ids.sql moves databases that took the old spelling.
--
-- notation = label on purpose. EEA ships an empty skos:notation for every one of these
-- concepts, and every pollutant display in Raven reads
-- COALESCE(NULLIF(notation, ''), label) -- so a synthesised notation (the bare number)
-- wins that COALESCE and 1,542 sampling points render as "51" instead of "Wind
-- velocity". See migration 015_meteoparameter_notation.sql and Vocabulary.notation_from.
--
-- id, notation and uri are all derived from the two columns below rather than repeated,
-- so they cannot drift apart.
insert into eea_pollutants (id, label, notation, uri)
select v.id, v.label, v.label as notation,
       'http://dd.eionet.europa.eu/vocabulary/aq/meteoparameter/' || v.id as uri
  from (values
          (51, 'Wind velocity'),
          (52, 'Wind direction'),
          (53, 'Pressure'),
          (54, 'Temperature'),
          (55, 'Absolute humidity'),
          (56, 'Mixing height'),
          (58, 'Relative humidity'),
          (59, 'Duration of sunlight'),
          (60, 'Precipitation'),
          (61, 'Wind component south-north'),
          (62, 'Wind component west-east'),
          (63, 'Wind component vertical'),
          (64, 'Volume of air'),
          (71, 'Direct solar IR radiation'),
          (72, 'Direct solar UV radiation'),
          (73, 'Direct solar radiation'),
          (74, 'Global radiation'),
          (75, 'Diffused radiation'),
          (76, 'Reflected radiation'),
          (77, 'Direct solar visible radiation'),
          (99, 'No meteo measured')
       ) as v(id, label)
-- Untargeted, so it absorbs a conflict on the id primary key AND on the unique uri.
-- Both matter: a database that already ran populate_vocabularies.py holds these ids, and
-- one that ran the old version of this file holds these URIs under 999900 + N.
on conflict do nothing;
