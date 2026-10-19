-- ===========================================================================
-- 031 — eea_environmentalobjective can hold the AAQD 2024/2881 recast vocabulary
--
-- populate_vocabularies.py prefers aq/environmentalobjective2024recast, because
-- AQR3 v5.02 is the recast. The table could not hold a single row of it:
--
--   * id was integer, but recast concepts are named, not numbered. The URI ends
--     in 0001_ALT_H_3hAbove_2026 where the original vocabulary ended in 1. The
--     loader rejected all 68 recast concepts. Their fetch had still succeeded,
--     so the original vocabulary was never tried, and the table stayed empty on
--     every database built by schema.sql or the migrate wizard. Generate regimes
--     then offered nothing.
--   * notation was varchar(10), and a recast notation is that same 23-character
--     name.
--   * assessment_threshold and exceedance_metric hold every value of a
--     multi-valued CSV column, comma-joined. Three or four assessment threshold
--     URIs are longer than 255 characters.
--
-- Nothing references eea_environmentalobjective by foreign key. Generate regimes
-- reads it, and assessmentregime_zones (dropped by 020) used to. Existing integer
-- ids become their text form ('1'..'165'); re-running populate_vocabularies.py
-- replaces them with the recast rows.
--
-- Idempotent: altering a column to the type it already has is a no-op.
-- ===========================================================================

begin;

alter table eea_environmentalobjective
    alter column id                   type varchar(100) using id::text,
    alter column notation             type varchar(100),
    alter column exceedance_metric    type text,
    alter column assessment_threshold type text;

insert into schema_version (version, description)
values ('4.502.31', 'eea_environmentalobjective.id is text, so the 2024/2881 recast '
                    'vocabulary (named, not numbered, concepts) can be loaded')
on conflict (version) do nothing;

commit;
