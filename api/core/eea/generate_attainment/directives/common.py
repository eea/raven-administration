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
    val = directive["value"]
    if val == None:
        val = directive["vegetation_value"]

    if val == None:
        val = directive["eco_value"]

    if val == None:
        val = 0
    return int(val)
