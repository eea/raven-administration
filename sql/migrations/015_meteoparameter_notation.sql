-- ===========================================================================
-- 015 — meteo parameter notation: store the label, not the URI suffix
--
-- Every pollutant display in Raven reads COALESCE(NULLIF(notation, ''), label).
-- That idiom exists so a vocabulary which supplies no notation falls through to
-- its label. EEA's aq/meteoparameter vocabulary is exactly such a vocabulary:
-- it ships an empty skos:notation for every concept but 51.
--
-- populate_vocabularies.py could not know that. Its parser falls back to the
-- URI's last segment whenever skos:notation is absent — the right answer for
-- most vocabularies, but here that segment is a bare number. So eea_pollutants
-- ended up holding notation = '51', '52', '54' ... which then *wins* the
-- COALESCE, and the label ("Wind velocity") is never reached.
--
-- Measured on the AirQUIS production database, 1,542 sampling points render as
-- an integer instead of a name:
--
--     51  Wind velocity        513      53  Pressure                     56
--     52  Wind direction       380      63  Wind component vertical       5
--     54  Temperature          339      74  Global radiation              5
--     58  Relative humidity    181
--     60  Precipitation         63
--
-- and they do so in every view that names a pollutant: Sampling Points, Verify,
-- Dashboard, Map, Latest data, Notifications, AQI, Scale.
--
-- The label is stored as the notation rather than the notation being blanked,
-- because roughly a dozen queries read eea_pollutants.notation *bare* rather
-- than through the COALESCE — and one of them (core/data/statistics.py) filters
-- on it. Blanking would turn a useless number into a useless blank there; the
-- label fixes every reader at once. This is also what the retired sql/meteo.sql
-- did for these same concepts.
--
-- The loader is fixed in the same commit (Vocabulary.notation_from='label'),
-- otherwise the next vocabulary refresh would write the numbers straight back.
-- ===========================================================================

begin;

-- Matched on uri, which is the only reliable discriminator: meteo parameters
-- deliberately share eea_pollutants' id space with aq/pollutant, so there is no
-- id range to test. Stored URIs are http:, not https: — they come from the RDF's
-- rdf:about — hence the leading wildcard rather than an equality on DD_BASE.
--
-- The numeric-notation predicate makes this idempotent and keeps it off any row
-- that already carries a real name.
update eea_pollutants
   set notation = label
 where uri like '%/aq/meteoparameter/%'
   and notation ~ '^[0-9]+$';

insert into schema_version (version, description)
values ('4.502.15',
        'eea_pollutants.notation for aq/meteoparameter concepts now holds the label rather '
        'than the numeric URI suffix. EEA ships no skos:notation for that vocabulary, so the '
        'loader synthesised one from the URI, and a synthesised notation wins the '
        'COALESCE(NULLIF(notation,''''), label) that every pollutant display uses — 1,542 '
        'sampling points read as "51" instead of "Wind velocity"')
on conflict (version) do nothing;

commit;
