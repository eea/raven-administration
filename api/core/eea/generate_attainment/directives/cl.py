import pandas as pd
from core.database import CursorFromPool
from core.data.mean import Mean, MeanType
from core.eea.generate_attainment.directives.common import get_annual_coverage, get_pre_coverage, get_limitvalue


def get_cl(directive, regime, year):
    fromtime = str(year) + "-01-01"
    totime = str(year + 1) + "-01-01"

    limitvalue = get_limitvalue(directive)
    exceedance_type = 2

    agg_coverage = 85
    coverage = 85
    fraction = 10
    comparingFraction = 0
    meantype = MeanType(directive["mean_type"])

    with CursorFromPool() as cursor:
        meanvalues = Mean.Aggregate(cursor, meantype, tuple(regime["samplingpoints"]), fromtime, totime, agg_coverage,  3, fraction, True)
        coverages_and_count_and_max = get_coverages_and_count_and_max(cursor, year, pd.DataFrame(meanvalues), limitvalue, comparingFraction, directive)
        if len(coverages_and_count_and_max) > 0:

            df_with_coverage = coverages_and_count_and_max[(coverages_and_count_and_max["coverage"] >= coverage)]
            df_with_coverage_or_count = coverages_and_count_and_max[(coverages_and_count_and_max["coverage"] >= coverage) | (coverages_and_count_and_max["count"] > directive["count"])]

            if df_with_coverage_or_count.empty:
                return {"regime": regime, "value": 0, "exceedance_type": exceedance_type, "has_exceedances": False}

            regime["used_samplingpoints"] = list(df_with_coverage_or_count["sampling_point_id"].unique())

            cnt = df_with_coverage_or_count["count"].max().item()
            mx = df_with_coverage["max_value"].max().item()
            has_exceedances = mx > limitvalue

            value = mx

            return {"regime": regime, "value": value, "exceedance_type": exceedance_type, "has_exceedances": has_exceedances}

        return {"regime": regime, "value": 0, "exceedance_type": exceedance_type, "has_exceedances": False}


def get_coverages_and_count_and_max(cursor, year, df, limitvalue, factor, directive):
    df["year"] = df.datetime.str[:4].astype(int)

    spos = list(df["sampling_point_id"].unique())

    counts = df.groupby(['sampling_point_id', 'year'])['value'].apply(lambda x: (round(x, factor) > limitvalue).sum()).reset_index(name='count')
    values = df.groupby(['sampling_point_id', 'year'])["value"].max().reset_index(name='max_value')

    if directive["pollutant"] == "O3" and directive["reportingmetric"] == "wMean":
        df = get_pre_coverage(pd.DataFrame(df))
    else:
        df = get_annual_coverage(cursor, tuple(spos), year)

    merged_df = pd.merge(df, counts, on=['sampling_point_id', 'year'])
    merged_df = pd.merge(merged_df, values, on=['sampling_point_id', 'year'])

    # if directive["pollutant"] == "O3" and directive["reportingmetric"] == "wMean":
    #     merged_df = merged_df.groupby(["sampling_point_id"]).agg(
    #         {
    #             "year": lambda x: x.max(),
    #             "coverage": lambda x: 100 if x.max() >= 85 else 0,
    #             "count": lambda x: round(x.mean()),
    #             "max_value": lambda x: x.max(),
    #         }
    #     ).reset_index()

    return merged_df
