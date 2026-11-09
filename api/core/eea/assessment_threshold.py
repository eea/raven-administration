"""Proposes an assessment regime's AssessmentThresholdExceedance (ARZ) from measured data.

A zone is classified per pollutant against the directive's assessment thresholds:

- 2008/50/EC Annex II A (and 2004/107/EC Annex II I for As, Cd, Ni and BaP): an upper and
  a lower threshold, giving aboveUAT, LAT-UAT or belowLAT.
- (EU) 2024/2881 Annex II: one assessment threshold, giving aboveAT or belowAT. The EEA
  vocabulary does not list these values yet, so they apply only to an objective whose
  allowed values include aboveAT.
- Ozone's long-term objective (2008/50 Article 9): aboveLTO if it was exceeded in any of
  the previous five years.

The determination rule is the same in all three directives (2008/50 Annex II B, 2004/107
Annex II II, 2024/2881 Article 7(3)): use the previous five years, and a threshold counts
as exceeded if it was exceeded in at least three separate years out of those five.

Values come from the directive texts as published by the EU Publications Office, and
docs-nilu/aggregations and statistics/ASSESSMENT_THRESHOLDS.md lists them.
tests/unit/test_assessment_thresholds.py checks that the two agree.

Where fewer than five years have data, the directives allow campaigns and modelling to
fill in. That is the user's call, so the proposal is reported as undetermined, unless the
missing years could not change the outcome (three years already above, say).
"""
from dataclasses import dataclass
from typing import Optional

# eea_pollutants ids (the vocabulary's numeric pollutant codes).
SO2, PM10, O3, NO2, NOX, CO, C6H6, PM25 = 1, 5, 7, 8, 9, 10, 20, 6001
PB, CD, NI, AS, BAP = 5012, 5014, 5015, 5018, 5029

# Statistic kinds. Each yields one number per sampling point and year.
ANNUAL_MEAN = 'aMean'           # annual mean
WINTER_MEAN = 'winterMean'      # 1 October - 31 March, counted to the year it ends in
DAYS_ABOVE = 'daysAbove'        # days whose daily mean is above the value
HOURS_ABOVE = 'hrsAbove'        # hours whose hourly mean is above the value
DMAX8H_DAYS_ABOVE = 'dmax8hDaysAbove'   # days whose maximum 8-hour mean is above
AOT40 = 'AOT40'                 # AOT40 for vegetation, May-July


@dataclass(frozen=True)
class Threshold:
    directive: str
    pollutant_id: int
    pollutant: str
    target: str                 # protection target notation: H or V
    kind: str
    upper: float                # UAT, AT or LTO
    lower: Optional[float]      # LAT, or None where there is one threshold
    allowed: Optional[int]      # exceedances allowed per year for a count statistic
    unit: str
    label: str


def _t(directive, pollutant_id, pollutant, target, kind, upper, lower, allowed, unit, label):
    return Threshold(directive, pollutant_id, pollutant, target, kind, upper, lower,
                     allowed, unit, label)


UPPER_LOWER = (
    # 2008/50/EC Annex II A
    _t('2008/50', SO2, 'SO2', 'H', DAYS_ABOVE, 75, 50, 3, 'µg/m³', '24-hour'),
    _t('2008/50', SO2, 'SO2', 'V', WINTER_MEAN, 12, 8, None, 'µg/m³', 'winter'),
    _t('2008/50', NO2, 'NO2', 'H', HOURS_ABOVE, 140, 100, 18, 'µg/m³', 'hourly'),
    _t('2008/50', NO2, 'NO2', 'H', ANNUAL_MEAN, 32, 26, None, 'µg/m³', 'annual'),
    _t('2008/50', NOX, 'NOx', 'V', ANNUAL_MEAN, 24, 19.5, None, 'µg/m³', 'annual'),
    _t('2008/50', PM10, 'PM10', 'H', DAYS_ABOVE, 35, 25, 35, 'µg/m³', '24-hour'),
    _t('2008/50', PM10, 'PM10', 'H', ANNUAL_MEAN, 28, 20, None, 'µg/m³', 'annual'),
    _t('2008/50', PM25, 'PM2.5', 'H', ANNUAL_MEAN, 17, 12, None, 'µg/m³', 'annual'),
    _t('2008/50', PB, 'Pb', 'H', ANNUAL_MEAN, 0.35, 0.25, None, 'µg/m³', 'annual'),
    _t('2008/50', C6H6, 'C6H6', 'H', ANNUAL_MEAN, 3.5, 2, None, 'µg/m³', 'annual'),
    # "Eight-hour average", with no exceedances allowed: one day above is enough.
    _t('2008/50', CO, 'CO', 'H', DMAX8H_DAYS_ABOVE, 7, 5, 0, 'mg/m³', '8-hour'),
    # 2004/107/EC Annex II I
    _t('2004/107', AS, 'As', 'H', ANNUAL_MEAN, 3.6, 2.4, None, 'ng/m³', 'annual'),
    _t('2004/107', CD, 'Cd', 'H', ANNUAL_MEAN, 3, 2, None, 'ng/m³', 'annual'),
    _t('2004/107', NI, 'Ni', 'H', ANNUAL_MEAN, 14, 10, None, 'ng/m³', 'annual'),
    _t('2004/107', BAP, 'BaP', 'H', ANNUAL_MEAN, 0.6, 0.4, None, 'ng/m³', 'annual'),
)

SINGLE = (
    # (EU) 2024/2881 Annex II, Section 1 (health). Footnote (1): the 24-hour and 8-hour
    # values are 99th percentiles, i.e. 3 exceedance days per year.
    _t('2024/2881', PM25, 'PM2.5', 'H', ANNUAL_MEAN, 5, None, None, 'µg/m³', 'annual'),
    _t('2024/2881', PM10, 'PM10', 'H', ANNUAL_MEAN, 15, None, None, 'µg/m³', 'annual'),
    _t('2024/2881', NO2, 'NO2', 'H', ANNUAL_MEAN, 10, None, None, 'µg/m³', 'annual'),
    _t('2024/2881', SO2, 'SO2', 'H', DAYS_ABOVE, 40, None, 3, 'µg/m³', '24-hour'),
    _t('2024/2881', C6H6, 'C6H6', 'H', ANNUAL_MEAN, 1.7, None, None, 'µg/m³', 'annual'),
    _t('2024/2881', CO, 'CO', 'H', DAYS_ABOVE, 4, None, 3, 'mg/m³', '24-hour'),
    _t('2024/2881', PB, 'Pb', 'H', ANNUAL_MEAN, 0.25, None, None, 'µg/m³', 'annual'),
    _t('2024/2881', AS, 'As', 'H', ANNUAL_MEAN, 3.0, None, None, 'ng/m³', 'annual'),
    _t('2024/2881', CD, 'Cd', 'H', ANNUAL_MEAN, 2.5, None, None, 'ng/m³', 'annual'),
    _t('2024/2881', NI, 'Ni', 'H', ANNUAL_MEAN, 10, None, None, 'ng/m³', 'annual'),
    _t('2024/2881', BAP, 'BaP', 'H', ANNUAL_MEAN, 0.30, None, None, 'ng/m³', 'annual'),
    _t('2024/2881', O3, 'O3', 'H', DMAX8H_DAYS_ABOVE, 100, None, 3, 'µg/m³', '8-hour max'),
    # Section 2 (vegetation and natural ecosystems)
    _t('2024/2881', SO2, 'SO2', 'V', WINTER_MEAN, 8, None, None, 'µg/m³', 'winter'),
    _t('2024/2881', NOX, 'NOx', 'V', ANNUAL_MEAN, 19.5, None, None, 'µg/m³', 'annual'),
)

LONG_TERM = (
    # 2008/50/EC Annex VII C: ozone long-term objectives.
    _t('2008/50', O3, 'O3', 'H', DMAX8H_DAYS_ABOVE, 120, None, 0, 'µg/m³', '8-hour max'),
    _t('2008/50', O3, 'O3', 'V', AOT40, 6000, None, None, 'µg/m³·h', 'AOT40'),
)

ALL_THRESHOLDS = UPPER_LOWER + SINGLE + LONG_TERM

# Pollutants sampled rather than measured continuously: an annual mean from one sample
# every few days still counts (2004/107 Annex IV asks for 33 % for fixed measurement of
# metals and BaP, indicative 14 %). Everything else needs 75 %.
_SAMPLED = {PB, CD, NI, AS, BAP, C6H6}
MIN_COVERAGE, MIN_COVERAGE_SAMPLED = 75, 14

YEARS = 5
NEEDED = 3

UPPER_LOWER_SCHEME, SINGLE_SCHEME, LTO_SCHEME, NA_SCHEME = 'UAT', 'AT', 'LTO', 'NA'


def scheme(allowed):
    """Which classification an environmental objective takes, from its allowed values."""
    allowed = set(allowed or ())
    if 'aboveUAT' in allowed:
        return UPPER_LOWER_SCHEME
    if 'aboveAT' in allowed:
        return SINGLE_SCHEME
    if 'aboveLTO' in allowed:
        return LTO_SCHEME
    if allowed == {'NA'}:
        return NA_SCHEME
    return None


def allowed_values(assessment_threshold):
    """eea_environmentalobjective.assessment_threshold: comma-joined URIs -> notations."""
    if not assessment_threshold:
        return []
    return [part.strip().rstrip('/').rsplit('/', 1)[-1]
            for part in str(assessment_threshold).split(',') if part.strip()]


def thresholds_for(pollutant_id, target, scheme_name):
    table = {UPPER_LOWER_SCHEME: UPPER_LOWER, SINGLE_SCHEME: SINGLE,
             LTO_SCHEME: LONG_TERM}.get(scheme_name, ())
    return [t for t in table if t.pollutant_id == pollutant_id and t.target == target]


# ---------------------------------------------------------------------------
# Classification from yearly statistics -- pure, so it is unit-tested without a database
# ---------------------------------------------------------------------------

def _exceeds(threshold, value, limit):
    if value is None or limit is None:
        return False
    if threshold.allowed is not None:
        return value > threshold.allowed
    return value > limit


def _level(threshold, stat):
    """2: above the upper threshold; 1: above the lower one only; 0: below both."""
    if threshold.allowed is not None:
        # A count statistic carries one count per threshold value.
        upper, lower = stat
        if _exceeds(threshold, upper, threshold.upper):
            return 2
        return 1 if threshold.lower is not None and _exceeds(threshold, lower, threshold.lower) else 0
    if _exceeds(threshold, stat, threshold.upper):
        return 2
    return 1 if threshold.lower is not None and _exceeds(threshold, stat, threshold.lower) else 0


_NAMES = {
    UPPER_LOWER_SCHEME: {2: 'aboveUAT', 1: 'LAT-UAT', 0: 'belowLAT'},
    SINGLE_SCHEME: {2: 'aboveAT', 0: 'belowAT'},
    LTO_SCHEME: {2: 'aboveLTO', 0: 'belowLTO'},
}


def _outcome(scheme_name, levels):
    """The classification for a list of yearly levels, five long at most."""
    if scheme_name == LTO_SCHEME:
        return 2 if any(level == 2 for level in levels) else 0
    above_upper = sum(1 for level in levels if level >= 2)
    above_lower = sum(1 for level in levels if level >= 1)
    if above_upper >= NEEDED:
        return 2
    if scheme_name == UPPER_LOWER_SCHEME and above_lower >= NEEDED:
        return 1
    return 0


def classify_years(scheme_name, thresholds, yearly):
    """Classify from {threshold: {year: stat}} over the five-year window.

    A year missing from a threshold's dict had too little data. The outcome is
    determined when filling the missing years with the best case and with the worst
    case gives the same classification; otherwise `value` is None.
    """
    best, worst, details = 0, 0, []
    for threshold in thresholds:
        stats = yearly.get(threshold, {})
        levels = [_level(threshold, stat) for stat in stats.values()]
        missing = YEARS - len(levels)
        best = max(best, _outcome(scheme_name, levels + [0] * missing))
        worst = max(worst, _outcome(scheme_name, levels + [2] * missing))
        details.append(_describe(threshold, stats, levels))

    # A single-threshold scheme only ever yields 2 or 0: it has no lower level.
    value = _NAMES[scheme_name][best] if best == worst else None
    years_with_data = max((len(yearly.get(t, {})) for t in thresholds), default=0)
    if value is None:
        details.insert(0, f'undetermined: data for {years_with_data} of {YEARS} years')
    return {'value': value, 'basis': '; '.join(details), 'years_with_data': years_with_data}


def _describe(threshold, stats, levels):
    lower = f'/{_num(threshold.lower)}' if threshold.lower is not None else ''
    if threshold.lower is not None:
        name = 'UAT/LAT'
    else:
        name = 'AT' if threshold.directive == '2024/2881' else 'LTO'
    if threshold.allowed is not None:
        what = f'{threshold.label} > {_num(threshold.upper)}{lower} {threshold.unit} more than {threshold.allowed}x'
    else:
        what = f'{threshold.label} {name} {_num(threshold.upper)}{lower} {threshold.unit}'
    if not stats:
        return f'{threshold.pollutant} {what}: no year with enough data'
    upper = sum(1 for level in levels if level >= 2)
    text = f'{threshold.pollutant} {what}: upper exceeded {upper}/{len(levels)} yrs'
    if threshold.lower is not None:
        text += f', lower {sum(1 for level in levels if level >= 1)}/{len(levels)}'
    if threshold.allowed is not None:
        # Counts: the worst year by how often the lower (or only) value was passed.
        peak_year, (above_upper, above_lower) = max(stats.items(), key=lambda kv: kv[1][::-1])
        times = f'{above_upper}x above {_num(threshold.upper)}'
        if threshold.lower is not None:
            times += f', {above_lower}x above {_num(threshold.lower)}'
        return f'{text} (worst {peak_year}: {times})'
    peak_year, peak = max(stats.items(), key=lambda kv: kv[1])
    return f'{text} (max {_num(round(peak, 3))} {threshold.unit} in {peak_year})'


def _num(value):
    return f'{float(value):g}'


# ---------------------------------------------------------------------------
# Yearly statistics from the database
# ---------------------------------------------------------------------------

# A station is in a zone when its coordinates are inside the zone's geometry. Stations
# carry WGS84 latitude/longitude; a zone stored in another SRID is transformed to.
IN_ZONE = """st_contains(z.geom,
        CASE WHEN st_srid(z.geom) IN (0, 4326)
             THEN st_setsrid(st_makepoint(st.longitude, st.latitude), st_srid(z.geom))
             ELSE st_transform(st_setsrid(st_makepoint(st.longitude, st.latitude), 4326),
                               st_srid(z.geom)) END)"""

_POINTS = f"""
    SELECT sp.id, sp.unit_id
      FROM sampling_points sp
      JOIN stations st ON st.id = sp.station_id
      JOIN zones z ON z.id = %(zone)s
     WHERE sp.pollutant_id = %(pollutant)s
       AND st.longitude IS NOT NULL AND st.latitude IS NOT NULL
       AND {IN_ZONE}
"""

# Years with enough data, per sampling point -- the same for every statistic.
_COVERED = """
    SELECT sampling_point_id, extract(year FROM "time")::int AS year
      FROM observations_year
     WHERE sampling_point_id = ANY(%(points)s)
       AND "time" >= make_date(%(first)s, 1, 1) AND "time" < make_date(%(last)s + 1, 1, 1)
       AND cov >= %(coverage)s
"""

_STATISTIC_SQL = {
    ANNUAL_MEAN: """
        SELECT sampling_point_id, extract(year FROM "time")::int AS year, val AS stat
          FROM observations_year
         WHERE sampling_point_id = ANY(%(points)s)
           AND "time" >= make_date(%(first)s, 1, 1) AND "time" < make_date(%(last)s + 1, 1, 1)
           AND val IS NOT NULL""",
    WINTER_MEAN: """
        SELECT sampling_point_id, extract(year FROM "time")::int AS year, val AS stat
          FROM observations_winter_season
         WHERE sampling_point_id = ANY(%(points)s)
           AND "time" >= make_date(%(first)s, 1, 1) AND "time" < make_date(%(last)s + 1, 1, 1)
           AND val IS NOT NULL AND cov >= %(coverage)s""",
    DAYS_ABOVE: """
        SELECT sampling_point_id, extract(year FROM "time")::int AS year,
               count(*) FILTER (WHERE val > %(upper)s) AS stat,
               count(*) FILTER (WHERE val > %(lower)s) AS stat_lower
          FROM observations_day
         WHERE sampling_point_id = ANY(%(points)s)
           AND "time" >= make_date(%(first)s, 1, 1) AND "time" < make_date(%(last)s + 1, 1, 1)
           AND cov >= 75
         GROUP BY 1, 2""",
    DMAX8H_DAYS_ABOVE: """
        SELECT sampling_point_id, extract(year FROM "time")::int AS year,
               count(*) FILTER (WHERE val > %(upper)s) AS stat,
               count(*) FILTER (WHERE val > %(lower)s) AS stat_lower
          FROM observations_day_8hmax
         WHERE sampling_point_id = ANY(%(points)s)
           AND "time" >= make_date(%(first)s, 1, 1) AND "time" < make_date(%(last)s + 1, 1, 1)
           AND val IS NOT NULL
         GROUP BY 1, 2""",
    # No pre-aggregate counts hours; the observations are read for these points only.
    HOURS_ABOVE: """
        SELECT sampling_point_id, extract(year FROM hour)::int AS year,
               count(*) FILTER (WHERE val > %(upper)s) AS stat,
               count(*) FILTER (WHERE val > %(lower)s) AS stat_lower
          FROM (SELECT sampling_point_id, date_trunc('hour', from_time) AS hour,
                       avg(value) FILTER (WHERE observationvalidity_id >= 1) AS val
                  FROM observations
                 WHERE sampling_point_id = ANY(%(points)s)
                   AND from_time >= make_date(%(first)s, 1, 1)
                   AND from_time < make_date(%(last)s + 1, 1, 1)
                 GROUP BY 1, 2) hourly
         GROUP BY 1, 2""",
    AOT40: """
        SELECT sampling_point_id, extract(year FROM "time")::int AS year, val AS stat
          FROM observations_aot40v
         WHERE sampling_point_id = ANY(%(points)s)
           AND "time" >= make_date(%(first)s, 1, 1) AND "time" < make_date(%(last)s + 1, 1, 1)
           AND val IS NOT NULL AND cov >= 90""",
}


# Concentration units relative to µg/m³: the sampling point's (eea_concentrations id)
# and the threshold's. A sampling point in ng/m³ is compared with a threshold in µg/m³
# by scaling, not by assuming the numbers are in the same unit.
_POINT_UNIT = {'ug.m-3': 1.0, 'ng.m-3': 1e-3, 'mg.m-3': 1e3}
_THRESHOLD_UNIT = {'µg/m³': 1.0, 'µg/m³·h': 1.0, 'ng/m³': 1e-3, 'mg/m³': 1e3}


def unit_factor(point_unit, threshold_unit):
    """Multiply a sampling point's value by this to get it in the threshold's unit.

    An unknown unit is taken to be the threshold's own.
    """
    point = _POINT_UNIT.get(point_unit)
    target = _THRESHOLD_UNIT.get(threshold_unit)
    if point is None or target is None:
        return 1.0
    return point / target


def yearly_statistics(cursor, zone_id, threshold, year):
    """{year: stat} for the five years before `year`: the zone's worst sampling point.

    For a count statistic the stat is (count above the upper value, count above the
    lower value), each the maximum over the zone's sampling points. Values are in the
    threshold's unit.
    """
    cursor.execute(_POINTS, {'zone': zone_id, 'pollutant': threshold.pollutant_id})
    groups = {}
    for row in cursor.fetchall():
        groups.setdefault(unit_factor(row['unit_id'], threshold.unit), []).append(row['id'])

    per_year = {}
    for factor, points in groups.items():
        lower = threshold.lower if threshold.lower is not None else threshold.upper
        params = {'points': points, 'first': year - YEARS, 'last': year - 1,
                  'coverage': MIN_COVERAGE_SAMPLED if threshold.pollutant_id in _SAMPLED
                  else MIN_COVERAGE,
                  # Counted in the points' own unit.
                  'upper': threshold.upper / factor, 'lower': lower / factor}

        cursor.execute(_COVERED, params)
        covered = {(row['sampling_point_id'], row['year']) for row in cursor.fetchall()}

        cursor.execute(_STATISTIC_SQL[threshold.kind], params)
        for row in cursor.fetchall():
            # Winter and AOT40 carry their own coverage; the rest need the annual one.
            if threshold.kind not in (WINTER_MEAN, AOT40) and \
                    (row['sampling_point_id'], row['year']) not in covered:
                continue
            if threshold.allowed is not None:
                stat = (int(row['stat']), int(row['stat_lower']))
                prev = per_year.get(row['year'])
                per_year[row['year']] = stat if prev is None else (max(prev[0], stat[0]),
                                                                   max(prev[1], stat[1]))
            else:
                stat = float(row['stat']) * factor
                per_year[row['year']] = max(per_year.get(row['year'], stat), stat)
    return per_year


def classify(cursor, zone_id, pollutant_id, target, allowed, year, cache=None):
    """Proposed AssessmentThresholdExceedance for one regime, or None with a reason.

    Returns {'value': notation or None, 'basis': text}. `cache` is shared across calls so
    a zone's statistics are read once for all objectives that need them.
    """
    scheme_name = scheme(allowed)
    if scheme_name is None:
        return {'value': None, 'basis': ''}
    if scheme_name == NA_SCHEME:
        return {'value': 'NA', 'basis': 'the objective allows only NA'}
    thresholds = thresholds_for(pollutant_id, target, scheme_name)
    if not thresholds:
        return {'value': None, 'basis': 'no assessment threshold in the directives for this '
                                         'pollutant and protection target'}
    cache = {} if cache is None else cache
    yearly = {}
    for threshold in thresholds:
        key = (zone_id, threshold, year)
        if key not in cache:
            cache[key] = yearly_statistics(cursor, zone_id, threshold, year)
        yearly[threshold] = cache[key]
    return classify_years(scheme_name, thresholds, yearly)
