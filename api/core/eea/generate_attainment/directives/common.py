from decimal import ROUND_HALF_UP, Decimal

import pandas as pd
from core.data.mean import Mean, MeanType


def get_annual_coverage(cursor, spos, year):
    fromtime = str(year) + "-01-01"
    totime = str(year + 1) + "-01-01"
    meanvalues = Mean.Aggregate(cursor, MeanType.Year, spos, fromtime, totime, 0,  3, 3, False)

    if len(meanvalues) == 0:
        return pd.DataFrame(columns=["sampling_point_id", "coverage", "year"])

    df = pd.DataFrame(meanvalues)
    df["year"] = year
    return df[["sampling_point_id", "coverage", "year"]]


def get_summer_winter_o3_coverage(df_meanvalues):
    df_meanvalues["year"] = df_meanvalues.datetime.str[:4].astype(int)

    g = df_meanvalues.groupby(["sampling_point_id", "year"])
    cov = map(lambda x:
              {
                  "sampling_point_id": x[0][0],
                  "coverage": get_summer_winter_coverage(x[1], int(x[0][1])),
                  "year": int(x[0][1])

              }, list(g))
    return pd.DataFrame(list(cov))


def get_pre_coverage(df_meanvalues):
    return df_meanvalues[["sampling_point_id", "coverage", "year"]]


def get_summer_winter_coverage(df, year):
    winterMonths = ["01", "02", "03", "10", "11", "12"]
    summerMonths = ["04", "05", "06", "07", "08", "09"]

    days_in_winter = 183 if is_leap_year(year) else 182
    days_in_summer = 183

    new_cov = 0

    df = df[df.value != None]

    no_of_days_winter = len(df[df.datetime.str[5:7].isin(winterMonths)])
    no_of_days_summer = len(df[df.datetime.str[5:7].isin(summerMonths)])

    if no_of_days_winter > 0 and no_of_days_summer > 0:
        winter_coverage = no_of_days_winter / days_in_winter * 100
        summer_coverage = no_of_days_summer / days_in_summer * 100
        new_cov = 100 if round(winter_coverage) >= 70 and round(summer_coverage) >= 85 else 0

    return new_cov


def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_limitvalue(directive):
    """The threshold a measurement is compared against, at full precision.

    Returns the Decimal as stored. It used to `return int(val)`, which silently
    destroyed every threshold below 1 and every half-unit:

        int(Decimal('0.5'))   == 0     Lead in PM10, LV annual mean -> everything exceeds
        int(Decimal('9.3'))   == 9     PM2.5 AEI, the ERT reduction target
        int(Decimal('120.5')) == 120   the value the EEA review asked for

    The cast also contradicted the code beside it: lv.py and tv.py set
    `comparingFraction = 1` for `Lead in PM10 (aerosol)` precisely so the count
    comparison rounds to one decimal against 0.5 -- and then this threw the 0.5 away.

    The `value` -> `vegetation_value` -> `eco_value` chain stays: four limitvalues
    entries (O3 TV AOT40c-5yr, NOx CL aMean, SO2 CL wMean and aMean) carry no `value`
    at all and depend on it.
    """
    val = directive["value"]
    if val == None:
        val = directive["vegetation_value"]

    if val == None:
        val = directive["eco_value"]

    if val == None:
        val = 0
    return val


def exceeds(value, limitvalue, fraction=0):
    """Whether `value` exceeds `limitvalue` under the EEA rounding rule.

    From the Reportnet3 contractor's review of Raven (4sfera, 18 Mar 2026):

        "To determine whether an exceedance occurs, rounding needs to be applied. As a
         general rule, an exceedance is only considered when the value is >= 120.5.
         Values below 120.5 are rounded down to 120 and therefore do not count as
         exceedances."

    So the rule belongs at the comparison, not in the threshold. NILU's own answer in
    the same thread -- "All decimals are used; values are not rounded until the final
    statistic" -- says the same thing from the other side: full precision through the
    aggregation, rounding once, here.

    `fraction` is the same `comparingFraction` the count comparison uses, so a sub-unit
    threshold keeps the decimals it needs (Lead's 0.5 rounds to 1 decimal, not to 0).

    ROUND_HALF_UP is explicit and load-bearing. Three rounding modes were in play here:

        postgres round(120.5::numeric, 0) -> 121   half-up
        python   round(Decimal('120.5'))  -> 120   half-even   (the default!)
        pandas   Series([120.5]).round(0) -> 120   half-even

    EEA's rule is that 120.5 *is* an exceedance, so half-even gets the one value the
    review was actually about wrong. The SQL path is right only because it casts to
    `numeric` -- `round(120.5::float8)` is half-even too.

    >>> exceeds(120.0625, 120)
    False
    >>> exceeds(120.5, 120)
    True
    >>> exceeds(120.6125, 120)
    True
    >>> exceeds(119.5, 120)
    False
    >>> exceeds(0.44, Decimal('0.5'), 1)
    False
    >>> exceeds(0.55, Decimal('0.5'), 1)
    True
    >>> exceeds(None, 120)
    False

    A sub-unit threshold keeps its own precision even when the caller asks for none:

    >>> exceeds(9.4, Decimal('9.3'))
    True
    >>> exceeds(9.2, Decimal('9.3'))
    False
    >>> exceeds(0.55, Decimal('0.5'))
    True
    """
    if value is None or limitvalue is None:
        return False
    limit = Decimal(str(limitvalue))
    return round_half_up(value, max(int(fraction), decimals(limit))) > limit


def decimals(limitvalue):
    """How many decimal places a threshold carries.

    The rounding must never be coarser than the threshold itself, or the comparison
    throws away the digits that distinguish it. With a flat `fraction=0`, PM2.5's 9.3
    ERT reduction target would be compared against a value rounded to whole numbers, so
    a measured 9.4 would read as *not* exceeding 9.3 -- effectively moving the target to
    9.5. Lead's 0.5 has the same shape, which is why lv.py and tv.py carry a hardcoded
    `comparingFraction = 1 if pollutant == "Lead in PM10 (aerosol)"`: that constant is a
    manual approximation of this, for the one threshold anybody noticed.

    Taking the maximum of the caller's `fraction` and this means nothing is ever rounded
    more coarsely than its own threshold, and an explicit `comparingFraction` can still
    ask for more precision than the threshold needs.

    >>> decimals(Decimal('120'))
    0
    >>> decimals(Decimal('0.5'))
    1
    >>> decimals(Decimal('9.3'))
    1
    >>> decimals(Decimal('0.12'))
    2
    """
    exponent = Decimal(str(limitvalue)).normalize().as_tuple().exponent
    return max(0, -int(exponent))


def round_half_up(value, fraction=0):
    """Round like Postgres `round(numeric)` does, not like Python and pandas do."""
    quantum = Decimal(1).scaleb(-int(fraction))
    return Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP)


def count_exceedances(series, limitvalue, fraction=0):
    """How many values in `series` exceed `limitvalue`, under the same rule.

    The eight `get_coverages_and_count_and_max` helpers each spelled this inline as
    `x.round(fraction) > limitvalue`, which is pandas' half-even rounding -- so the
    count and the SQL statistics disagreed on any value sitting exactly on the half
    unit. One rule, one place.
    """
    return sum(1 for value in series
               if value is not None and value == value  # NaN excludes itself
               and exceeds(value, limitvalue, fraction))
