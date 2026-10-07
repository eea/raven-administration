"""What is left to do before this database can be submitted to Reportnet 3.

One catalogue, two readers:

  * the migration wizard's verifier runs it once, straight after converting a v3
    database, and writes the result into the run report;
  * Raven v4 serves it live from `/api/management/upgrade/tasks`, so an item
    disappears when the operator actually completes it rather than lingering as a
    snapshot of migration day.

Every check is a query against the database as it is now. Nothing here reads
migration state, which is what lets the same code answer both questions.

Editorial rule, inherited from `views/management/samplingpoints/help.js`: cite the
AQR3 attribute, then say what it means for this database. A task that only names a
problem is not a task -- `where` and `how` are mandatory, because the operator's
next question is always "so where do I go and what do I type".
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Callable, Optional

# Severity drives ordering and colour, nothing else.
BLOCKER = 'blocker'          # Reportnet 3 rejects the submission until this is fixed
RECOMMENDED = 'recommended'  # the submission is accepted but thinner than it should be
INFO = 'info'                # done for you, or expected -- shown so it is not a surprise

_ORDER = {BLOCKER: 0, RECOMMENDED: 1, INFO: 2}


@dataclass
class Task:
    id: str
    title: str
    why: str
    where: str
    how: list[str]
    severity: str = RECOMMENDED
    count: int = 0
    examples: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def _scalar(cursor, sql, params=None, default=0):
    """Query that tolerates a table the schema has not got. Returns `default`.

    Callers run inside a read-only request; a missing relation aborts the
    transaction, so it has to be rolled back before the next check runs.
    """
    try:
        # Not `params or ()`: psycopg2 only skips %-interpolation when the second
        # argument is absent, so an empty tuple makes a bare `%` in a LIKE pattern
        # an "unsupported format character" -- which this except would then swallow,
        # silently turning a real finding into zero.
        cursor.execute(sql, params) if params else cursor.execute(sql)
        row = cursor.fetchone()
        if row is None:
            return default
        return list(row.values())[0] if hasattr(row, 'values') else row[0]
    except Exception:
        try:
            cursor.connection.rollback()
        except Exception:
            pass
        return default


def _column(cursor, sql, params=None, limit=5):
    try:
        cursor.execute(sql, params) if params else cursor.execute(sql)
        rows = cursor.fetchall() or []
        out = []
        for r in rows[:limit]:
            out.append(list(r.values())[0] if hasattr(r, 'values') else r[0])
        return out
    except Exception:
        try:
            cursor.connection.rollback()
        except Exception:
            pass
        return []


# ---------------------------------------------------------------- checks ----
# Each returns a Task when there is something to say, else None.

def _check_regime_identifiers(cursor) -> Optional[Task]:
    """ARZ_02. A regime whose id predates the mandatory format cannot be edited
    at all in Raven v4 -- the update route validates the id before every save, so
    the whole row is refused, not just the id."""
    n = _scalar(cursor, r"select count(*) from assessment_regimes where id not like 'ARE\_%'")
    if not n:
        return None
    return Task(
        id='regime-identifiers',
        title=f'{n} assessment regime identifier(s) are not in the required format',
        why='AQR3 ARZ_02 requires AssessmentRegimeId to start with "ARE_" and carry seven '
            'segments. Reportnet 3 rejects the AssessmentRegimeZone table outright, and '
            'Raven refuses to save any change to these rows until the identifier is '
            'corrected — including changes to completely unrelated fields.',
        where='Assessment Regime Zones',
        how=['Open Assessment Regime Zones.',
             'Each affected regime offers "Repair identifier", which rebuilds the id from '
             'the regime\'s own zone, pollutant, objective, target, metric and year.',
             'A regime missing any of those cannot be repaired until you fill it in — the '
             'identifier is built from them.'],
        severity=BLOCKER, count=n,
        examples=_column(cursor, r"select id from assessment_regimes "
                                 r"where id not like 'ARE\_%' order by id"))


def _check_regimes_without_zone(cursor) -> Optional[Task]:
    n = _scalar(cursor, 'select count(*) from assessment_regimes where zone_id is null')
    if not n:
        return None
    return Task(
        id='regime-no-zone',
        title=f'{n} assessment regime(s) have no zone',
        why='ARZ_03 ZoneId is mandatory, and the AssessmentRegimeId is built from it. '
            'Without a zone the regime cannot be reported and its identifier cannot be '
            'repaired, so it is stuck until someone says which zone it belongs to.',
        where='Assessment Regime Zones',
        how=['Open Assessment Regime Zones and find the regimes listed below.',
             'Set the zone. The identifier often names it already — a regime called '
             '"…MT0001…" almost certainly belongs to zone ZON-MT0001, but only you can '
             'confirm that.',
             'Then use "Repair identifier" on the same row.'],
        severity=BLOCKER, count=n,
        examples=_column(cursor, 'select id from assessment_regimes '
                                 'where zone_id is null order by id'))


def _check_dangling_classification_document(cursor) -> Optional[Task]:
    """ARZ_19. There is no foreign key behind this column and nothing joins DOC to
    ARZ at export time, so an unresolvable reference ships silently."""
    n = _scalar(cursor, """
        select count(*) from assessment_regimes ar
         where ar.classification_document_id is not null
           and ar.classification_document_id <> ''
           and not exists (select 1 from documents d where d.id = ar.classification_document_id)
    """)
    if not n:
        return None
    return Task(
        id='classification-document-missing',
        title=f'{n} assessment regime(s) point at a document that does not exist',
        why='ARZ_19 ClassificationDocumentId must match a DocumentId in the Documentation '
            'table. Nothing in Raven enforces that, so the reference travels into the '
            'submission and Reportnet 3 rejects it there instead.',
        where='Documents',
        how=['Open Documents and add one row per reference listed below.',
             'Set Id to exactly the value shown — it is what the regimes already point at.',
             'Set Data Table to "AssessmentRegimeZone (ARZ)" so it appears for assessment '
             'regimes.',
             'Fill in the attachment filename or the original URL.'],
        severity=BLOCKER, count=n,
        examples=_column(cursor, """
            select distinct ar.classification_document_id from assessment_regimes ar
             where ar.classification_document_id is not null
               and ar.classification_document_id <> ''
               and not exists (select 1 from documents d
                                where d.id = ar.classification_document_id)
        """))


def _check_settings(cursor) -> Optional[Task]:
    row = None
    try:
        cursor.execute('select country_code_id, timezone_id from settings limit 1')
        row = cursor.fetchone()
    except Exception:
        try:
            cursor.connection.rollback()
        except Exception:
            pass
    if row is None:
        return None
    country = row['country_code_id'] if hasattr(row, 'keys') else row[0]
    tz = row['timezone_id'] if hasattr(row, 'keys') else row[1]
    missing = [n for n, v in (('country', country), ('reporting timezone', tz)) if not v]
    if not missing:
        return None
    return Task(
        id='settings-incomplete',
        title=f'The {" and the ".join(missing)} is not set',
        why='Every exported datetime carries the reporting timezone offset, and every '
            'table is keyed on the country code. Without them Reportnet 3 rejects the '
            'whole submission rather than individual rows.',
        where='Settings',
        how=['Open Settings and choose the missing value.',
             'The timezone is the one your networks aggregate to, not the one you live in.'],
        severity=BLOCKER, count=len(missing))


def _check_stations_without_eoi(cursor) -> Optional[Task]:
    # Same rule the migration's pre-flight uses: a one-character code is not a
    # country prefix plus a station number, so it is as unusable as a blank one.
    n = _scalar(cursor, "select count(*) from stations where station_eoi_code is null "
                        "or length(station_eoi_code) < 2")
    if not n:
        return None
    return Task(
        id='stations-no-eoi',
        title=f'{n} station(s) have no EoI code',
        why='STA_02 StationEoICode is the station\'s identity in AQR3. A station without '
            'one cannot be exported at all, so everything measured at it disappears from '
            'the submission silently.',
        where='Stations',
        how=['Open Stations and fill in the EoI code for each one listed.',
             'If a station is genuinely not part of the EEA obligation, switch EEA '
             'Reporting off for it instead — then its absence is a decision, not a gap.'],
        severity=BLOCKER, count=n,
        examples=_column(cursor, "select id from stations where station_eoi_code is null "
                                 "or length(station_eoi_code) < 2 order by id"))


def _check_authorities_without_email(cursor) -> Optional[Task]:
    n = _scalar(cursor, "select count(*) from authorities where email is null or email = ''")
    if not n:
        return None
    return Task(
        id='authorities-no-email',
        title=f'{n} responsible authority/authorities have no e-mail address',
        why='AUT_04 Email is part of the Authority primary key, so a blank one is not an '
            'empty field — it is an unidentifiable row.',
        where='Authorities',
        how=['Open Authorities and add a contact address for each one listed.'],
        severity=BLOCKER, count=n,
        examples=_column(cursor, "select id from authorities "
                                 "where email is null or email = '' order by id"))


def _check_sampling_points_without_regime(cursor) -> Optional[Task]:
    """Not a conformance error — a thin submission. These series are measured and
    reported, but nothing says what they are assessed against."""
    n = _scalar(cursor, """
        select count(*) from sampling_points sp
         where sp.pollutant_id is not null
           and not exists (select 1 from assessmentdata ad
                            where ad.sampling_point_id = sp.id
                              and ad.assessment_regime_id is not null)
    """)
    if not n:
        return None
    return Task(
        id='sampling-points-no-regime',
        title=f'{n} sampling point(s) are not linked to any assessment regime',
        why='Compliance (CAM) is derived by matching a sampling point to a regime for its '
            'pollutant. These series are exported as measurements, but say nothing about '
            'whether a limit value was met — so the submission reports the air without '
            'assessing it.',
        where='Assessment Regime Zones → Assessment data',
        how=['Open Assessment Regime Zones.',
             'For each regime, link the sampling points that measure its pollutant.',
             'Then run Recalculate compliance on the Dataflow page.'],
        severity=RECOMMENDED, count=n,
        examples=_column(cursor, """
            select sp.id from sampling_points sp
             where sp.pollutant_id is not null
               and not exists (select 1 from assessmentdata ad
                                where ad.sampling_point_id = sp.id
                                  and ad.assessment_regime_id is not null)
             order by sp.id
        """))


def _check_sampling_point_locations(cursor) -> Optional[Task]:
    n = _scalar(cursor, 'select count(*) from sampling_point_locations')
    if n:
        return None
    total = _scalar(cursor, 'select count(*) from sampling_points')
    if not total:
        return None
    return Task(
        id='no-sampling-point-locations',
        title='No sampling point location history has been entered',
        why='SPL is the record of where a sampling point physically was, and when it '
            'moved. There is no v3 source for it, so a migrated database starts empty and '
            'the export falls back to the sampling point\'s own start and end dates — one '
            'location for all time, which is only true if nothing ever moved.',
        where='Sampling Points → Locations',
        how=['Open Sampling Points and add the location history for any point that has '
             'moved, changed inlet height, or changed its surroundings.',
             'If nothing has ever moved, the fallback is correct and you can leave this.'],
        severity=RECOMMENDED, count=total)


def _check_compliance_empty(cursor) -> Optional[Task]:
    regimes = _scalar(cursor, 'select count(*) from assessment_regimes')
    if not regimes:
        return None
    n = _scalar(cursor, 'select count(*) from compliance_assessment_method')
    if n:
        return None
    return Task(
        id='compliance-not-calculated',
        title='Compliance has not been calculated',
        why='CAM is the only reporting table whose contents are derived rather than '
            'entered. Until it is calculated the submission declares assessment regimes '
            'and then says nothing about whether any of them were met.',
        where='Dataflow',
        how=['Open Dataflow, choose the reporting year, and press Recalculate compliance.'],
        severity=BLOCKER, count=regimes)


LIVE_CHECKS: tuple[Callable, ...] = (
    _check_settings,
    _check_regime_identifiers,
    _check_regimes_without_zone,
    _check_dangling_classification_document,
    _check_stations_without_eoi,
    _check_authorities_without_email,
    _check_compliance_empty,
    _check_sampling_points_without_regime,
    _check_sampling_point_locations,
)


def live_tasks(cursor) -> list[dict]:
    """Everything outstanding in the database as it is right now."""
    out = []
    for check in LIVE_CHECKS:
        try:
            task = check(cursor)
        except Exception:
            try:
                cursor.connection.rollback()
            except Exception:
                pass
            continue
        if task is not None:
            out.append(task.as_dict())
    out.sort(key=lambda t: (_ORDER.get(t['severity'], 9), t['id']))
    return out


# ------------------------------------------------- migration-time extras ----

def conversion_notes(finish: dict | None) -> list[dict]:
    """What the conversion did on the operator's behalf.

    Not tasks -- the opposite. These are shown so that a changed identifier or a
    populated table is never a surprise discovered later.
    """
    finish = finish or {}
    notes: list[dict] = []

    ids = finish.get('identifiers') or {}
    repaired = ids.get('repaired') or []
    if repaired:
        notes.append(Task(
            id='did-repair-identifiers',
            title=f'{len(repaired)} assessment regime identifier(s) were rebuilt',
            why='Their v3 spelling is not a valid AssessmentRegimeId, and Raven v4 refuses '
                'to save any change to a regime whose identifier is invalid. They were '
                'rebuilt from each regime\'s own zone, pollutant, objective, target, '
                'metric and year. Assessment data and compliance rows followed '
                'automatically.',
            where='Assessment Regime Zones',
            how=['Nothing to do. The list is recorded in the run report if you need to '
                 'map an old identifier to its replacement.'],
            severity=INFO, count=len(repaired),
            examples=[f"{r['from']} → {r['to']}" for r in repaired[:5]]).as_dict())

    comp = finish.get('compliance') or {}
    if comp.get('ran') and comp.get('written'):
        notes.append(Task(
            id='did-calculate-compliance',
            title=f"Compliance was calculated for {comp.get('reporting_year')} "
                  f"({comp.get('written')} rows)",
            why='CAM is derived rather than migrated, so it would otherwise have been '
                'exported empty.',
            where='Dataflow',
            how=['Nothing to do. Re-run it from the Dataflow page whenever the '
                 'assessment data changes.'],
            severity=INFO, count=comp.get('written') or 0).as_dict())

    return notes
