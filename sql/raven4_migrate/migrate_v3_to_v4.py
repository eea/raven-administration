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

The migration runs in a single transaction - if any part fails, nothing is committed.
"""

import os
import sys
import argparse
import psycopg2
from psycopg2 import sql
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


def log(msg):
    """Print timestamped log message"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# Case mapping for values that differ between v3 URIs and v4 notations
# v3 URI suffix (lowercase) → v4 notation (camelCase)
CASE_MAPPINGS = {
    # measurementregime
    'continuousdatacollection': 'continuousDataCollection',
    'demanddriven': 'demandDriven',
    'onceoff': 'onceOff',
    'periodicdatacollection': 'periodicDataCollection',
    # measurement methods (URI suffix uses underscore, notation uses plus)
    'nephelometry_beta': 'nephelometry+beta',
    # media - already lowercase in v4
    # processtype - already lowercase in v4
    # resultnature - already lowercase in v4
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
    
    def __init__(self, dry_run=False, batch_size=10000, recreate_schema=False):
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.recreate_schema = recreate_schema
        self.source_conn = None
        self.target_conn = None
        self.stats = {}
    
    def connect(self):
        """Connect to both databases"""
        log("Connecting to source database (ravendb)...")
        self.source_conn = psycopg2.connect(**SOURCE_DB)
        self.source_conn.set_session(readonly=True)
        
        log("Connecting to target database (ravendb4)...")
        self.target_conn = psycopg2.connect(**TARGET_DB)
        # Don't autocommit - we want transaction control
        self.target_conn.autocommit = False
        
        log("✓ Connected to both databases")
    
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
        
        # Find schema file relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_file = os.path.join(script_dir, '..', '..', '..', '..', 'raven-rn3-db', 'schema_v4.sql')
        
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
        
        # Import and run the populate script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        populate_script = os.path.join(script_dir, '..', '..', '..', '..', 'raven-rn3-db', 'populate_lookups_v4_2.py')
        
        if not os.path.exists(populate_script):
            raise FileNotFoundError(f"Populate script not found: {populate_script}")
        
        # Run populate script in subprocess
        import subprocess
        result = subprocess.run(
            [sys.executable, populate_script],
            capture_output=True, text=True, cwd=os.path.dirname(populate_script)
        )
        
        if result.returncode != 0:
            log(f"   ⚠ Populate script output: {result.stderr}")
            raise RuntimeError(f"Populate script failed: {result.stderr}")
        
        log("   ✓ Lookup tables populated")
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
            'assessmentdata', 'assessment_regimes', 'assessmentregime_zones', 'zones',
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
            log("RAVEN v3 → v4 DATA MIGRATION")
            log(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
            log(f"Batch size: {self.batch_size:,}")
            log("=" * 60)
            
            # Setup: ensure schema and lookups exist
            self.setup_schema()
            self.populate_lookups()
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
        
        src.execute("SELECT country_code FROM settings LIMIT 1")
        row = src.fetchone()
        if row:
            # v4.4.0 settings: just country_code_id, timezone_id
            country_code = row[0]
            tgt.execute("""
                INSERT INTO settings (country_code_id, timezone_id)
                VALUES (%s, %s)
            """, (country_code, None))
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
        # v4: id, person_name, email, organisation_name, organisation_url, organisation_address, instance_id, object_id, status_id
        # DEFAULTS: instance_id='network', object_id='AQD', status_id='active' (for RN3 required fields)
        src.execute("SELECT id, name, organisation, email, website, address FROM responsible_authorities")
        rows = src.fetchall()
        
        for row in rows:
            id_val, name, organisation, email, website, address = row
            tgt.execute("""
                INSERT INTO authorities 
                (id, person_name, email, organisation_name, organisation_url, organisation_address,
                 instance_id, object_id, status_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (id_val, name, email, organisation, website, address,
                  'network', 'AQD', 'active'))  # RN3 required field defaults
        
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
        # v4.8.0: id, name, administration_level_id, timezone_id (report_id moved to stations.document_id)
        src.execute("SELECT id, name, organisational, aggregation_timezone FROM networks")
        rows = src.fetchall()
        
        for row in rows:
            id_val, name, organisational, aggregation_timezone = row
            # Transform URI FK to notation
            admin_level = extract_notation_from_uri(organisational)
            # Extract timezone notation from URI (e.g., 'http://.../timezone/UTC+02' -> 'UTC+02')
            timezone_id = extract_notation_from_uri(aggregation_timezone) if aggregation_timezone else None
            
            tgt.execute("""
                INSERT INTO networks (id, name, administration_level_id, timezone_id)
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
        """Migrate stations (v4.8.0: id, eoi_code, name, national_code, lat, lon, alt, supersite, area_classification_id, document_id, network_id)"""
        log("\n📋 Migrating stations...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v3: id, name, begin_position, end_position, network_id, city, national_station_code,
        #     media_monitored, mobile, measurement_regime, area_classification, distance_junction,
        #     traffic_volume, heavy_duty_fraction, street_width, height_facades, geom, municipality,
        #     eoi_code, city_code
        # v4.8.0: id, eoi_code, name, national_code, lat, lon, alt, supersite, area_classification_id, document_id, network_id
        # Note: document_id will be NULL - needs to be populated separately via documents table
        src.execute("""
            SELECT id, eoi_code, name, national_station_code, 
                   ST_Y(geom) as latitude, ST_X(geom) as longitude, ST_Z(geom) as altitude,
                   area_classification, network_id
            FROM stations
        """)
        rows = src.fetchall()
        
        for row in rows:
            id_val, eoi, name, national_code, lat, lon, alt, area_class_uri, network_id = row
            # Transform URI FK to notation
            area_classification_id = extract_notation_from_uri(area_class_uri)
            
            tgt.execute("""
                INSERT INTO stations (id, eoi_code, name, national_code, latitude, longitude, altitude, 
                                      supersite, area_classification_id, document_id, network_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (id_val, eoi, name, national_code, lat, lon, alt, 
                  False, area_classification_id, None, network_id))  # document_id = NULL
        
        self.stats['stations'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_sampling_points_with_samples(self):
        """Migrate sampling_points (v4.4.0 simplified)"""
        log("\n📋 Migrating sampling_points...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v4.4.0: id, sampling_point_ref, inlet_height, building_distance, kerb_distance, emission_source_distance,
        #         logger_id, private, use_in_public_api, from_time, to_time,
        #         pollutant_id, time_resolution_id, unit_id, spo_category_id, station_id
        # Need station.eoi_code for generating sampling_point_ref
        src.execute("""
            SELECT DISTINCT ON (sp.id)
                sp.id,
                s.inlet_height,
                s.building_distance,
                s.kerb_distance,
                sp.logger_id,
                sp.private,
                sp.use_in_public_api,
                sp.from_time,
                sp.to_time,
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
        
        for row in rows:
            (id_val, inlet_height, building_distance, kerb_distance, logger_id, 
             private, use_in_public_api, from_time, to_time, 
             pollutant_uri, timestep_uri, concentration_uri, station_classification_uri, station_id, eoi_code) = row
            
            # Transform URIs
            pollutant_id = extract_pollutant_id_from_uri(pollutant_uri)
            time_resolution_id = extract_notation_from_uri(timestep_uri)
            unit_id = extract_concentration_from_uri(concentration_uri)
            # station_classification URI -> spo_category_id (extract last part, lowercase)
            spo_category_id = extract_notation_from_uri(station_classification_uri).lower() if station_classification_uri else None
            
            # Generate sampling_point_ref: SPOref_[EOI]_[POLLUTANT_ID]_[N]
            # e.g., SPOref_NO0042A_00005_1
            if eoi_code and pollutant_id:
                ref_key = f"{eoi_code}_{pollutant_id:05d}"
                spo_ref_counters[ref_key] = spo_ref_counters.get(ref_key, 0) + 1
                sampling_point_ref = f"SPOref_{eoi_code}_{pollutant_id:05d}_{spo_ref_counters[ref_key]}"
                # Truncate to 32 chars if needed
                sampling_point_ref = sampling_point_ref[:32]
            else:
                sampling_point_ref = None
            
            tgt.execute("""
                INSERT INTO sampling_points 
                (id, sampling_point_ref, inlet_height, building_distance, kerb_distance, emission_source_distance,
                 logger_id, private, use_in_public_api, from_time, to_time,
                 pollutant_id, time_resolution_id, unit_id, spo_category_id, station_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                id_val, sampling_point_ref, inlet_height, building_distance, kerb_distance, None,
                logger_id, private or False, use_in_public_api or False, from_time, to_time,
                pollutant_id, time_resolution_id, unit_id, spo_category_id, station_id
            ))
        
        self.stats['sampling_points'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
    
    def migrate_processes_with_observing_capabilities(self):
        """Migrate processes (v4.8.0: with 3 document references)"""
        log("\n📋 Migrating processes...")
        
        src = self.source_conn.cursor()
        tgt = self.target_conn.cursor()
        
        # v4.8.0: id, activity_begin, activity_end, 
        #         data_quality_document_id, equivalence_demonstration_document_id, process_document_id,
        #         measurement_type_id, method_id, equipment_id, analytical_technique_id,
        #         equivalence_demonstrated_id, sampling_point_id
        # Note: document_ids will be NULL - needs to be populated separately via documents table
        src.execute("""
            SELECT DISTINCT ON (p.id)
                p.id,
                oc.begin_position as activity_begin,
                oc.end_position as activity_end,
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
            (id_val, activity_begin, activity_end, meas_type_uri, meas_method_uri,
             meas_equip_uri, analytical_tech, equiv_demo_uri, sampling_point_id) = row
            
            # Transform URI FKs to notation
            measurement_type_id = extract_notation_from_uri(meas_type_uri)
            method_id = extract_notation_from_uri(meas_method_uri)
            equipment_id = extract_notation_from_uri(meas_equip_uri)
            equivalence_demonstrated_id = extract_notation_from_uri(equiv_demo_uri)
            # analytical_technique_id - keep as-is for now (text field in v3)
            
            tgt.execute("""
                INSERT INTO processes 
                (id, activity_begin, activity_end, 
                 data_quality_document_id, equivalence_demonstration_document_id, process_document_id,
                 measurement_type_id, method_id, equipment_id, analytical_technique_id,
                 equivalence_demonstrated_id, sampling_point_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                id_val, activity_begin, activity_end, 
                None, None, None,  # 3 document_ids = NULL
                measurement_type_id, method_id, equipment_id, None,  # analytical_technique_id
                equivalence_demonstrated_id, sampling_point_id
            ))
        
        self.stats['processes'] = len(rows)
        log(f"   ✓ {len(rows)} rows")
        
        src.close()
        tgt.close()
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
        offset = 0
        migrated = 0
        
        while offset < total:
            src.execute(f"""
                SELECT id, sampling_point_id, value,
                       verification_flag, validation_flag, touched, from_time, to_time,
                       import_value, scaled_value
                FROM observations
                ORDER BY id
                LIMIT {self.batch_size} OFFSET {offset}
            """)
            rows = src.fetchall()
            if not rows:
                break
            
            for row in rows:
                (id_val, sp_id, value,
                 verification_flag, validation_flag, touched, from_time, to_time,
                 import_value, scaled_value) = row
                
                # Map old verification_flag to EEA observationverification_id
                # 0 -> 3 (not verified), 1 -> 1 (verified)
                observationverification_id = 1 if verification_flag == 1 else 3
                
                tgt.execute("""
                    INSERT INTO observations 
                    (id, sampling_point_id, value,
                     observationverification_id, observationvalidity_id, touched, from_time, to_time,
                     import_value, scaled_value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    id_val, sp_id, value,
                    observationverification_id, validation_flag, touched, from_time, to_time,
                    import_value, scaled_value
                ))
            
            migrated += len(rows)
            offset += self.batch_size
            log(f"   ... {migrated:,} / {total:,} ({100*migrated/total:.1f}%)")
        
        # Reset sequence
        tgt.execute("SELECT setval('observations_id_seq', (SELECT MAX(id) FROM observations))")
        
        self.stats['observations'] = migrated
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
        
        # v4.4.0: id, code, name, geom, area, zone_category_id, zone_type_id
        src.execute("SELECT id, code, name, geom, area, type FROM zones")
        rows = src.fetchall()
        
        for row in rows:
            id_val, code, name, geom, area, type_uri = row
            zone_type_id = extract_notation_from_uri(type_uri)
            
            tgt.execute("""
                INSERT INTO zones (id, code, name, geom, area, zone_category_id, zone_type_id)
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
                tgt.execute("""
                    INSERT INTO assessment_regimes 
                    (id, fixed_spo_reduction, resident_population_year, resident_population,
                     classification_year, classification_report_id,
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
            
            tgt.execute("""
                INSERT INTO assessmentdata 
                (id, assessment_regime_id, assessmentlocal_id, assessmenttype, assessmentmethodedescription)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                row_dict['id'],
                row_dict['assessmentregime_id'],
                row_dict['assessmentlocal_id'],
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
        
        # directives
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
        
        # statistics
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
        
        # aqi
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
        
        src.close()
        tgt.close()
    
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
    parser.add_argument('--recreate-schema', action='store_true', help='Drop and recreate schema')
    args = parser.parse_args()
    
    migration = Migration(dry_run=args.dry_run, batch_size=args.batch_size, recreate_schema=args.recreate_schema)
    migration.run()


if __name__ == '__main__':
    main()
