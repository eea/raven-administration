"""
RAVEN v3 to v4 Data Migration

This script migrates data from ravendb (v3) to ravendb4 (v4).

Key transformations:
1. Lookup table FK values: full URI → notation (e.g., 'http://...measurementtype/automatic' → 'automatic')
2. Pollutant references: uri → numeric id (e.g., 'http://.../pollutant/1' → 1)
3. samples table → merged into sampling_points
4. observing_capabilities → merged into processes
5. New columns get default values or NULL

Usage:
    python migrate_v3_to_v4.py [--dry-run] [--batch-size=10000]
    python migrate_v3_to_v4.py --init-only       # blank DB with schema + EEA lookups, no source DB
    python migrate_v3_to_v4.py --remediate-only  # derive AQR3 columns in an existing v4 DB

The migration runs in a single transaction - if any part fails, nothing is committed.

Schema source: sql/schema.sql, which since schema version 4.502.11 also embodies
migrations 001-010 (archived under sql/migrations/archive/). The DML those migrations
carried lives in remediate_legacy_data() below, because it depends on rows rather than
structure and so cannot live in schema.sql.

WHAT THIS DOES NOT MIGRATE, deliberately -- these are AQR3 v5.02 entities with no v3
source data, and they are filled through the admin UI after the migration:

    sampling_point_locations        SPL location history. The export falls back to
                                    sampling_points.from_time/to_time when absent.
    moe_result_external / srs_external / moe_result_inline / models
                                    MOE/MRI/MRE/SRE modelling results.
    pollution_level_adjustment      ADJ. Partly seeded by remediate_legacy_data() where
                                    exceedancedescriptions.adjustment_source exists.
    compliance_assessment_method    CAM. Derived by POST /api/dataflow/compliance/recalculate.
    documents.documentattachment    DOC_05 / DOC_06. Reportnet3 attachment filename and
    documents.document_original_url published URL; no v3 equivalent.

V3 DEPLOYMENTS DIFFER, and this script probes rather than assumes. v3 was deployed per
country over several years and the schemas drifted; the Andorra database has no
`directives` table at all and its `settings` predates country_code. Because the whole
migration is one transaction, a missing relation aborts everything at whatever point it
is reached, so:

    settings.country_code   probed; falls back to the common prefix of
                            stations.eoi_code, overridable with --country-code XX.
    settings.timezone_id    has no v3 column at all. Taken from the shared value of
                            networks.aggregation_timezone, because the AQR3 export
                            resolves its UTC offset from it -- left NULL, every datetime
                            in every exported table is emitted without an offset.
    directives / statistics / aqi
                            each probed; skipped with a warning when absent.
    sampling_points.from_time
                            falls back to begin_position, since it is AQR3 SPL_03
                            LocationBegin and part of SamplingPointLocation's unique key.
    responsible_authorities.is_responsible_reporter
                            probed; decides AUT_03 reporting vs assessment.

METEOPARAMETERS keep their pollutant_id -- aq/pollutant and aq/meteoparameter share one
id space (migration 017), so 51 is "Wind velocity" and the FK is valid -- but are given
report_to_eea = false, which is what that column exists for. They stay in Raven and out
of every AQR3 table.

KNOWN DEFECT, not introduced by the fold-in: clear_migration_tables() TRUNCATEs
exceedancedescriptions, attainments and exceedingmethods, but no migrate_* function
repopulates them -- nothing here reads those tables from v3. So re-running this script
against a database whose exceedance data was entered through the UI DESTROYS it, and
that is the source of AQR3 dataflow G. Take a dump first, or remove those three from
the list if the target already holds exceedance data.
"""

import os
import sys
import argparse
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Database connections
SOURCE_DB = {
    'host': os.getenv('SOURCE_DB_HOST', 'localhost'),
    'port': int(os.getenv('SOURCE_DB_PORT', '5432')),
    'database': os.getenv('SOURCE_DB_NAME', 'ravendb'),
    'user': os.getenv('SOURCE_DB_USER', 'ravendb'),
    'password': os.getenv('SOURCE_DB_PASSWORD')
}

TARGET_DB = {
    'host': os.getenv('TARGET_DB_HOST', 'localhost'),
    'port': int(os.getenv('TARGET_DB_PORT', '5432')),
    'database': os.getenv('TARGET_DB_NAME', 'ravendb4'),
    'user': os.getenv('TARGET_DB_USER', 'ravendb4'),
    'password': os.getenv('TARGET_DB_PASSWORD')
}


# log() writes ✓/⚠/❌, and on Windows a redirected stdout defaults to cp1252, which
# cannot encode them: piping this script's output made it die with UnicodeEncodeError
# mid-migration -- and then die a second time inside its own `except` handler, hiding
# the real error. Anything that captures this output hits that, including CI and any
# wrapper that subprocesses it.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass


def log(msg):
    """Print timestamped log message"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# Case mapping for values that differ between v3 URIs and v4 notations
# v3 URI suffix (lowercase) → v4 notation (camelCase)
CASE_MAPPINGS = {
    # measurementregime
    'continuousdatacollection': 'continuousDataCollection',
    'demanddriven': 'demandDriven',
    'onceoff': 'onceOff',
    'periodicdatacollection': 'periodicDataCollection',
    # media - already lowercase in v4
    # processtype - already lowercase in v4
    # resultnature - already lowercase in v4
}

# v3's aq/organisationallevel carried six terms; v4's replacement aq/administrativelevel
# carries three (local, national, regional). These are the retired ones, mapped to the
# nearest surviving level. `international` has no equivalent and is dropped to NULL --
# STA_05 is nullable, and inventing a level would misreport the network.
RETIRED_ADMINISTRATIVE_LEVELS = {
    'municipality': 'local',
    'localauthority': 'local',
    'international': None,
}

# Time unit mappings: v3 → v4
TIME_UNIT_MAPPINGS = {
    'variable': 'var',
    'other': 'var',  # Map 'other' to 'var' as closest match
}

# No concentration mappings needed - v4 now uses URI suffix as id (e.g., 'ug.m-3')
# The notation column stores the display format (e.g., 'µg/m3') for CSV exports


def extract_notation_from_uri(uri):
    """Extract notation (last part) from URI and apply case mapping
    
    Examples:
    - 'http://dd.eionet.europa.eu/vocabulary/aq/measurementtype/automatic' → 'automatic'
    - 'http://inspire.ec.europa.eu/codelist/measurementregimevalue/continuousdatacollection' → 'continuousDataCollection'
    """
    if not uri:
        return None
    notation = uri.rstrip('/').split('/')[-1]
    # Apply case mapping if needed
    return CASE_MAPPINGS.get(notation, notation)


def extract_concentration_from_uri(uri):
    """Extract concentration id (URI suffix) from URI
    
    v4 uses URI suffix as id (URL-safe format like 'ug.m-3')
    The notation column stores display format for CSV export
    
    Examples:
    - 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ug.m-3' → 'ug.m-3'
    - 'http://dd.eionet.europa.eu/vocabulary/uom/meteo/Cel' → 'Cel'
    """
    if not uri:
        return None
    # Just extract URI suffix - no mapping needed
    return uri.rstrip('/').split('/')[-1]


def extract_time_unit_from_uri(uri):
    """Extract time unit from URI with mapping for deprecated values
    
    Examples:
    - 'http://dd.eionet.europa.eu/vocabulary/aq/timeunit/hour' → 'hour'
    - 'http://dd.eionet.europa.eu/vocabulary/aq/timeunit/variable' → 'var'
    - 'http://dd.eionet.europa.eu/vocabulary/aq/timeunit/other' → 'var'
    """
    if not uri:
        return None
    notation = uri.rstrip('/').split('/')[-1]
    # Apply time unit mapping if needed
    return TIME_UNIT_MAPPINGS.get(notation, notation)


# Pollutant ID mappings: v3_id -> v4_id
# NOTE: Most pollutant IDs do NOT need mapping - they are distinct in the EEA vocabulary
# Different IDs represent different media (air+aerosol, precip, precip+dry_dep, PM10, etc.)
# Only add mappings here if the ID was truly deprecated/removed from the vocabulary
POLLUTANT_ID_MAPPINGS = {
    # Currently no mappings needed - all pollutant IDs are valid
}

# Meteoparameter IDs (55, 58) are free in the pollutant vocabulary, so no mapping needed
# They can be stored as-is alongside regular pollutant IDs
METEOPARAMETER_MAPPINGS = {
    # No mappings needed - IDs 55 and 58 are not used by pollutants
}


def extract_pollutant_id_from_uri(uri):
    """Extract numeric ID from pollutant URI with mapping for deprecated IDs
    
    Example: 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1' → 1
             'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5610' → 5609 (mapped)
             'http://dd.eionet.europa.eu/vocabulary/aq/meteoparameter/55' → -55 (meteo)
    """
    if not uri:
        return None
    try:
        raw_id = int(uri.rstrip('/').split('/')[-1])
        # Check if it's a meteoparameter (different vocabulary)
        if '/meteoparameter/' in uri:
            return METEOPARAMETER_MAPPINGS.get(raw_id, raw_id)
        # Apply pollutant ID mapping for deprecated IDs
        return POLLUTANT_ID_MAPPINGS.get(raw_id, raw_id)
    except ValueError:
        return None


class Migration:
    """Handle Raven v3 → v4 migration with transaction support"""
    
    def __init__(self, dry_run=False, batch_size=10000, recreate_schema=False, init_only=False,
                 remediate_only=False, country_code=None):
        self.country_code = country_code
        self._vocab_cache = {}
        self._admin_level_ids = None
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.recreate_schema = recreate_schema
        self.init_only = init_only
        self.remediate_only = remediate_only
        self.source_conn = None
        self.target_conn = None
        self.stats = {}

    def resolve_vocabulary_id(self, table, uri):
        """Look an EEA vocabulary id up by URI, falling back to the URI's last segment.

        The eea_* tables are keyed by the concept's *notation*, and EEA does not always
        write the notation the way it writes the URI: aq/measurementequipment/GRIMM-EDM180
        has notation "GRIMM EDM 180", with spaces. Deriving the id from the URI suffix
        therefore produces a value no row holds, and the foreign key rejects it -- which
        is a migration abort, since this all runs in one transaction. Five of 380
        equipment terms and three of 50 method terms diverge this way.

        v3 stores the full URI and every eea_* table keeps a `uri` column, so matching on
        URI is both the correct join and immune to the next such divergence. The suffix
        stays as the fallback for a concept the target vocabulary simply does not have --
        the caller decides whether that is fatal.
        """
        if not uri:
            return None
        cache = self._vocab_cache.setdefault(table, None)
        if cache is None:
            cur = self.target_conn.cursor()
            cur.execute(sql.SQL('SELECT uri, id FROM {} WHERE uri IS NOT NULL').format(
                sql.Identifier(table)))
            cache = {u: str(i) for u, i in cur.fetchall()}
            cur.close()
            self._vocab_cache[table] = cache
        found = cache.get(uri.rstrip('/')) or cache.get(uri)
        if found is not None:
            return found
        return extract_notation_from_uri(uri)

    def _admin_levels(self):
        """The ids aq/administrativelevel actually offers, cached."""
        if getattr(self, '_admin_level_ids', None) is None:
            cur = self.target_conn.cursor()
            cur.execute('SELECT id FROM eea_administrativelevels')
            self._admin_level_ids = {r[0] for r in cur.fetchall()}
            cur.close()
        return self._admin_level_ids

    def source_has_table(self, table):
        """True when the v3 source actually has this table.

        v3 was deployed per country over several years and the deployments drifted:
        the Andorra database has no `directives` table at all, and its `settings`
        predates country_code. Probing beats assuming, because this migration runs in
        one transaction -- a missing relation aborts the whole run at whatever point
        it is reached, after everything before it has already been done.
        """
        cur = self.source_conn.cursor()
        cur.execute("""
            SELECT EXISTS (SELECT 1 FROM information_schema.tables
                            WHERE table_schema = 'public' AND table_name = %s)
        """, (table,))
        found = cur.fetchone()[0]
        cur.close()
        return found

    def source_has_column(self, table, column):
        """True when the v3 source has this column. See source_has_table()."""
        cur = self.source_conn.cursor()
        cur.execute("""
            SELECT EXISTS (SELECT 1 FROM information_schema.columns
                            WHERE table_schema = 'public'
                              AND table_name = %s AND column_name = %s)
        """, (table, column))
        found = cur.fetchone()[0]
        cur.close()
        return found

    def target_uri(self):
        """The target as a libpq URI, for subprocesses that take --db-uri."""
        return (f"postgresql://{TARGET_DB['user']}:{TARGET_DB['password']}"
                f"@{TARGET_DB['host']}:{TARGET_DB['port']}/{TARGET_DB['database']}")

    @property
    def target_only(self):
        """True when no source database is needed."""
        return self.init_only or self.remediate_only

    def connect(self):
        """Connect to both databases (or only target when --init-only/--remediate-only)"""
        if not self.target_only:
            log("Connecting to source database (ravendb)...")
            self.source_conn = psycopg2.connect(**SOURCE_DB)
            self.source_conn.set_session(readonly=True)

        log("Connecting to target database (ravendb4)...")
        self.target_conn = psycopg2.connect(**TARGET_DB)
        # Don't autocommit - we want transaction control
        self.target_conn.autocommit = False

        log("✓ Connected to target database" if self.target_only
            else "✓ Connected to both databases")
    
    def close(self):
        """Close connections"""
        if self.source_conn:
            self.source_conn.close()
        if self.target_conn:
            self.target_conn.close()
    
    def check_schema_exists(self):
        """Check if the v4 schema exists in target database"""
        cur = self.target_conn.cursor()
        # Check for a core table that's always created
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'sampling_points'
        """)
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    
    def setup_schema(self):
        """Create schema if it doesn't exist"""
        log("\n🔍 Checking target database schema...")
        
        if self.check_schema_exists() and not self.recreate_schema:
            log("   ✓ Schema already exists")
            return
        
        if self.recreate_schema and self.check_schema_exists():
            log("   Recreating schema (--recreate-schema flag set)...")
            # Close current connection and reconnect with fresh connection
            self.close()
            
            # Use a separate connection for cleanup
            cleanup_conn = psycopg2.connect(**TARGET_DB)
            cleanup_conn.autocommit = True
            cleanup_cur = cleanup_conn.cursor()
            
            # Get all tables in public schema
            cleanup_cur.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' AND tablename NOT LIKE 'pg_%'
                ORDER BY tablename DESC
            """)
            tables = [row[0] for row in cleanup_cur.fetchall()]
            
            if tables:
                log(f"   Dropping {len(tables)} tables...")
                for table in tables:
                    try:
                        cleanup_cur.execute(f"DROP TABLE IF EXISTS \"{table}\" CASCADE")
                    except Exception as e:
                        log(f"   Warning: Could not drop {table}: {e}")
            
            cleanup_cur.close()
            cleanup_conn.close()
            log("   ✓ Old schema dropped")
            
            # Reconnect
            self.connect()
        
        if self.check_schema_exists() and not self.recreate_schema:
            log("   ✓ Schema already exists")
            return
        
        log("   Creating schema...")
        
        # Find schema file relative to this script (canonical schema in raven-admin/sql/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_file = os.path.join(script_dir, '..', 'schema.sql')
        
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        log(f"   Loading schema from: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        cur = self.target_conn.cursor()
        cur.execute(schema_sql)
        cur.close()
        
        # Commit schema so populate script can see it
        self.target_conn.commit()
        
        log("   ✓ Schema created successfully")
    
    def populate_lookups(self):
        """Populate EEA lookup tables from RDF vocabularies"""
        log("\n📥 Checking/populating lookup tables...")
        
        cur = self.target_conn.cursor()
        
        # Check if lookups already populated
        cur.execute("SELECT COUNT(*) FROM eea_pollutants")
        pollutant_count = cur.fetchone()[0]
        
        if pollutant_count > 0:
            log(f"   ✓ Lookups already populated ({pollutant_count} pollutants)")
            cur.close()
            return
        
        log("   Lookups empty - populating from RDF vocabularies...")

        # sql/populate_vocabularies.py is the canonical loader and lives in this repo,
        # so it ships in every image. The old path went four levels up to
        # ../../../../raven-rn3-db/populate_lookups_v4_2.py -- outside the repo and
        # absent from the container -- so this step raised FileNotFoundError on any
        # target whose eea_pollutants was empty, which is every fresh install.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        populate_script = os.path.join(script_dir, '..', 'populate_vocabularies.py')

        if not os.path.exists(populate_script):
            raise FileNotFoundError(f"Populate script not found: {populate_script}")

        # It takes --db-uri (defaulting to $DB_URI), not the TARGET_DB_* variables this
        # script uses, so pass the target explicitly rather than letting it pick up
        # whichever DB_URI the environment happens to carry -- which on a developer
        # machine is usually a different database entirely.
        import subprocess
        result = subprocess.run(
            [sys.executable, populate_script, '--db-uri', self.target_uri()],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.abspath(populate_script))
        )

        if result.returncode != 0:
            log(f"   ⚠ Populate script output: {result.stderr}")
            raise RuntimeError(f"Populate script failed: {result.stderr}")

        log("   ✓ Lookup tables populated")
        cur.close()
    
    def remediate_legacy_data(self):
        """Derive AQR3 v5.02 columns from data an older Raven already holds.

        This is the DML half of migrations 002, 003 and 004. Their DDL is in
        sql/schema.sql; these three statements are not expressible there because they
        depend on rows rather than structure, so they moved here when 001-010 were
        archived (see sql/migrations/archive/README.md).

        Be clear about when this does work. A plain v3 -> v4 run populates none of the
        three inputs: observations.meta is written as NULL below (it is an ADACS-only
        field), and exceedancedescriptions / srs_inline are never migrated at all. So
        during a v3 -> v4 run this is a no-op by construction, and that is fine -- it
        earns its place because --remediate-only makes it runnable against a database
        that DOES hold such rows: one fed by ADACS or AirQUIS, or populated through the
        admin UI. Each statement is idempotent and reports what it changed.
        """
        log("\n🔧 Remediating legacy data (AQR3 v5.02 derived columns)...")

        cur = self.target_conn.cursor()

        # --- 002: observations.data_capture from the ADACS instrument validity ------
        #
        # OMR_14 DataCapture is the share of the averaging period with valid raw data.
        # ADACS records it in observations.meta; nothing else does, so it is only
        # derivable where meta is present.
        #
        # The trigger suspension is load-bearing, not tidiness:
        # raven_observations_set_timestamp_trigger sets `touched` on every UPDATE, and
        # `touched` is exported as the AQR3 ResultTime. Without this, backfilling a
        # derived column would rewrite the reported time of every observation it
        # touches, silently changing what has already been submitted.
        cur.execute("""
            select count(*) from information_schema.columns
            where table_schema = 'public' and table_name = 'observations'
              and column_name = 'meta'
        """)
        if cur.fetchone()[0]:
            cur.execute("alter table observations disable trigger "
                        "raven_observations_set_timestamp_trigger")
            try:
                cur.execute("""
                    update observations
                       set data_capture = (meta->>'instrument_validity')::numeric
                     where data_capture is null
                       and meta ? 'instrument_validity'
                       and (meta->>'instrument_validity') ~ '^[0-9]+(\\.[0-9]+)?$'
                """)
                log(f"   ✓ observations.data_capture: {cur.rowcount:,} row(s) derived from meta")
            finally:
                cur.execute("alter table observations enable trigger "
                            "raven_observations_set_timestamp_trigger")
        else:
            log("   - observations.meta absent; nothing to derive for data_capture")

        # --- 003: pollution_level_adjustment from exceedance descriptions ----------
        #
        # ADJ_02/ADJ_03: one row per (attainment, adjustment source). The v3-era
        # exceedancedescriptions.adjustment_source already names the source, so the ADJ
        # row can be created; the quantities (adjusted concentration, method, document)
        # are entered afterwards in the admin UI, which is why only two of the four
        # columns are written here.
        cur.execute("""
            select to_regclass('public.exceedancedescriptions') is not null
               and exists (select 1 from information_schema.columns
                           where table_schema = 'public'
                             and table_name = 'exceedancedescriptions'
                             and column_name = 'adjustment_source')
        """)
        if cur.fetchone()[0]:
            cur.execute("""
                insert into pollution_level_adjustment (attainment_id, adjustment_source_id)
                select distinct ed.attainment_id, ed.adjustment_source
                  from exceedancedescriptions ed
                 where ed.adjustment_source is not null
                   and ed.attainment_id is not null
                on conflict (attainment_id, adjustment_source_id) do nothing
            """)
            log(f"   ✓ pollution_level_adjustment: {cur.rowcount:,} row(s) seeded "
                f"from exceedancedescriptions")
        else:
            log("   - exceedancedescriptions.adjustment_source absent; no ADJ rows to seed")

        # --- 004: snap srs_inline to the EPSG:3035 INSPIRE grid --------------------
        #
        # SRI_03/SRI_04 must be INSPIRE grid cell coordinates: the south-west corner of
        # a cell whose side is spatial_resolution metres. Rows written before that rule
        # was enforced hold arbitrary coordinates, and snapping can collide two rows
        # onto one cell, so de-duplicate afterwards -- keeping the lowest ctid, which is
        # arbitrary but deterministic.
        #
        # Only the DML lives here. 004's ALTER COLUMN retypes stayed in the archive:
        # they apply to a database whose srs_inline descends from the NILU-only
        # sr_area_inline, and schema.sql already declares the final types.
        cur.execute("select to_regclass('public.srs_inline') is not null")
        if cur.fetchone()[0]:
            cur.execute("""
                update srs_inline
                   set x = floor(x::numeric / spatial_resolution)::bigint * spatial_resolution,
                       y = floor(y::numeric / spatial_resolution)::bigint * spatial_resolution
                 where spatial_resolution is not null
                   and spatial_resolution > 0
                   and (x % spatial_resolution <> 0 or y % spatial_resolution <> 0)
            """)
            snapped = cur.rowcount
            cur.execute("""
                delete from srs_inline a
                 where a.ctid > (select min(b.ctid) from srs_inline b
                                  where b.spatial_representativeness_id
                                        = a.spatial_representativeness_id
                                    and b.x = a.x and b.y = a.y
                                    and b.spatial_resolution = a.spatial_resolution)
            """)
            log(f"   ✓ srs_inline: {snapped:,} cell(s) snapped to the EPSG:3035 grid, "
                f"{cur.rowcount:,} duplicate(s) removed")
        else:
            log("   - srs_inline absent; no grid snapping needed")

        cur.close()

    def clear_migration_tables(self):
        """Clear data tables before migration (preserve lookups)"""
        log("\n🗑️ Clearing existing data from target tables...")
        
        cur = self.target_conn.cursor()
        
        # Tables to clear in reverse FK order (v4.8.0 names)
        tables_to_clear = [
            'notifications_samplingpoints', 'notifications_runs', 'notifications',
            'aqi', 'statistics', 'directives',
            'exceedingmethods', 'exceedancedescriptions', 'attainments',
            'assessmentdata', 'assessment_regimes', 'zones',
            'autovalidated_series', 'converted_series', 'calculated_series', 'scaling_points',
            'observations', 'processes', 'sampling_points',
            'stations', 'groupnetwork', 'networks', 'authorities',
            'documents',  # v4.8.0: centralized document references
            'usergroup', 'users', '"group"', 'settings'
        ]
        
        # Use savepoint to allow continuing after failures
        for table in tables_to_clear:
            try:
                cur.execute(f"TRUNCATE TABLE {table} CASCADE")
            except Exception as e:
                # Rollback just this statement but continue
                self.target_conn.rollback()
                # Don't log - table may not exist which is fine
        
        log("   ✓ Data tables cleared")
        cur.close()
    
    def run(self):
        """Run the complete migration"""
        try:
            self.connect()
            
            log("=" * 60)
            if self.init_only:
                log("RAVEN v4 DATABASE INITIALISATION")
            elif self.remediate_only:
                log("RAVEN v4 LEGACY DATA REMEDIATION")
                log(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
            else:
                log("RAVEN v3 → v4 DATA MIGRATION")
                log(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
                log(f"Batch size: {self.batch_size:,}")
            log("=" * 60)

            # Remediation acts on an existing populated database, so it must not touch
            # the schema or the lookups -- and above all must not clear any table.
            if self.remediate_only:
                self.remediate_legacy_data()
                if self.dry_run:
                    log("\n🔄 DRY RUN - Rolling back all changes...")
                    self.target_conn.rollback()
                else:
                    log("\n💾 Committing remediation...")
                    self.target_conn.commit()
                return

            # Setup: ensure schema and lookups exist
            self.setup_schema()
            self.populate_lookups()

            if self.init_only:
                log("\n💾 Committing schema and lookup tables...")
                self.target_conn.commit()
                log("✓ Blank database initialised successfully")
                return

            self.clear_migration_tables()
            
            # Run migrations in order (respecting FK dependencies)
            self.migrate_settings()
            self.migrate_groups()
            self.migrate_users()
            self.migrate_usergroups()
            self.migrate_responsible_authorities()
            self.migrate_networks()
            self.migrate_groupnetworks()
            self.migrate_stations()
            self.migrate_sampling_points_with_samples()  # Merged
            self.migrate_processes_with_observing_capabilities()  # Merged
            self.migrate_observations()  # Big one - batched
            self.migrate_scaling_points()
            self.migrate_calculated_series()
            self.migrate_converted_series()
            self.migrate_autovalidated_series()
            self.migrate_zones()
            self.migrate_assessment_tables()
            self.migrate_supporting_tables()
            self.migrate_notifications()

            # Last, so it sees everything the migration wrote. A no-op on a pure v3
            # source -- see remediate_legacy_data's docstring for why it runs anyway.
            self.remediate_legacy_data()


            # Commit or rollback
            if self.dry_run:
                log("\n🔄 DRY RUN - Rolling back all changes...")
                self.target_conn.rollback()
            else:
                log("\n💾 Committing all changes...")
                self.target_conn.commit()
            
            self.print_summary()
            
        except Exception as e:
            log(f"\n❌ ERROR: {e}")
            if self.target_conn:
                log("🔄 Rolling back transaction...")
                self.target_conn.rollback()
            raise
        finally:
            self.close()
    
    def migrate_settings(self):
        """Migrate settings table (1 row) - v4.4.0 simplified to just country_code_id, timezone_id"""
        log("\n📋 Migrating settings...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # CountryCode is the first column of every AQR3 table, so the migration cannot
        # proceed without one. Three sources, in descending order of authority.
        country_code = None
        if self.country_code:
            country_code = self.country_code
            source = '--country-code'
        elif self.source_has_column('settings', 'country_code'):
            src.execute("SELECT country_code FROM settings LIMIT 1")
            row = src.fetchone()
            country_code = row[0] if row else None
            source = 'v3 settings.country_code'
        else:
            # Older v3 deployments have no country_code: Andorra's settings is
            # (id, namespace, uom_m, observation_prefix, language_code). The EoI code
            # EIONET assigned each station opens with the country, so derive it from
            # there -- but only when every station agrees, because a disagreement means
            # the assumption does not hold and guessing would poison every AQR3 table.
            src.execute("""
                SELECT DISTINCT upper(left(eoi_code, 2))
                  FROM stations
                 WHERE eoi_code IS NOT NULL AND length(eoi_code) >= 2
            """)
            prefixes = [r[0] for r in src.fetchall()]
            if len(prefixes) == 1:
                country_code = prefixes[0]
                source = 'stations.eoi_code prefix'
            else:
                raise RuntimeError(
                    "v3 settings has no country_code and the station EoI codes do not "
                    f"agree on one country (found {prefixes or 'none'}). "
                    "Re-run with --country-code XX.")

        if not country_code:
            raise RuntimeError("Could not determine the country code. Use --country-code XX.")

        # settings.timezone_id is what the AQR3 export resolves its UTC offset from
        # (core/reporting/aqr3/context.py). Left NULL, the offset resolves to '' and
        # every datetime in every exported table is emitted naive -- "2005-01-01
        # 00:00:00" rather than "2005-01-01 00:00:00+01:00" -- which AQR3 rejects.
        # v3 held the same fact per network, as networks.aggregation_timezone, so take
        # it from there when the networks agree.
        timezone_id = None
        if self.source_has_column('networks', 'aggregation_timezone'):
            src.execute("""
                SELECT DISTINCT aggregation_timezone
                  FROM networks
                 WHERE aggregation_timezone IS NOT NULL
            """)
            zones = [extract_notation_from_uri(r[0]) for r in src.fetchall()]
            zones = sorted({z for z in zones if z})
            if len(zones) == 1:
                timezone_id = zones[0]
                log(f"   timezone_id  = {timezone_id}  (from networks.aggregation_timezone)")
            elif zones:
                log(f"   ⚠ networks disagree on a timezone ({zones}); settings.timezone_id "
                    f"left NULL - set it in the admin UI before exporting to Reportnet3")
        if timezone_id is None:
            log("   ⚠ settings.timezone_id is NULL - AQR3 datetimes will carry no UTC "
                "offset until it is set")

        log(f"   country_code = {country_code}  (from {source})")
        tgt.execute("""
            INSERT INTO settings (country_code_id, timezone_id)
            VALUES (%s, %s)
        """, (country_code, timezone_id))
        self.stats['settings'] = 1
        log(f"   ✓ 1 row")
        
        src.close()
        tgt.close()
    
    def migrate_groups(self):
        """Migrate group table"""
        log("\n📋 Migrating groups...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        src.execute('SELECT * FROM "group"')
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            tgt.execute(f"""
                INSERT INTO "group" ({', '.join(cols)})
                VALUES ({', '.join(['%s'] * len(cols))})
                ON CONFLICT (id) DO NOTHING
            """, row)
        
        self.stats['group'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_users(self):
        """Migrate users table"""
        log("\n📋 Migrating users...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        src.execute("SELECT * FROM users")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            tgt.execute(f"""
                INSERT INTO users ({', '.join(cols)})
                VALUES ({', '.join(['%s'] * len(cols))})
                ON CONFLICT (id) DO NOTHING
            """, row)
        
        self.stats['users'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_usergroups(self):
        """Migrate usergroup table"""
        log("\n📋 Migrating usergroups...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        src.execute("SELECT * FROM usergroup")
        rows = src.fetchall()
        
        for row in rows:
            tgt.execute("""
                INSERT INTO usergroup (userid, groupid)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, row)
        
        self.stats['usergroup'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_responsible_authorities(self):
        """Migrate responsible_authorities to authorities (v4.3.0 simplified)"""
        log("\n📋 Migrating authorities...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v3: id, name, organisation, locator, postcode, email, address, phone, website, is_responsible_reporter
        # v4: id, person_name, email, authority_name, authority_url, authority_address, authority_instance_id, authority_role_id, authority_status_id
        # DEFAULTS: authority_instance_id='network', authority_role_id='AQD', authority_status_id='active' (for RN3 required fields)
        # is_responsible_reporter carries the one piece of role information v3 held, so
        # read it where it exists rather than sending every authority to the same role.
        has_reporter_flag = self.source_has_column('responsible_authorities',
                                                   'is_responsible_reporter')
        reporter_col = 'is_responsible_reporter' if has_reporter_flag else 'false'
        src.execute(f"""
            SELECT id, name, organisation, email, website, address, {reporter_col}
              FROM responsible_authorities
        """)
        rows = src.fetchall()

        for row in rows:
            id_val, name, organisation, email, website, address, is_reporter = row
            tgt.execute("""
                INSERT INTO authorities 
                (id, person_name, email, authority_name, authority_url, authority_address,
                 authority_instance_id, authority_role_id, authority_status_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id, authority_role_id, email) DO NOTHING
            """, (id_val, name, email, organisation, website, address,
                  # AUT_05 AuthorityInstance is keyed by concept name since migration 019:
                  # 'Network', not the old lowercase 'network'. v3 attaches an authority to
                  # a network (networks.responsible_authority_id), so that is the instance.
                  # AUT_03 AuthorityRole is eea_authorityobject, whose terms are
                  # 'reporting' and 'assessment' -- 'AQD' was never one of them.
                  'Network',
                  'reporting' if is_reporter else 'assessment',
                  'active'))
        
        self.stats['authorities'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_networks(self):
        """Migrate networks (v4.8.0: id, name, administration_level_id, timezone_id - removed report_id)"""
        log("\n📋 Migrating networks...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v3: id, name, media_monitored, responsible_authority_id, organisational, begin_position, end_position, aggregation_timezone
        # v4.502: id, name, network_organisational_level_id (AQR3 STA_05), timezone_id.
        # network_document_id (STA_09) has no v3 source and is filled through the admin UI.
        src.execute("SELECT id, name, organisational, aggregation_timezone FROM networks")
        rows = src.fetchall()
        
        for row in rows:
            id_val, name, organisational, aggregation_timezone = row
            # Transform URI FK to notation
            # The URI lookup fails for a term v4's vocabulary retired, so fall back to
            # the documented remapping before giving up; anything still unrecognised is
            # left NULL with a warning rather than aborting the whole migration.
            admin_level = self.resolve_vocabulary_id('eea_administrativelevels', organisational)
            if admin_level and admin_level not in self._admin_levels():
                suffix = extract_notation_from_uri(organisational)
                if suffix in RETIRED_ADMINISTRATIVE_LEVELS:
                    mapped = RETIRED_ADMINISTRATIVE_LEVELS[suffix]
                    log(f"   ℹ {id_val}: organisational level '{suffix}' is retired in v4 -> "
                        f"{mapped or 'NULL'}")
                    admin_level = mapped
                else:
                    log(f"   ⚠ {id_val}: organisational level '{suffix}' is not a term of "
                        f"aq/administrativelevel and has no mapping - left NULL")
                    admin_level = None
            # Extract timezone notation from URI (e.g., 'http://.../timezone/UTC+02' -> 'UTC+02')
            timezone_id = self.resolve_vocabulary_id('eea_timezones', aggregation_timezone)
            
            tgt.execute("""
                INSERT INTO networks (id, name, network_organisational_level_id, timezone_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (id_val, name, admin_level, timezone_id))
        
        self.stats['networks'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_groupnetworks(self):
        """Migrate groupnetwork table"""
        log("\n📋 Migrating groupnetworks...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        src.execute("SELECT * FROM groupnetwork")
        rows = src.fetchall()
        
        for row in rows:
            tgt.execute("""
                INSERT INTO groupnetwork (groupid, networkid)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, row)
        
        self.stats['groupnetwork'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_stations(self):
        """Migrate stations (v4.8.0: id, station_eoi_code, name, station_national_code, lat, lon, alt, supersite, station_area_id, document_id, network_id)"""
        log("\n📋 Migrating stations...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v3: id, name, begin_position, end_position, network_id, city, national_station_code,
        #     media_monitored, mobile, measurement_regime, area_classification, distance_junction,
        #     traffic_volume, heavy_duty_fraction, street_width, height_facades, geom, municipality,
        #     eoi_code, city_code
        # v4.8.0: id, station_eoi_code, name, station_national_code, lat, lon, alt, supersite, station_area_id, document_id, network_id
        # Note: document_id will be NULL - needs to be populated separately via documents table
        #
        # The SELECT below reads the SOURCE, so it must use v3 spellings: eoi_code
        # (renamed to station_eoi_code by migration 002) and national_station_code
        # (which v4 calls station_national_code). Verified by introspecting
        # dev-db-dmz02/ravendb 2026-08-18. A rename pass once applied the v4 names
        # here too, which made this query fail against every v3 database.
        src.execute("""
            SELECT id, eoi_code, name, national_station_code,
                   ST_Y(geom) as latitude, ST_X(geom) as longitude, ST_Z(geom) as altitude,
                   area_classification, network_id
            FROM stations
        """)
        rows = src.fetchall()
        
        for row in rows:
            id_val, eoi, name, station_national_code, lat, lon, alt, area_class_uri, network_id = row
            # Transform URI FK to notation
            station_area_id = self.resolve_vocabulary_id('eea_areaclassifications', area_class_uri)
            
            tgt.execute("""
                INSERT INTO stations (id, station_eoi_code, name, station_national_code, latitude, longitude, altitude, 
                                      supersite, station_area_id, document_id, network_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (id_val, eoi, name, station_national_code, lat, lon, alt, 
                  False, station_area_id, None, network_id))  # document_id = NULL
        
        self.stats['stations'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_sampling_points_with_samples(self):
        """Migrate sampling_points (v4.4.0 simplified)"""
        log("\n📋 Migrating sampling_points...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v4.4.0: id, sampling_point_reference_id, inlet_height, building_distance, kerb_distance, emission_source_distance,
        #         logger_id, private, use_in_public_api, from_time, to_time,
        #         pollutant_id, time_resolution_id, unit_id, sampling_point_category_id, station_id
        # Need the station's EoI code for generating sampling_point_reference_id.
        # v3 spelling: st.eoi_code (migration 002 renamed it to station_eoi_code in v4).
        src.execute("""
            SELECT DISTINCT ON (sp.id)
                sp.id,
                s.inlet_height,
                s.building_distance,
                s.kerb_distance,
                sp.logger_id,
                sp.private,
                sp.use_in_public_api,
                -- from_time is v3's observation-data window and is what v4 uses for
                -- SPL_03 LocationBegin, which AQR3 makes part of SamplingPointLocation's
                -- unique key. It is NULL for a sampling point that never collected data,
                -- and an empty mandatory key column fails validation -- so fall back to
                -- begin_position, v3's declared AQD validity period, which is the only
                -- other date it holds. The two are different facts (they disagree on 17
                -- of Andorra's 44 populated rows), hence a fallback and not a COALESCE
                -- of preference. The offset is dropped to match from_time, which v3
                -- already stores as naive local time.
                COALESCE(sp.from_time,
                         substring(sp.begin_position from 1 for 19)::timestamp) as from_time,
                COALESCE(sp.to_time,
                         substring(sp.end_position from 1 for 19)::timestamp) as to_time,
                sp.pollutant,
                sp.timestep,
                sp.concentration,
                sp.station_classification,
                sp.station_id,
                st.eoi_code
            FROM sampling_points sp
            LEFT JOIN observing_capabilities oc ON sp.id = oc.sampling_point_id
            LEFT JOIN samples s ON oc.sample_id = s.id
            LEFT JOIN stations st ON sp.station_id = st.id
        """)
        rows = src.fetchall()
        
        # Track SPOref counters per station+pollutant combination
        spo_ref_counters = {}
        meteo_count = [0]
        
        for row in rows:
            (id_val, inlet_height, building_distance, kerb_distance, logger_id, 
             private, use_in_public_api, from_time, to_time, 
             pollutant_uri, timestep_uri, concentration_uri, station_classification_uri, station_id, station_eoi_code) = row
            
            # Transform URIs
            pollutant_id = extract_pollutant_id_from_uri(pollutant_uri)
            time_resolution_id = self.resolve_vocabulary_id('eea_times', timestep_uri)
            unit_id = self.resolve_vocabulary_id('eea_concentrations', concentration_uri)
            # station_classification URI -> sampling_point_category_id (extract last part, lowercase)
            # eea_spocategory is keyed lowercase; v3 writes the URI in the stationclassification
            # vocabulary, so try the URI first and lowercase whatever comes back.
            sampling_point_category_id = self.resolve_vocabulary_id(
                'eea_spocategory', station_classification_uri)
            if sampling_point_category_id:
                sampling_point_category_id = sampling_point_category_id.lower()

            # Generate sampling_point_reference_id (AQR3 SPO_03): SPOref_[EOI]_[POLLUTANT_ID]_[N]
            # e.g., SPOref_NO0042A_00005_1
            if station_eoi_code and pollutant_id:
                ref_key = f"{station_eoi_code}_{pollutant_id:05d}"
                spo_ref_counters[ref_key] = spo_ref_counters.get(ref_key, 0) + 1
                sampling_point_reference_id = f"SPOref_{station_eoi_code}_{pollutant_id:05d}_{spo_ref_counters[ref_key]}"
                # Truncate to 32 chars if needed
                sampling_point_reference_id = sampling_point_reference_id[:32]
            else:
                sampling_point_reference_id = None

            # aq/pollutant and aq/meteoparameter share one id space (see migration 017),
            # so a meteoparameter keeps a perfectly valid pollutant_id and its EEA
            # identity -- 51 is "Wind velocity". What it is not is part of the reporting
            # obligation: AQR3 SPO/SPL/SPP/OMR describe pollutant measurements. Intent
            # and capability are separate columns since 4.502.22, and this is exactly the
            # case report_to_eea exists for, so the flag carries it rather than a NULL
            # pollutant_id that would also throw away which parameter it is.
            is_meteo = bool(pollutant_uri) and '/meteoparameter/' in pollutant_uri
            if is_meteo:
                meteo_count[0] += 1

            tgt.execute("""
                INSERT INTO sampling_points
                (id, sampling_point_reference_id, inlet_height, building_distance, kerb_distance, emission_source_distance,
                 logger_id, private, use_in_public_api, from_time, to_time,
                 pollutant_id, time_resolution_id, unit_id, sampling_point_category_id, station_id,
                 report_to_eea)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                id_val, sampling_point_reference_id, inlet_height, building_distance, kerb_distance, None,
                logger_id, private or False, use_in_public_api or False, from_time, to_time,
                pollutant_id, time_resolution_id, unit_id, sampling_point_category_id, station_id,
                not is_meteo
            ))
        
        self.stats['sampling_points'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        if meteo_count[0]:
            log(f"   ℹ {meteo_count[0]} meteoparameter series set report_to_eea = false "
                f"(kept, but out of AQR3 scope)")
        
        src.close()
        tgt.close()
    
    def migrate_processes_with_observing_capabilities(self):
        """Migrate processes (v4.8.0: with 3 document references)"""
        log("\n📋 Migrating processes...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v4.8.0: id, process_activity_begin, process_activity_end, 
        #         data_quality_document_id, equivalence_demonstration_document_id, process_document_id,
        #         measurement_type_id, method_id, equipment_id, analytical_technique_id,
        #         equivalence_demonstrated_id, sampling_point_id
        # Note: document_ids will be NULL - needs to be populated separately via documents table
        # One row per observing capability, not per process. v4's primary key is
        # (id, sampling_point_id, process_activity_begin) precisely because one
        # equipment configuration serves several sampling points and several operating
        # periods; the DISTINCT ON (p.id) this replaces collapsed all of them into one
        # row. On the Andorra database SPP-METEO alone covers 21 sampling points, so 20
        # of its 21 capabilities were being dropped.
        src.execute("""
            SELECT
                p.id,
                oc.begin_position as process_activity_begin,
                oc.end_position as process_activity_end,
                p.measurement_type,
                p.measurement_method,
                p.measurement_equipment,
                p.analytical_tech,
                p.equiv_demonstration,
                oc.sampling_point_id
            FROM processes p
            LEFT JOIN observing_capabilities oc ON p.id = oc.process_id
            WHERE oc.sampling_point_id IS NOT NULL
        """)
        rows = src.fetchall()
        
        for row in rows:
            (id_val, process_activity_begin, process_activity_end, meas_type_uri, meas_method_uri,
             meas_equip_uri, analytical_tech, equiv_demo_uri, sampling_point_id) = row
            
            # Transform URI FKs to notation
            measurement_type_id = self.resolve_vocabulary_id('eea_measurementtypes', meas_type_uri)
            method_id = self.resolve_vocabulary_id('eea_measurementmethods', meas_method_uri)
            equipment_id = self.resolve_vocabulary_id('eea_measurementequipments', meas_equip_uri)
            equivalence_demonstrated_id = self.resolve_vocabulary_id(
                'eea_equivalencedemonstrated', equiv_demo_uri)
            # analytical_technique_id - keep as-is for now (text field in v3)
            
            tgt.execute("""
                INSERT INTO processes 
                (id, process_activity_begin, process_activity_end, 
                 data_quality_document_id, equivalence_demonstration_document_id, process_document_id,
                 measurement_type_id, method_id, equipment_id, analytical_technique_id,
                 equivalence_demonstrated_id, sampling_point_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id, sampling_point_id, process_activity_begin) DO NOTHING
            """, (
                id_val, process_activity_begin, process_activity_end, 
                None, None, None,  # 3 document_ids = NULL
                measurement_type_id, method_id, equipment_id, None,  # analytical_technique_id
                equivalence_demonstrated_id, sampling_point_id
            ))
        
        self.stats['processes'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    def duplicate_observation_ids(self):
        """Ids of the v3 observations that lose a (sampling_point, from_time, to_time) tie.

        v4 declares that triple unique; v3 did not, so a v3 database can hold several rows
        for one sampling point and hour. Ranking, in order:

          1. a valid reading beats an invalid one (validation_flag >= 1), so a real
             measurement is never dropped in favour of a -999 placeholder;
          2. otherwise the higher id wins -- the later import, which on a database with
             overlapping imports is the stream the instance is still writing to.

        Returns the losers, so the caller skips them. Empty on a source with no duplicates,
        which is the normal case and costs one scan to establish.
        """
        cur = self.source_conn.cursor()
        cur.execute("""
            SELECT id FROM (
                SELECT id,
                       row_number() OVER (
                           PARTITION BY sampling_point_id, from_time, to_time
                           ORDER BY (validation_flag >= 1) DESC, id DESC
                       ) AS rn
                  FROM observations
            ) ranked
            WHERE rn > 1
        """)
        losers = {r[0] for r in cur.fetchall()}
        cur.close()
        if losers:
            log(f"   ⚠ {len(losers):,} duplicate (sampling_point, from_time, to_time) row(s) "
                f"in the v3 source - keeping the valid/later row of each")
        return losers

    def migrate_observations(self):
        """Migrate observations table (v4.5.0 - batched for 4M+ rows, v3-compatible columns)"""
        log("\n📋 Migrating observations (batched)...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # Get total count
        src.execute("SELECT COUNT(*) FROM observations")
        total = src.fetchone()[0]
        log(f"   Total rows to migrate: {total:,}")
        
        # v4.6.0: Map old verification_flag (0,1) to EEA vocab (3,1)
        # Old: 0=not verified, 1=verified
        # EEA: 1=verified, 2=preliminary, 3=not verified
        # Map: 0 -> 3, 1 -> 1
        #
        # validation_flag values are same in both systems: -99, -1, 1, 2, 3, 4
        # Keyset paging, not LIMIT/OFFSET: OFFSET makes the server walk and discard
        # every earlier row, so paging 6.5M rows this way is quadratic and spends most
        # of its time re-reading the start of the table. `id` is the primary key, so
        # `id > last_id ORDER BY id` seeks straight to each page.
        #
        # And one execute_values() per page instead of one execute() per row: the
        # round trip dominated everything else at this volume.
        # v4 has a unique constraint on (sampling_point_id, from_time, to_time) that v3
        # never had, so a v3 database may hold rows v4 cannot accept. Serbia does: two
        # overlapping imports, one legacy and one still running, wrote the same local hour
        # twice with different UTC offsets -- 145,842 collisions across 2014-2020.
        #
        # Resolved here rather than by ON CONFLICT DO NOTHING, because which row survives
        # must be a decision and not an accident of insertion order: keep a valid reading
        # over an invalid one, and otherwise keep the later import, which is the stream the
        # instance is still running on. The losers are collected up front -- a few hundred
        # thousand integers at worst -- so the paging below stays a plain keyset scan.
        skip_ids = self.duplicate_observation_ids()
        skipped = 0

        last_id = None
        migrated = 0

        while True:
            if last_id is None:
                src.execute("""
                    SELECT id, sampling_point_id, value,
                           verification_flag, validation_flag, touched, from_time, to_time,
                           import_value, scaled_value
                    FROM observations
                    ORDER BY id
                    LIMIT %s
                """, (self.batch_size,))
            else:
                src.execute("""
                    SELECT id, sampling_point_id, value,
                           verification_flag, validation_flag, touched, from_time, to_time,
                           import_value, scaled_value
                    FROM observations
                    WHERE id > %s
                    ORDER BY id
                    LIMIT %s
                """, (last_id, self.batch_size))
            rows = src.fetchall()
            if not rows:
                break

            values = []
            for row in rows:
                (id_val, sp_id, value,
                 verification_flag, validation_flag, touched, from_time, to_time,
                 import_value, scaled_value) = row

                if id_val in skip_ids:
                    skipped += 1
                    continue

                # Map old verification_flag to EEA observationverification_id
                # 0 -> 3 (not verified), 1 -> 1 (verified)
                observationverification_id = 1 if verification_flag == 1 else 3

                values.append((
                    id_val, sp_id, value,
                    observationverification_id, validation_flag, touched, from_time, to_time,
                    import_value, scaled_value, None
                ))

            if values:
                execute_values(tgt, """
                    INSERT INTO observations
                    (id, sampling_point_id, value,
                     observationverification_id, observationvalidity_id, touched, from_time, to_time,
                     import_value, scaled_value, meta)
                    VALUES %s
                    ON CONFLICT (id) DO NOTHING
                """, values, page_size=len(values))

            last_id = rows[-1][0]
            migrated += len(values)
            log(f"   ... {migrated:,} / {total:,} ({100*migrated/total:.1f}%)")
        
        # Reset sequence
        tgt.execute("SELECT setval('observations_id_seq', (SELECT MAX(id) FROM observations))")
        
        self.stats['observations'] = migrated
        if skipped:
            log(f"   ✓ {migrated:,} rows ({skipped:,} duplicate row(s) dropped)")
        else:
            log(f"   ✓ {migrated:,} rows")
        
        src.close()
        tgt.close()
    
    def migrate_scaling_points(self):
        """Migrate scaling_points table"""
        log("\n📋 Migrating scaling_points...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        src.execute("SELECT * FROM scaling_points")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            tgt.execute(f"""
                INSERT INTO scaling_points ({', '.join(cols)})
                VALUES ({', '.join(['%s'] * len(cols))})
                ON CONFLICT (id) DO NOTHING
            """, row)
        
        if rows:
            tgt.execute("SELECT setval('scaling_points_id_seq', (SELECT MAX(id) FROM scaling_points))")
        
        self.stats['scaling_points'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_calculated_series(self):
        """Migrate calculated_series table"""
        log("\n📋 Migrating calculated_series...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        src.execute("SELECT * FROM calculated_series")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            tgt.execute(f"""
                INSERT INTO calculated_series ({', '.join(cols)})
                VALUES ({', '.join(['%s'] * len(cols))})
                ON CONFLICT (id) DO NOTHING
            """, row)
        
        self.stats['calculated_series'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_converted_series(self):
        """Migrate converted_series table with FK transformations"""
        log("\n📋 Migrating converted_series...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        src.execute("SELECT * FROM converted_series")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            row_dict = dict(zip(cols, row))
            
            # Transform URI FKs to notation
            source = extract_notation_from_uri(row_dict.get('source'))
            target = extract_notation_from_uri(row_dict.get('target'))
            
            tgt.execute("""
                INSERT INTO converted_series 
                (id, sampling_point_id, source, target, factor, createdby)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                row_dict['id'],
                row_dict['sampling_point_id'],
                source,
                target,
                row_dict['factor'],
                row_dict['createdby'],
            ))
        
        self.stats['converted_series'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_autovalidated_series(self):
        """Migrate autovalidated_series with FK transformations"""
        log("\n📋 Migrating autovalidated_series...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        src.execute("SELECT * FROM autovalidated_series")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            row_dict = dict(zip(cols, row))
            
            # Pollutant: URI → numeric ID
            pollutant_id = extract_pollutant_id_from_uri(row_dict.get('pollutant'))
            
            if pollutant_id:
                tgt.execute("""
                    INSERT INTO autovalidated_series 
                    (id, pollutant_id, max, min, rep, enabled)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    row_dict['id'],
                    pollutant_id,
                    row_dict['max'],
                    row_dict['min'],
                    row_dict['rep'],
                    row_dict.get('enabled', True),
                ))
        
        self.stats['autovalidated_series'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_zones(self):
        """Migrate zones table (v4.4.0 simplified)"""
        log("\n📋 Migrating zones...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v3 source: id, code, name, geom, area, type
        # v4 target: id, zone_national_code, name, geom, zone_area, zone_category_id,
        #            zone_type_id -- code/area were renamed by migration 002 (ZGE_02, ZGE_09).
        src.execute("SELECT id, code, name, geom, area, type FROM zones")
        rows = src.fetchall()

        for row in rows:
            id_val, code, name, geom, area, type_uri = row
            zone_type_id = extract_notation_from_uri(type_uri)

            tgt.execute("""
                INSERT INTO zones (id, zone_national_code, name, geom, zone_area,
                                   zone_category_id, zone_type_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (id_val, code, name, geom, area, None, zone_type_id))
        
        self.stats['zones'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_assessment_tables(self):
        """Migrate assessment-related tables (v4.4.0)"""
        log("\n📋 Migrating assessment tables...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # assessment_regimes (renamed from assessmentregimes)
        src.execute("SELECT * FROM assessmentregimes")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            row_dict = dict(zip(cols, row))
            
            pollutant_id = extract_pollutant_id_from_uri(row_dict.get('pollutant'))
            protection_target_id = extract_notation_from_uri(row_dict.get('protectiontarget'))
            reporting_metric_id = extract_notation_from_uri(row_dict.get('reportingmetric'))
            threshold_id = extract_notation_from_uri(row_dict.get('assessmentthresholdexceedance'))
            # objecttype -> objective_type_id (v4.4.0)
            objective_type_id = extract_notation_from_uri(row_dict.get('objecttype'))
            
            if pollutant_id:
                # Migration 002 renamed four of these: fixed_spo_reduction ->
                # fixed_measurement_reduction (ARZ_14), resident_population[_year] ->
                # zone_resident_population[_year] (ARZ_12/13), classification_report_id ->
                # classification_document_id (ARZ_19).
                tgt.execute("""
                    INSERT INTO assessment_regimes
                    (id, fixed_measurement_reduction, zone_resident_population_year,
                     zone_resident_population, classification_year, classification_document_id,
                     assessment_threshold_exceedance_id, pollutant_id, protection_target_id,
                     objective_type_id, reporting_metric_id, zone_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    row_dict['id'],
                    row_dict.get('include', True),  # Map include -> fixed_spo_reduction
                    row_dict.get('thresholdclassificationyear'),  # resident_population_year
                    None,  # resident_population
                    row_dict.get('thresholdclassificationyear'),  # classification_year
                    row_dict.get('thresholdclassificationreport'),  # classification_report_id
                    threshold_id,
                    pollutant_id,
                    protection_target_id,
                    objective_type_id,
                    reporting_metric_id,
                    row_dict.get('zoneid'),
                ))
        
        self.stats['assessment_regimes'] = len(rows)
        log(f"   ✓ assessment_regimes: {len(rows)} rows")
        
        # assessmentdata
        src.execute("SELECT * FROM assessmentdata")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            row_dict = dict(zip(cols, row))
            assesstype = extract_notation_from_uri(row_dict.get('assessmenttype'))
            
            # Since 4.502.24 assessmentlocal_id is generated from sampling_point_id
            # and model_id, so it cannot be written directly -- and the v3 column held
            # either kind. The MOD_/OBE_ prefix is mandatory on models.id (AQR3 MOE_02,
            # enforced by models_id_prefix), so it is what tells the two apart.
            local_id = row_dict['assessmentlocal_id']
            is_model = str(local_id or '').startswith(('MOD_', 'OBE_'))

            tgt.execute("""
                INSERT INTO assessmentdata
                (id, assessment_regime_id, sampling_point_id, model_id, assessmenttype,
                 assessmentmethodedescription)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                row_dict['id'],
                row_dict['assessmentregime_id'],
                None if is_model else local_id,
                local_id if is_model else None,
                assesstype,
                row_dict.get('assessmentmethodedescription'),
            ))
        
        self.stats['assessmentdata'] = len(rows)
        log(f"   ✓ assessmentdata: {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_supporting_tables(self):
        """Migrate directives, statistics, aqi tables"""
        log("\n📋 Migrating supporting tables...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # directives -- absent entirely from older v3 deployments (Andorra has none)
        if not self.source_has_table('directives'):
            log("   ⚠ directives: no such table in the v3 source - skipped")
            self.stats['directives'] = 0
        else:
            self._migrate_directives(src, tgt)

        self._migrate_statistics(src, tgt)
        self._migrate_aqi(src, tgt)

        src.close()
        tgt.close()

    def _migrate_directives(self, src, tgt):
        src.execute("SELECT * FROM directives")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            row_dict = dict(zip(cols, row))
            pollutant_id = extract_pollutant_id_from_uri(row_dict.get('pollutant_uri'))
            
            if pollutant_id:
                tgt.execute("""
                    INSERT INTO directives 
                    (pollutant_id, pollutant, mean_type, limitvalue_type, valid_from_year,
                     value, count, vegetaion_value, eco_value, reportingmetric, objectivetype)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    pollutant_id,
                    row_dict['pollutant'],
                    row_dict['mean_type'],
                    row_dict['limitvalue_type'],
                    row_dict['valid_from_year'],
                    row_dict.get('value'),
                    row_dict.get('count'),
                    row_dict.get('vegetaion_value'),
                    row_dict.get('eco_value'),
                    row_dict.get('reportingmetric'),
                    row_dict.get('objectivetype'),
                ))
        
        self.stats['directives'] = len(rows)
        log(f"   ✓ directives: {len(rows)} rows")

    def _migrate_statistics(self, src, tgt):
        if not self.source_has_table('statistics'):
            log("   ⚠ statistics: no such table in the v3 source - skipped")
            self.stats['statistics'] = 0
            return
        src.execute("SELECT * FROM statistics")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            row_dict = dict(zip(cols, row))
            pollutant_id = extract_pollutant_id_from_uri(row_dict.get('pollutant_uri'))
            agg_process = extract_notation_from_uri(row_dict.get('aggregation_process_id'))
            
            if pollutant_id and agg_process:
                tgt.execute("""
                    INSERT INTO statistics 
                    (pollutant_id, aggregation_process_id, directive_2008_50, directive_2024_2881)
                    VALUES (%s, %s, %s, %s)
                """, (
                    pollutant_id,
                    agg_process,
                    row_dict.get('directive_2008_50', False),
                    row_dict.get('directive_2024_2881', False),
                ))
        
        self.stats['statistics'] = len(rows)
        log(f"   ✓ statistics: {len(rows)} rows")

    def _migrate_aqi(self, src, tgt):
        if not self.source_has_table('aqi'):
            log("   ⚠ aqi: no such table in the v3 source - skipped")
            self.stats['aqi'] = 0
            return
        src.execute("SELECT * FROM aqi")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            row_dict = dict(zip(cols, row))
            pollutant_id = extract_pollutant_id_from_uri(row_dict.get('pollutant_uri'))
            timestep = extract_notation_from_uri(row_dict.get('timestep'))
            
            if pollutant_id and timestep:
                tgt.execute("""
                    INSERT INTO aqi 
                    (calculation_type, level, description, color, range, pollutant_id, timestep)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    row_dict['calculation_type'],
                    row_dict['level'],
                    row_dict['description'],
                    row_dict['color'],
                    row_dict['range'],
                    pollutant_id,
                    timestep,
                ))
        
        self.stats['aqi'] = len(rows)
        log(f"   ✓ aqi: {len(rows)} rows")

    def migrate_notifications(self):
        """Migrate notification tables"""
        log("\n📋 Migrating notifications...")
        
        import json
        from psycopg2.extras import Json
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # notifications
        src.execute("SELECT * FROM notifications")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        
        for row in rows:
            tgt.execute(f"""
                INSERT INTO notifications ({', '.join(cols)})
                VALUES ({', '.join(['%s'] * len(cols))})
                ON CONFLICT (name) DO NOTHING
            """, row)
        
        self.stats['notifications'] = len(rows)
        log(f"   ✓ notifications: {len(rows)} rows")
        
        # notifications_runs - has JSONB column 'details'
        src.execute("SELECT * FROM notifications_runs")
        rows = src.fetchall()
        cols = [desc[0] for desc in src.description]
        details_idx = cols.index('details') if 'details' in cols else -1
        
        for row in rows:
            # Convert dict back to JSON for JSONB column
            row_list = list(row)
            if details_idx >= 0 and row_list[details_idx] is not None:
                if isinstance(row_list[details_idx], dict):
                    row_list[details_idx] = Json(row_list[details_idx])
            tgt.execute(f"""
                INSERT INTO notifications_runs ({', '.join(cols)})
                VALUES ({', '.join(['%s'] * len(cols))})
                ON CONFLICT (id) DO NOTHING
            """, row_list)
        
        if rows:
            tgt.execute("SELECT setval('notifications_runs_id_seq', (SELECT MAX(id) FROM notifications_runs))")
        
        self.stats['notifications_runs'] = len(rows)
        log(f"   ✓ notifications_runs: {len(rows)} rows")
        
        # notifications_samplingpoints
        src.execute("SELECT * FROM notifications_samplingpoints")
        rows = src.fetchall()
        
        for row in rows:
            tgt.execute("""
                INSERT INTO notifications_samplingpoints (notification_id, sampling_point_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, row)
        
        self.stats['notifications_samplingpoints'] = len(rows)
        log(f"   ✓ notifications_samplingpoints: {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def print_summary(self):
        """Print migration summary"""
        log("\n" + "=" * 60)
        log("MIGRATION SUMMARY")
        log("=" * 60)
        
        total = 0
        for table, count in sorted(self.stats.items()):
            log(f"  {table}: {count:,} rows")
            total += count
        
        log("-" * 60)
        log(f"  TOTAL: {total:,} rows migrated")
        log("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Migrate Raven v3 to v4')
    parser.add_argument('--dry-run', action='store_true', help='Run without committing changes')
    parser.add_argument('--batch-size', type=int, default=10000, help='Batch size for observations')
    parser.add_argument('--country-code', metavar='XX',
                        help='ISO country code for settings.country_code_id. Only needed when '
                             'the v3 source has no settings.country_code and its station EoI '
                             'codes do not agree on one country.')
    parser.add_argument('--recreate-schema', action='store_true', help='Drop and recreate schema')
    parser.add_argument('--init-only', action='store_true',
                        help='Create schema and populate EEA lookup tables only (no v3 source needed)')
    parser.add_argument('--remediate-only', action='store_true',
                        help='Derive the AQR3 v5.02 columns that can be computed from data an '
                             'existing v4 database already holds (observations.data_capture, '
                             'pollution_level_adjustment, srs_inline grid snapping) and change '
                             'nothing else. No v3 source needed; safe to re-run.')
    args = parser.parse_args()

    if args.init_only and args.remediate_only:
        parser.error('--init-only and --remediate-only are mutually exclusive: one creates an '
                     'empty database, the other only rewrites rows in a populated one.')

    migration = Migration(dry_run=args.dry_run, batch_size=args.batch_size,
                          recreate_schema=args.recreate_schema, init_only=args.init_only,
                          remediate_only=args.remediate_only, country_code=args.country_code)
    migration.run()


if __name__ == '__main__':
    main()
