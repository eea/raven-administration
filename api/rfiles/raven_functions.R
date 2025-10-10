# ---SECTION 0 ---
library(RPostgres)
library(DBI)
library(tidyr)
library(dplyr, warn.conflicts=F)
library(lubridate, warn.conflicts=F)
library(openair)
library(ggplot2)

prepare_data <- function(con){
    # Transform dataset to have date and pollutants/meteo as columns

    # get data from the observations table
    df <- dbReadTable(con, "observations") %>% select(-id)

    # replace sentinel values with NA
    df$value[df$value < -50] <- NA

    # extract station and pollutant from sampling_point_id
    df$station <- sapply(strsplit(df$sampling_point_id, "-"), '[', 2)
    df$pollutant <- sapply(strsplit(df$station, "_"), function(x) x[2])

    # detect and remove malformed sampling_point_id rows
    parts_len <- sapply(strsplit(df$sampling_point_id, "-"), length)
    bad_spo <- is.na(df$sampling_point_id) | parts_len < 2 | is.na(df$station)
    if(any(bad_spo)) df <- df[!bad_spo, ]

    # translation between SPO and pollutant
    eea_pollutants <- dbReadTable(con, "eea_pollutants")

    # map pollutant numeric id to notation
    df$pollutant_orig <- df$pollutant
    df$pollutant <- as.numeric(df$pollutant)
    df$pollutant <- eea_pollutants[match(df$pollutant, eea_pollutants$id), "notation"]
    # drop rows with unmapped pollutant
    df <- df[!is.na(df$pollutant), ]

    # parse end_position as datetime and set timezone
    df$date <- ymd_hms(df$end_position)
    df$date <- with_tz(df$date, tzone = "Etc/GMT-1")
    df <- df[!is.na(df$date), ]

    # remove rows without measurement value or pollutant
    df <- df[!is.na(df$value) & !is.na(df$pollutant), ]

    # pivot to have pollutants as columns
    data_col <- df %>% pivot_wider(
        id_cols = c(station, date),
        names_from = pollutant,
        values_from = value,
        values_fn = mean
    )

    # drop rows where all pollutant columns are NA
    pollutant_cols <- setdiff(colnames(data_col), c("station", "date"))
    if(length(pollutant_cols) > 0){
        na_rows_all <- apply(is.na(data_col[, pollutant_cols, drop = FALSE]), 1, all)
        if(any(na_rows_all)) data_col <- data_col[!na_rows_all, ]
    }

    # ensure ordering for rolling means
    data_col <- data_col %>% arrange(station, date)

    # 24h and 8h aggregations with guards
    if("PM10" %in% colnames(data_col)){
        for(st in unique(data_col$station)){
            df_st <- data_col %>% dplyr::filter(station == st)
            if(all(is.na(df_st$PM10))) next
            df_pm <- df_st %>% rollingMean(., pollutant = "PM10", width = 24, new.name = "PM10_24h",
                                           align = "right", data.capture = 75)
            if("PM10_24h" %in% colnames(df_pm)) data_col[data_col$station == st, "PM10"] <- round(df_pm$PM10_24h)
        }
    }

    if("PM2.5" %in% colnames(data_col)){
        for(st in unique(data_col$station)){
            df_st <- data_col %>% dplyr::filter(station == st)
            if(all(is.na(df_st[["PM2.5"]]))) next
            df_pm <- df_st %>% rollingMean(., pollutant = "PM2.5", width = 24, new.name = "PM2.5_24h",
                                           align = "right", data.capture = 75)
            if("PM2.5_24h" %in% colnames(df_pm)) data_col[data_col$station == st, "PM2.5"] <- round(df_pm$PM2.5_24h)
        }
    }

    if("CO" %in% colnames(data_col)){
        for(st in unique(data_col$station)){
            df_st <- data_col %>% dplyr::filter(station == st)
            if(all(is.na(df_st$CO))) next
            df_co <- df_st %>% rollingMean(., pollutant = "CO", width = 8, new.name = "CO_8h",
                                           align = "right", data.capture = 75)
            if("CO_8h" %in% colnames(df_co)) data_col[data_col$station == st, "CO"] <- round(df_co$CO_8h)
        }
    }

    return(data_col)
}
                           
plot_timeVariation <- function(df,poll){
    timeVariation(df,
                  pollutant = poll,
                  group = "station",
                  cols = "viridis")
}

# ---SECTION 1 ---


# ---SECTION 2 ---


# ---SECTION 3 ---


# ---SECTION 4 ---


# ---SECTION 5 ---


# ---SECTION 6 ---
