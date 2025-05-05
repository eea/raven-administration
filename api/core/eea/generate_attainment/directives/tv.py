from core.database import CursorFromPool
from core.data.mean import Mean, MeanType
import pandas as pd
from itertools import groupby
from core.eea.generate_attainment.directives.common import get_annual_coverage, get_summer_winter_o3_coverage, get_limitvalue, get_pre_coverage


def get_tv(directive, regime, year):
    fromtime = str(year) + "-01-01"
    totime = str(year + 1) + "-01-01"

    if directive["reportingmetric"] == "daysAbove-3yr":
        fromtime = str(year - 2) + "-01-01"
    if directive["reportingmetric"] == "AOT40c-5yr":
        fromtime = str(year - 4) + "-01-01"

    limitvalue = get_limitvalue(directive)
    exceedance_type = 1 if directive["count"] != None else 2

    agg_coverage = 75 if directive["reportingmetric"] == "daysAbove-3yr" else 85
    agg_coverage = 90 if directive["reportingmetric"] == "AOT40c-5yr" else agg_coverage

    coverage = 90 if directive["reportingmetric"] == "AOT40c-5yr" else 85

    fraction = 10
    comparingFraction = 1 if directive["pollutant"] == "Lead in PM10 (aerosol)" else 0
    meantype = MeanType(directive["mean_type"])

    with CursorFromPool() as cursor:
        meanvalues = Mean.Aggregate(cursor, meantype, tuple(regime["samplingpoints"]), fromtime, totime, agg_coverage,  3, fraction, True)
        if directive["reportingmetric"] == "AOT40c-5yr":
            meanvalues = convert_aot40(meanvalues)

        coverages_and_count_and_max = get_coverages_and_count_and_max(cursor, year, pd.DataFrame(meanvalues), limitvalue, comparingFraction, directive)

        if len(coverages_and_count_and_max) > 0:

            df_with_coverage = coverages_and_count_and_max[(coverages_and_count_and_max["coverage"] >= coverage)]
            df_with_coverage_or_count = coverages_and_count_and_max[(coverages_and_count_and_max["coverage"] >= coverage) | (coverages_and_count_and_max["count"] > directive["count"])]

            if df_with_coverage_or_count.empty:
                return {"regime": regime, "value": 0, "exceedance_type": exceedance_type, "has_exceedances": False}

            regime["used_samplingpoints"] = list(df_with_coverage_or_count["sampling_point_id"].unique())

            use_count = directive["count"] != None

            cnt = df_with_coverage_or_count["count"].max().item()
            mx = df_with_coverage["max_value"].max().item()
            has_exceedances = cnt > directive["count"] if use_count else mx > limitvalue

            value = cnt if use_count else mx

            return {"regime": regime, "value": value, "exceedance_type": exceedance_type, "has_exceedances": has_exceedances}

        return {"regime": regime, "value": 0, "exceedance_type": exceedance_type, "has_exceedances": False}


def get_coverages_and_count_and_max(cursor, year, df, limitvalue, factor, directive):
    if df.empty:
        return pd.DataFrame()

    df["year"] = df.datetime.str[:4].astype(int)

    spos = list(df["sampling_point_id"].unique())

    # Counts how many non-NaN values exceed limitvalue (after rounding) for each (sampling_point_id, year) group.
    counts = (
        df.groupby(['sampling_point_id', 'year'])['value']
        .apply(lambda x: (x.dropna().round(factor) > limitvalue).sum())
        .reset_index(name='count')
    )
    values = df.groupby(['sampling_point_id', 'year'])["value"].max().reset_index(name='max_value')

    if directive["pollutant"] == "O3" and directive["reportingmetric"] == "daysAbove-3yr":
        df = get_summer_winter_o3_coverage(pd.DataFrame(df))
    elif directive["reportingmetric"] == "AOT40c-5yr":
        df = get_pre_coverage(pd.DataFrame(df))
    else:
        df = get_annual_coverage(cursor, tuple(spos), year)

    merged_df = pd.merge(df, counts, on=['sampling_point_id', 'year'])
    merged_df = pd.merge(merged_df, values, on=['sampling_point_id', 'year'])

    if directive["pollutant"] == "O3" and directive["reportingmetric"] == "daysAbove-3yr":
        merged_df = merged_df.groupby(["sampling_point_id"]).agg(
            {
                "year": lambda x: x.max(),
                "coverage": lambda x: 100 if x.max() >= 85 else 0,
                "count": lambda x: round(x.mean()),
                "max_value": lambda x: x.max(),
            }
        ).reset_index()

    return merged_df


def convert_aot40(meanvalues):
    df_meanvalues = pd.DataFrame(meanvalues)
    if df_meanvalues.empty:
        return meanvalues

    g = df_meanvalues.groupby(["sampling_point_id", "unit", "station", "component", "timestep", "lng", "lat", "meantype"])
    n = g.agg(
        {
            "value": lambda x: x.mean(),
            "cnt": lambda x: x.count(),
            "coverage": lambda x: 100 if (x >= 85).sum() >= 3 else 0,
            "datetime": lambda x: x.max()
        }
    )
    meanvalues = n.reset_index().to_dict(orient="records")
    return meanvalues
