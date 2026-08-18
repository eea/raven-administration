# Archived migrations (001–010)

Every DDL effect of these files is in `sql/schema.sql` — verified individually across
columns, indexes, named constraints, partition ranges and triggers. They were folded in at
schema version `4.502.11` and moved here so a fresh install runs one statement instead of
ten idempotent no-ops that re-ran renames against a schema which already had the new names.

**`sql/apply_migrations.py` cannot see this directory.** `migration_files()`
(`apply_migrations.py:34-43`) is a NON-recursive `glob('*.sql')`. That is deliberate and
load-bearing: making it recursive would resurrect all ten migrations against every database.
`tests/unit/test_migration_layout.py` asserts it returns exactly one file.

## Why these are kept rather than deleted

- **`tests/integration/test_schema_migration_parity.py` replays them** to prove `schema.sql`
  still embodies them. Every one was written to be idempotent, so a no-op is the expected
  outcome and any resulting diff is a real gap in `schema.sql`. That is the only automated
  check that the fold-in has not rotted, and there is no pre-001 baseline schema in the repo
  to construct a "migrations-built" database from any other way.
- **`002_aqr3_v502_renames.sql` is the only executable record of the v3 → v5.02 column-name
  map** — `stations.eoi_code → station_eoi_code` and 30 more. Any AirQUIS-era database still
  needs it, and it is the reference used to fix `sql/raven4_migrate/migrate_v3_to_v4.py`.
- **`sql/migrations/011_migration_baseline.sql` points here.** Its fold-in guard refuses to
  apply itself to a database that predates the fold-in and names this directory in the error.

## Applying them by hand

Only needed when 011's guard tells you to. They are idempotent, so running all ten against a
database that is only partly behind is safe.

```bash
for f in sql/migrations/archive/0*.sql; do psql "$DB_URI" -f "$f"; done
```

```powershell
Get-ChildItem sql/migrations/archive/0*.sql |
    ForEach-Object { psql $env:DB_URI -f $_.FullName }
```

Then re-run `python sql/apply_migrations.py`.

## Data remediation that was NOT folded in

Three of these carried DML that `schema.sql` cannot express, because it depends on rows
rather than structure. It now lives in `sql/raven4_migrate/migrate_v3_to_v4.py`
(`remediate_legacy_data()`, runnable on its own with `--remediate-only`):

| Archived | What moved |
|---|---|
| `002` | `observations.data_capture` from `meta->>'instrument_validity'`, with `raven_observations_set_timestamp_trigger` suspended so the update does not overwrite `touched` (the exported AQR3 ResultTime) |
| `003` | `pollution_level_adjustment` from `exceedancedescriptions.adjustment_source` |
| `004` | snap `srs_inline` to the EPSG:3035 INSPIRE grid, then de-duplicate |

`004`'s column *retypes* did **not** move. They only apply to a database whose `srs_inline`
descends from the NILU-only `sr_area_inline`, and 011's guard rejects such a database anyway
— run `004` from here for those.

`006` and `008` moved nothing. `006` brings `settings` forward from the v3 shape, which
`schema.sql` already declares (`country_code_id`, `timezone_id`), and its country backfill
survives as the `eea_countries` lookup in `migrate_v3_to_v4.migrate_settings()`. `008`
renames `assessmentregime_id → assessment_regime_id`, which a database built from
`schema.sql` never had.

## Version history

| Version | File |
|---|---|
| `4.502.1` | `001_aqr3_v502_sampling_point.sql` |
| `4.502.2` | `002_aqr3_v502_renames.sql` |
| `4.502.3` | `003_aqr3_v502_new_tables.sql` |
| `4.502.4` | `004_aqr3_v502_snap_srs_grid.sql` |
| `4.502.5` | `005_daily_check_log.sql` |
| `4.502.6` | `006_settings_v4_shape.sql` |
| `4.502.7` | `007_timezone_offset_generated.sql` |
| `4.502.8` | `008_assessment_regime_id_rename.sql` |
| `4.502.9` | `009_documents_attachment.sql` |
| `4.502.10` | `010_documents_original_url.sql` |

Databases migrated before the fold-in hold all eleven rows in `schema_version`; a database
created from `schema.sql` afterwards holds only `4.502.11`. Both read as up to date, because
every consumer derives what it expects from the files actually present.
