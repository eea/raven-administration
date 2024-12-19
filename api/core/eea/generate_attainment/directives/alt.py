from core.database import CursorFromPool
from core.data.mean import Mean, MeanType
import pandas as pd
from core.eea.generate_attainment.directives.common import get_annual_coverage, get_limitvalue


def get_alt(directive, regime, year):
    fromtime = str(year) + "-01-01"
    totime = str(year + 1) + "-01-01"
    coverage = 75
    fraction = 10
    comparingFraction = 0
    meantype = MeanType(directive["mean_type"])
    limitvalue = get_limitvalue(directive)
    exceedance_type = 1

    with CursorFromPool() as cursor:
        meanvalues = Mean.Aggregate(cursor, meantype, tuple(regime["samplingpoints"]), fromtime, totime, coverage,  3, fraction, True)
        coverages_and_count_and_max = get_coverages_and_count_and_max(cursor, year, pd.DataFrame(meanvalues), limitvalue, comparingFraction)
        if len(coverages_and_count_and_max) > 0:

            df_with_coverage = coverages_and_count_and_max[(coverages_and_count_and_max["coverage"] >= 85)]
            df_with_coverage_or_count = coverages_and_count_and_max[(coverages_and_count_and_max["coverage"] >= 85) | (coverages_and_count_and_max["count"] > directive["count"])]

            if df_with_coverage_or_count.empty:
                return {"regime": regime, "value": 0, "exceedance_type": exceedance_type, "has_exceedances": False}

            regime["used_samplingpoints"] = list(df_with_coverage_or_count["sampling_point_id"].unique())

            cnt = df_with_coverage_or_count["count"].max().item()
            mx = df_with_coverage["max_value"].max().item()
            has_exceedances = cnt > directive["count"] if directive["count"] != None else False

            value = cnt

            return {"regime": regime, "value": value, "exceedance_type": exceedance_type, "has_exceedances": has_exceedances}

        return {"regime": regime, "value": 0, "exceedance_type": exceedance_type, "has_exceedances": False}


def get_coverages_and_count_and_max(cursor,  year, df, limitvalue, factor):
    spos = list(df["sampling_point_id"].unique())

    counts = df.groupby('sampling_point_id')['value'].apply(lambda x: (round(x, factor) > limitvalue).sum()).reset_index(name='count')
    values = df.groupby("sampling_point_id")["value"].max().reset_index(name='max_value')

    df = get_annual_coverage(cursor, tuple(spos), year)
    merged_df = pd.merge(df, counts, on="sampling_point_id")
    merged_df = pd.merge(merged_df, values, on="sampling_point_id")
    return merged_df
