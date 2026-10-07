#!/usr/bin/env python3
"""Clear station EoI codes that EIONET never assigned.

    python sql/cleanup_fabricated_eoi.py --db-uri <uri>            # dry run, default
    python sql/cleanup_fabricated_eoi.py --db-uri <uri> --apply

AQR3 STA_02 StationEoICode is assigned by EIONET and is the key the whole
submission is organised by. Until 4.502.22 Raven's write path required one on
every station -- `StationModel.station_eoi_code: str`, `required: true` in
stations/pageOptions.js -- even though migration 013 had made the column nullable
precisely so a site outside the EEA reporting obligation could be stored without
one. The predictable result is invented identifiers: on the development database
66 of 174 stations carry codes of the form `NILU-1002 Gvarv`, 63 of them in a
network called "NILU Internal Monitoring". Every one of them passes the
reportability test and would be submitted to Reportnet 3 under a code that
identifies nothing.

Deliberately not a migration. Clearing an identifier is not reversible, the rows
are one deployment's data accident rather than a schema fact, and a migration
runs unattended on every pod boot. This runs when someone decides to run it,
after reading what it proposes to change. The same reasoning as
nilu-private-migration/cleanup_invented_vocabulary.py, which removed the invented
`eea_times '5min'` row and the 999xxx pollutants.

What it changes, per affected station:

    station_eoi_code  -> NULL      the code was never an EoI code
    report_to_eea     -> false     and the site is not reported

and for that station's sampling points:

    sampling_point_reference_id -> NULL

because AQR3 SPO_03 is `SPOref_<StationEoICode>_<PollutantId>_<idx>` and there is
no longer an EoI code to build it from. Migration 013 says the same thing.

Everything it clears is copied into `stations_fabricated_eoi` first, with the
original code and the time it was archived, so the change can be undone by hand.
"""
import argparse
import re
import sys

import psycopg2
import psycopg2.extras

# The EIONET form: a two-letter country code, digits, and a letter for the
# station type -- NO0001R, DU0001. Written as a shape rather than as a `NILU-%`
# pattern so the script is not specific to one deployment's habits.
EIONET_SHAPE = r'^[A-Z]{2}[0-9]+[A-Z]$'

SELECT_FABRICATED = f"""
    SELECT s.id, s.station_eoi_code, s.name, s.network_id, n.name AS network,
           (SELECT count(*) FROM sampling_points sp WHERE sp.station_id = s.id) AS sampling_points
      FROM stations s
      LEFT JOIN networks n ON n.id = s.network_id
     WHERE s.station_eoi_code IS NOT NULL
       AND s.station_eoi_code !~ '{EIONET_SHAPE}'
     ORDER BY s.station_eoi_code
"""


def _refuse_production(uri):
    if re.search(r'prod|ad_aqraven_eu', uri, re.I):
        raise SystemExit(f'Refusing to run against what looks like production: '
                         f'{re.sub(r"//[^@]*@", "//", uri)}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db-uri', required=True)
    ap.add_argument('--apply', action='store_true',
                    help='make the changes; without it this only reports them')
    args = ap.parse_args()

    _refuse_production(args.db_uri)

    connection = psycopg2.connect(args.db_uri)
    connection.autocommit = False
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Both migrations have to be in place first, or the work below either cannot be
    # done or cannot be recorded. Checked up front, because the failure without this
    # is a raw NotNullViolation naming a row rather than a missing migration.
    cursor.execute("""
        SELECT (SELECT is_nullable = 'YES' FROM information_schema.columns
                 WHERE table_name = 'stations' AND column_name = 'station_eoi_code')
                    AS eoi_nullable,
               to_regclass('public.stations') IS NOT NULL
               AND EXISTS (SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'stations' AND column_name = 'report_to_eea')
                    AS has_scope_flag
    """)
    state = cursor.fetchone()
    if not state['eoi_nullable']:
        raise SystemExit('stations.station_eoi_code is still NOT NULL: apply migration 013 '
                         'before clearing codes, or there is nowhere for them to go.')
    if not state['has_scope_flag']:
        raise SystemExit('stations.report_to_eea does not exist: apply migration 022 first, '
                         'so a cleared station can be recorded as not reported.')

    cursor.execute(SELECT_FABRICATED)
    rows = cursor.fetchall()
    if not rows:
        print('No station carries an EoI code outside the EIONET form. Nothing to do.')
        return 0

    print(f'{len(rows)} station(s) carry an EoI code that is not of the form '
          f'{EIONET_SHAPE}:\n')
    print(f'  {"code":24} {"station":28} {"network":22} sampling points')
    for row in rows:
        print(f'  {row["station_eoi_code"]:24} {(row["name"] or "")[:26]:28} '
              f'{(row["network"] or row["network_id"] or "")[:20]:22} {row["sampling_points"]}')

    # A second, independent reading of the same set. If the shape rule and the
    # deployment's own naming disagree, the shape rule is picking up something
    # that was not part of this defect and a human should look before anything is
    # cleared.
    cursor.execute("SELECT count(*) FROM stations WHERE station_eoi_code LIKE 'NILU-%%'")
    nilu = cursor.fetchone()[0]
    if nilu and nilu != len(rows):
        print(f'\n  note: {nilu} station(s) match the NILU- naming but {len(rows)} fail the '
              f'EIONET shape. The two sets differ, so read the list above before applying.')

    if not args.apply:
        print('\nDry run. Nothing changed. Re-run with --apply to clear these.')
        return 0

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations_fabricated_eoi (
            station_id       varchar(100) not null,
            station_eoi_code varchar(20)  not null,
            station_name     varchar(255),
            network_id       varchar(100),
            archived_at      timestamptz  not null default now()
        )
    """)
    cursor.execute("""
        COMMENT ON TABLE stations_fabricated_eoi IS
            'EoI codes cleared by sql/cleanup_fabricated_eoi.py because they are not of '
            'the form EIONET assigns. The stations they belonged to were set '
            'report_to_eea = false at the same time. Kept so the change can be undone; '
            'drop this table once nobody needs it.'
    """)
    cursor.execute(f"""
        INSERT INTO stations_fabricated_eoi (station_id, station_eoi_code, station_name, network_id)
        SELECT s.id, s.station_eoi_code, s.name, s.network_id
          FROM stations s
         WHERE s.station_eoi_code IS NOT NULL
           AND s.station_eoi_code !~ '{EIONET_SHAPE}'
    """)
    archived = cursor.rowcount

    cursor.execute(f"""
        UPDATE sampling_points sp
           SET sampling_point_reference_id = NULL
          FROM stations s
         WHERE sp.station_id = s.id
           AND s.station_eoi_code IS NOT NULL
           AND s.station_eoi_code !~ '{EIONET_SHAPE}'
           AND sp.sampling_point_reference_id IS NOT NULL
    """)
    references = cursor.rowcount

    cursor.execute(f"""
        UPDATE stations
           SET station_eoi_code = NULL,
               report_to_eea    = false
         WHERE station_eoi_code IS NOT NULL
           AND station_eoi_code !~ '{EIONET_SHAPE}'
    """)
    cleared = cursor.rowcount

    connection.commit()
    print(f'\nArchived {archived} code(s) to stations_fabricated_eoi.')
    print(f'Cleared {cleared} station EoI code(s) and marked those stations not reported.')
    print(f'Cleared {references} sampling point reference id(s) built from them.')

    cursor.execute('SELECT count(*) FROM stations WHERE report_to_eea '
                   'AND station_eoi_code IS NOT NULL')
    print(f'{cursor.fetchone()[0]} station(s) remain in scope and reportable.')
    connection.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
