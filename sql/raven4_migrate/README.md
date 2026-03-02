# Raven v3 to v4 Migration Scripts

This folder contains scripts for migrating data from RAVEN v3 (ravendb) to RAVEN v4 (ravendb4).

## Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual database credentials:**
   ```bash
   # Update the password fields in .env
   SOURCE_DB_PASSWORD=your_actual_password
   TARGET_DB_PASSWORD=your_actual_password
   ```

3. **Install required Python packages:**
   ```bash
   pip install psycopg2-binary python-dotenv
   ```

## Scripts

### `analyze_v3.py`
Analyzes the Raven v3 database schema and data to help plan the migration.

**Usage:**
```bash
python analyze_v3.py
```

### `migrate_v3_to_v4.py`
Performs the actual data migration from v3 to v4.

**Usage:**
```bash
# Dry run (test without committing)
python migrate_v3_to_v4.py --dry-run

# Full migration with custom batch size
python migrate_v3_to_v4.py --batch-size=5000

# Full migration (default batch size 10000)
python migrate_v3_to_v4.py
```

## Security Notes

- **Never commit the `.env` file** - it contains sensitive database credentials
- The `.env` file is listed in `.gitignore` to prevent accidental commits
- Use `.env.example` as a template for other users/environments
- Keep database passwords secure and rotate them regularly

## Migration Process

1. Analyze the source database with `analyze_v3.py`
2. Review schema changes in `schema_v4.sql`
3. Test migration with `--dry-run` flag
4. Perform full migration when ready
5. Verify data integrity in target database
