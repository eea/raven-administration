from core.database import CursorFromPool
from core.data.mean import Mean, MeanType
import pandas as pd
from core.eea.generate_attainment.directives.common import get_annual_coverage, get_limitvalue


def get_eco(directive, regime, year):
    fromtime = str(year - 2) + "-01-01"
    totime = str(year + 1) + "-01-01"
    coverage = 85
    fraction = 10
    comparingFraction = 0
    meantype = MeanType(directive["mean_type"])
    limitvalue = get_limitvalue(directive)
    exceedance_type = 2

    with CursorFromPool() as cursor:
        meanvalues = Mean.Aggregate(cursor, meantype, tuple(regime["samplingpoints"]), fromtime, totime, coverage,  3, fraction, True)
        meanvalues = aggregate_all(meanvalues)
        coverages_and_count_and_max = get_coverages_and_count_and_max(cursor, year, pd.DataFrame(meanvalues), limitvalue, comparingFraction)
        if len(coverages_and_count_and_max) > 0:

            df_with_coverage = coverages_and_count_and_max[(coverages_and_count_and_max["coverage"] >= 85)]
            df_with_coverage_or_count = coverages_and_count_and_max[(coverages_and_count_and_max["coverage"] >= 85) | (coverages_and_count_and_max["count"] > directive["count"])]

            if df_with_coverage_or_count.empty:
                return {"regime": regime, "value": 0, "exceedance_type": exceedance_type, "has_exceedances": False}

            regime["used_samplingpoints"] = list(df_with_coverage_or_count["sampling_point_id"].unique())

            cnt = df_with_coverage_or_count["count"].max()
            mx = df_with_coverage["max_value"].max()
            has_exceedances = mx > limitvalue

            value = mx

            return {"regime": regime, "value": value, "exceedance_type": exceedance_type, "has_exceedances": has_exceedances}

        return {"regime": regime, "value": 0, "exceedance_type": exceedance_type, "has_exceedances": False}


def get_coverages_and_count_and_max(cursor,  year, df, limitvalue, factor):
    if df.empty:
        return pd.DataFrame()

    spos = list(df["sampling_point_id"].unique())

    # Counts how many non-NaN values exceed limitvalue (after rounding) for each (sampling_point_id, year) group.
    counts = (
        df.groupby('sampling_point_id')['value']
        .apply(lambda x: (x.fillna(float('-inf')).round(factor) > limitvalue).sum())
        .reset_index(name='count')
    )
    values = df.groupby("sampling_point_id")["value"].max().reset_index(name='max_value')

    df = get_annual_coverage(cursor, tuple(spos), year)
    merged_df = pd.merge(df, counts, on="sampling_point_id")
    merged_df = pd.merge(merged_df, values, on="sampling_point_id")
    return merged_df


def aggregate_all(meanvalues):
    df = pd.DataFrame(meanvalues)

    sampling_point_id = df["sampling_point_id"].max()
    datetime_max = df["datetime"].max()

    g = df.groupby(["datetime"])
    n = g.agg(
        {
            "sampling_point_id": lambda x: sampling_point_id,
            "value": lambda x: x.mean(),
            "cnt": lambda x: x.count(),
            "coverage": lambda x: 100,
        }
    )

    value = round(n["value"].mean(), 1)
    meanvalues = {
        "sampling_point_id": sampling_point_id,
        "datetime": datetime_max,
        "value": value,
        "cnt": 1,
        "coverage": 100,
    }
    return [meanvalues]
