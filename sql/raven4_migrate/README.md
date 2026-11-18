# Migrating a Raven v3 database to Raven v4

`migrate_v3_to_v4.py` copies a Raven v3 database (`ravendb`) into a new, empty Raven v4
database. It builds the v4 structure from `sql/schema.sql`, loads the EEA code lists,
copies and converts the data, and seeds the defaults v3 did not have. **The v3 database
is only read, never changed.**

Use this instead of the "Setup the database" steps in the main README. Those are for a
fresh install, and some of them must not be run on a migrated database (see
[After the migration](#after-the-migration)).

## What you need

- **Python 3.10+** with `pip install psycopg2-binary python-dotenv`
- **The v3 database** connection details. A read-only user is enough.
- **An empty PostgreSQL database for v4** with PostGIS enabled:
  ```sql
  CREATE DATABASE ravendb4;
  -- connected to ravendb4:
  CREATE EXTENSION postgis;
  ```
- **Internet access to `dd.eionet.europa.eu`.** The EEA code lists are fetched from
  there. Without it the script falls back to a smaller built-in set and says so.

## Configure

In this folder, copy `.env.example` to `.env` and fill in both databases:

```
SOURCE_DB_HOST=...      # Raven v3
SOURCE_DB_PORT=5432
SOURCE_DB_NAME=ravendb
SOURCE_DB_USER=...
SOURCE_DB_PASSWORD=...

TARGET_DB_HOST=...      # the new, empty v4 database
TARGET_DB_PORT=5432
TARGET_DB_NAME=ravendb4
TARGET_DB_USER=...
TARGET_DB_PASSWORD=...
```

`.env` is ignored by git; never commit it.

## Run

```bash
cd sql/raven4_migrate
python migrate_v3_to_v4.py --dry-run     # rehearsal: everything, then rolled back
python migrate_v3_to_v4.py               # the real run
```

The script does everything itself: the schema, the EEA code lists, and the data. Options:

| Option | When |
|--------|------|
| `--country-code XX` | v3 has no `settings.country_code` and the station EoI codes do not agree on one country |
| `--recreate-schema` | start over: **drops every table in the v4 database** and rebuilds it |
| `--batch-size N` | observations are copied N rows at a time (default 10000) |
| `--init-only` | only build an empty v4 database (schema + code lists); no v3 needed |

The data is copied in **one transaction**: if anything fails, nothing is written, and you
can fix the cause and run it again. The schema and the code lists are committed before
that, and a second run reuses them.

The code-list loader reports some lists as still empty. That is expected: several have no
EEA source or belong to Plans and Programmes, and the migration does not use them. The
script checks the twelve lists it does need and stops with a clear message only if one of
those is missing.

### Running it again

A re-run clears and re-copies the migrated tables. That includes **attainments,
exceedance descriptions and exceeding methods**, and the AQI bands, so anything entered
in those in v4 since the last run is replaced by the v3 contents. Take a dump first if
the v4 database has been worked on.

## After the migration

1. **Do not run** the fresh-install scripts from the main README (`data.sql`,
   `aqi.sql`, `meteo.sql`, `notifications.sql`, `statistics.sql`, ...) against the
   migrated database. `schema.sql` and this script already cover them.
   *Exception:* if the script stopped because the EEA code lists could not be loaded,
   it tells you to run `psql -d ravendb4 -f sql/data.sql` and then run it again.
2. Point Raven's `DB_URI` at the new database and start it.
3. Open **Misc → Finish the upgrade**. It lists what is still missing before the
   database can be reported to Reportnet 3, and each item links to the page that fixes
   it. Work through it until it is empty.
4. Calculate compliance: **Dataflow → Recalculate compliance**, or the wand on
   Management → Compliance assessment method.

## What is not migrated

v3 has no data for several AQR3 v5.02 entities (sampling point location history,
modelling results, pollution level adjustments, document attachments, ...); they are
filled in through Raven afterwards. The full list, and how differences between v3
deployments are handled, is in the docstring at the top of `migrate_v3_to_v4.py`.

## Other scripts

- `analyze_v3.py` prints the v3 database's tables and row counts, to see what a
  migration will have to handle. It uses the same `.env`.
- `python migrate_v3_to_v4.py --remediate-only` derives the AQR3 columns an existing v4
  database can compute from its own data and changes nothing else. No v3 needed.
