from core.data.mean import Mean, MeanType
from datetime import datetime


class Statistics:
    def __init__(self, cursor):
        self.cursor = cursor

    # ============================================================================
    # Public API Methods
    # ============================================================================

    def generate(self, aggregation_process, pollutant, year):
        # switch case for different aggregation processes, case insensitive
        if aggregation_process.lower() == "winter-avg":
            return self.generate_winter_avg(pollutant, year)
        elif aggregation_process.lower() == "aot40c":
            return self.generate_aot40c(pollutant, year)
        elif aggregation_process.lower() == "aot40c-p5y":
            return self.generate_aot40c_p5y(pollutant, year)
        elif aggregation_process.lower() == "p1y":
            return self.generate_p1y(pollutant, year)
        elif aggregation_process.lower() == "p1y-hr-max":
            return self.generate_p1y_hr_max(pollutant, year)
        elif aggregation_process.lower() == "p1y-hr-min":
            return self.generate_p1y_hr_min(pollutant, year)
        elif aggregation_process.lower() == "p1y-day-max":
            return self.generate_p1y_day_max(pollutant, year)
        elif aggregation_process.lower() == "p1y-day-min":
            return self.generate_p1y_day_min(pollutant, year)
        elif aggregation_process.lower() == "p1y-p1d-per99":
            return self.generate_p1y_day_per99(pollutant, year)
        elif aggregation_process.lower() == "p1y-3daysabove50":
            return self.generate_p1y_consecutive_days_above_50(pollutant, year)
        elif aggregation_process.lower() == "p1y-3daysabove90":
            return self.generate_p1y_consecutive_days_above_90(pollutant, year)
        elif aggregation_process.lower() == "p1y-daysabove125":
            return self.generate_p1y_days_above_125(pollutant, year)
        elif aggregation_process.lower() == "p1y-daysabove25":
            return self.generate_p1y_days_above_25(pollutant, year)
        elif aggregation_process.lower() == "p1y-daysabove4":
            return self.generate_p1y_days_above_4(pollutant, year)
        elif aggregation_process.lower() == "p1y-daysabove45":
            return self.generate_p1y_days_above_45(pollutant, year)
        elif aggregation_process.lower() == "p1y-daysabove50":
            return self.generate_p1y_days_above_50(pollutant, year)
        elif aggregation_process.lower() == "p1y-daysabove90":
            return self.generate_p1y_days_above_90(pollutant, year)
        elif aggregation_process.lower() == "p1y-dmaxabove100":
            return self.generate_p1y_daymax_above_100(pollutant, year)
        elif aggregation_process.lower() == "p1y-dmaxabove120":
            return self.generate_p1y_daymax_above_120(pollutant, year)
        elif aggregation_process.lower() == "p1y-3habove200":
            return self.generate_p1y_3h_above_200(pollutant, year)
        elif aggregation_process.lower() == "p1y-3habove350":
            return self.generate_p1y_3h_above_350(pollutant, year)
        elif aggregation_process.lower() == "p1y-3habove400":
            return self.generate_p1y_3h_above_400(pollutant, year)
        elif aggregation_process.lower() == "p1y-3habove500":
            return self.generate_p1y_3h_above_500(pollutant, year)
        elif aggregation_process.lower() == "p1y-8hdmxabove10":
            return self.generate_p1y_8hdmx_above_10(pollutant, year)
        elif aggregation_process.lower() == "p1y-dmax-per99":
            return self.generate_p1y_dmax_per99(pollutant, year)
        elif aggregation_process.lower() == "p1y-hrsabove150":
            return self.generate_p1y_hrs_above_150(pollutant, year)
        elif aggregation_process.lower() == "p1y-hrsabove180":
            return self.generate_p1y_hrs_above_180(pollutant, year)
        elif aggregation_process.lower() == "p1y-hrsabove200":
            return self.generate_p1y_hrs_above_200(pollutant, year)
        elif aggregation_process.lower() == "p1y-hrsabove240":
            return self.generate_p1y_hrs_above_240(pollutant, year)
        elif aggregation_process.lower() == "p1y-hrsabove275":
            return self.generate_p1y_hrs_above_275(pollutant, year)
        elif aggregation_process.lower() == "p1y-hrsabove350":
            return self.generate_p1y_hrs_above_350(pollutant, year)
        elif aggregation_process.lower() == "p3y-dmaxabove120":
            return self.generate_p3y_dmax_above_120(pollutant, year)
        elif aggregation_process.lower() == "somo10":
            return self.generate_somo10(pollutant, year)
        elif aggregation_process.lower() == "somo35":
            return self.generate_somo35(pollutant, year)

        return []

    # ============================================================================
    # Count Aggregation Methods
    # ============================================================================
    def generate_p1y_days_above_125(self, pollutant, year):
        """
        Count of days with values above 125 µg/m³ (P1Y-daysAbove125).
        Uses the pre-calculated daily values from observations_day table.

        Returns count of days above threshold, with coverage as None.
        """
        sql = self._get_count_observation_data("observations_day", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-daysAbove125",
            "year": year,
            "pollutant": pollutant,
            "threshold": 125,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_days_above_25(self, pollutant, year):
        """
        Count of days with values above 25 µg/m³ (P1Y-daysAbove25).
        Uses the pre-calculated daily values from observations_day table.

        Returns count of days above threshold, with coverage as None.
        """
        sql = self._get_count_observation_data("observations_day", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-daysAbove25",
            "year": year,
            "pollutant": pollutant,
            "threshold": 25,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_days_above_4(self, pollutant, year):
        """
        Count of days with values above 4 µg/m³ (P1Y-daysAbove4).
        Uses the pre-calculated daily values from observations_day table.

        Returns count of days above threshold, with coverage as None.
        """
        sql = self._get_count_observation_data("observations_day", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-daysAbove4",
            "year": year,
            "pollutant": pollutant,
            "threshold": 4,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_days_above_45(self, pollutant, year):
        """
        Count of days with values above 45 µg/m³ (P1Y-daysAbove45).
        Uses the pre-calculated daily values from observations_day table.

        Returns count of days above threshold, with coverage as None.
        """
        sql = self._get_count_observation_data("observations_day", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-daysAbove45",
            "year": year,
            "pollutant": pollutant,
            "threshold": 45,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_days_above_50(self, pollutant, year):
        """
        Count of days with values above 50 µg/m³ (P1Y-daysAbove50).
        Uses the pre-calculated daily values from observations_day table.

        Returns count of days above threshold, with coverage as None.
        """
        sql = self._get_count_observation_data("observations_day", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-daysAbove50",
            "year": year,
            "pollutant": pollutant,
            "threshold": 50,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_days_above_90(self, pollutant, year):
        """
        Count of days with values above 90 µg/m³ (P1Y-daysAbove90).
        Uses the pre-calculated daily values from observations_day table.

        Returns count of days above threshold, with coverage as None.
        """
        sql = self._get_count_observation_data("observations_day", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-daysAbove90",
            "year": year,
            "pollutant": pollutant,
            "threshold": 90,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_daymax_above_100(self, pollutant, year):
        """
        Count of days with values above 100 µg/m³ (P1Y-dmaxAbove100).
        Uses the pre-calculated daily values from observations_day_8hmax table.

        Returns count of days above threshold, with coverage as None.
        """
        sql = self._get_count_observation_data("observations_day_8hmax", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-dmaxAbove100",
            "year": year,
            "pollutant": pollutant,
            "threshold": 100,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_daymax_above_120(self, pollutant, year):
        """
        Count of days with values above 120 µg/m³ (P1Y-dmaxAbove120).
        Uses the pre-calculated daily values from observations_day_8hmax table.

        Returns count of days above threshold, with coverage as None.
        """
        sql = self._get_count_observation_data("observations_day_8hmax", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-dmaxAbove120",
            "year": year,
            "pollutant": pollutant,
            "threshold": 120.5,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================
    # Simple Aggregation Methods
    # ============================================================================

    def generate_p1y(self, pollutant, year):
        """Annual (1-year) aggregation data."""
        sql = self._get_simple_observation_data("observations_year", pollutant, year)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_winter_avg(self, pollutant, year):
        """
        Winter season average (Oct 1 - Mar 31) for ecosystem protection.
        Uses daily means from observations_day with 75% coverage threshold (EU assessment standard).
        Winter for year Y = Oct-Dec of year Y-1 + Jan-Mar of year Y.
        
        See: eea-raven/docs-nilu/winter-avg-calculation.md for methodology notes.
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        winter_days AS (
            -- Oct, Nov, Dec of previous year
            SELECT sampling_point_id, time, val, cov
            FROM observations_day
            WHERE EXTRACT(YEAR FROM time) = %(year)s - 1
              AND EXTRACT(MONTH FROM time) IN (10, 11, 12)
              AND val IS NOT NULL
            UNION ALL
            -- Jan, Feb, Mar of current year
            SELECT sampling_point_id, time, val, cov
            FROM observations_day
            WHERE EXTRACT(YEAR FROM time) = %(year)s
              AND EXTRACT(MONTH FROM time) IN (1, 2, 3)
              AND val IS NOT NULL
        ),
        expected_days AS (
            -- Calculate expected winter days (182 or 183 if leap year in Feb)
            SELECT CASE 
                WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) 
                THEN 183  -- leap year has 29 days in Feb
                ELSE 182
            END as total_days
        )
        SELECT 
            asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            ROUND(AVG(CASE WHEN wd.cov >= 75 THEN wd.val END)::numeric, 3) as value,
            ROUND((COUNT(CASE WHEN wd.cov >= 75 THEN 1 END)::numeric / ed.total_days) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN expected_days ed
        LEFT JOIN winter_days wd ON wd.sampling_point_id = asp.spo
        GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, ed.total_days
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        self.cursor.execute(sql, {
            "aggregation_process": "winter-avg",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_aot40c(self, pollutant, year):
        """AOT40 vegetation protection (single year)."""
        sql = self._get_simple_observation_data("observations_aot40v", pollutant, year)
        self.cursor.execute(sql, {
            "aggregation_process": "AOT40c",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_hr_max(self, pollutant, year):
        """
        Annual maximum of hourly values (P1Y-hr-max).
        Uses the pre-calculated max value from observations_year_hour table.
        """
        sql = self._get_simple_observation_data("observations_year_hour", pollutant, year, "max")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-hr-max",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_hr_min(self, pollutant, year):
        """
        Annual maximum of hourly values (P1Y-hr-max).
        Uses the pre-calculated min value from observations_year_hour table.
        """
        sql = self._get_simple_observation_data("observations_year_hour", pollutant, year, "min")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-hr-min",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

     # ============================================================================

    def generate_p1y_day_max(self, pollutant, year):
        """
        Annual maximum of daily values (P1Y-day-max).
        For O3: Uses daily 8-hour max values from observations_day_8hmax table.
        For other pollutants (including CO): Uses daily means from observations_day table.
        
        Coverage is calculated as: (count of valid days / total days in year) * 100
        where valid days have cov >= 75% (sufficient hourly data).
        """
        # Only O3 uses 8-hour daily max as the base for P1Y-day-max
        if pollutant.upper() == 'O3':
            # For O3, get the maximum of daily 8h-max values
            sql = f"""
            WITH {self._get_all_sampling_points_cte(pollutant)},
            year_info AS (
                SELECT 
                    CASE 
                        WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                        ELSE 365
                    END as total_days
            )
            SELECT 
                asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant,
                %(aggregation_process)s as aggregation_process,
                %(year)s as year,
                ROUND(MAX(CASE WHEN o.cov >= %(coverage)s THEN o.val END), 3) as value,
                ROUND((COUNT(CASE WHEN o.cov >= %(coverage)s THEN 1 END)::numeric / year_info.total_days) * 100, 2) as coverage
            FROM all_sampling_points asp
            CROSS JOIN year_info
            LEFT JOIN observations_day_8hmax o ON o.sampling_point_id = asp.spo 
                AND EXTRACT(YEAR FROM o.time) = %(year)s
                AND o.val IS NOT NULL
            GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, year_info.total_days
            ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
            """
            self.cursor.execute(sql, {
                "aggregation_process": "P1Y-day-max",
                "year": year,
                "pollutant": pollutant,
                "coverage": 75
            })
        else:
            # All other pollutants (including CO) use daily mean from observations_day
            sql = f"""
            WITH {self._get_all_sampling_points_cte(pollutant)},
            year_info AS (
                SELECT 
                    CASE 
                        WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                        ELSE 365
                    END as total_days
            )
            SELECT 
                asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant,
                %(aggregation_process)s as aggregation_process,
                %(year)s as year,
                ROUND(MAX(CASE WHEN o.cov >= %(coverage)s THEN o.val END), 3) as value,
                ROUND((COUNT(CASE WHEN o.cov >= %(coverage)s THEN 1 END)::numeric / year_info.total_days) * 100, 2) as coverage
            FROM all_sampling_points asp
            CROSS JOIN year_info
            LEFT JOIN observations_day o ON o.sampling_point_id = asp.spo 
                AND EXTRACT(YEAR FROM o.time) = %(year)s
                AND o.val IS NOT NULL
            GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, year_info.total_days
            ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
            """
            self.cursor.execute(sql, {
                "aggregation_process": "P1Y-day-max",
                "year": year,
                "pollutant": pollutant,
                "coverage": 75
            })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_day_min(self, pollutant, year):
        """
        Annual minimum of daily values (P1Y-day-min).
        For O3: Uses daily 8-hour max values from observations_day_8hmax table.
        For other pollutants (including CO): Uses daily means from observations_day table.
        
        Coverage is calculated as: (count of valid days / total days in year) * 100
        where valid days have cov >= 75% (sufficient hourly data).
        """
        # Only O3 uses 8-hour daily max as the base for P1Y-day-min
        if pollutant.upper() == 'O3':
            # For O3, get the minimum of daily 8h-max values
            sql = f"""
            WITH {self._get_all_sampling_points_cte(pollutant)},
            year_info AS (
                SELECT 
                    CASE 
                        WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                        ELSE 365
                    END as total_days
            )
            SELECT 
                asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant,
                %(aggregation_process)s as aggregation_process,
                %(year)s as year,
                ROUND(MIN(CASE WHEN o.cov >= %(coverage)s THEN o.val END), 3) as value,
                ROUND((COUNT(CASE WHEN o.cov >= %(coverage)s THEN 1 END)::numeric / year_info.total_days) * 100, 2) as coverage
            FROM all_sampling_points asp
            CROSS JOIN year_info
            LEFT JOIN observations_day_8hmax o ON o.sampling_point_id = asp.spo 
                AND EXTRACT(YEAR FROM o.time) = %(year)s
                AND o.val IS NOT NULL
            GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, year_info.total_days
            ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
            """
            self.cursor.execute(sql, {
                "aggregation_process": "P1Y-day-min",
                "year": year,
                "pollutant": pollutant,
                "coverage": 75
            })
        else:
            # All other pollutants (including CO) use daily mean from observations_day
            sql = f"""
            WITH {self._get_all_sampling_points_cte(pollutant)},
            year_info AS (
                SELECT 
                    CASE 
                        WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                        ELSE 365
                    END as total_days
            )
            SELECT 
                asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant,
                %(aggregation_process)s as aggregation_process,
                %(year)s as year,
                ROUND(MIN(CASE WHEN o.cov >= %(coverage)s THEN o.val END), 3) as value,
                ROUND((COUNT(CASE WHEN o.cov >= %(coverage)s THEN 1 END)::numeric / year_info.total_days) * 100, 2) as coverage
            FROM all_sampling_points asp
            CROSS JOIN year_info
            LEFT JOIN observations_day o ON o.sampling_point_id = asp.spo 
                AND EXTRACT(YEAR FROM o.time) = %(year)s
                AND o.val IS NOT NULL
            GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, year_info.total_days
            ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
            """
            self.cursor.execute(sql, {
                "aggregation_process": "P1Y-day-min",
                "year": year,
                "pollutant": pollutant,
                "coverage": 75
            })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_day_per99(self, pollutant, year):
        """
        Annual 99th percentile of daily values (P1Y-P1D-per99).
        Uses daily values from observations_day table.
        
        Coverage is calculated as: (count of valid days / total days in year) * 100
        where valid days have cov >= 75% (sufficient hourly data).
        
        Uses PERCENTILE_DISC (discrete) per EU regulatory standard - no interpolation.
        Note: For O3, use P1Y-dmax-per99 instead (99th percentile of daily 8h-max).
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        year_info AS (
            SELECT 
                CASE 
                    WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                    ELSE 365
                END as total_days
        )
        SELECT 
            asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            ROUND((PERCENTILE_DISC(0.99) WITHIN GROUP (ORDER BY o.val))::numeric, 3) as value,
            ROUND((COUNT(CASE WHEN o.cov >= %(coverage)s THEN 1 END)::numeric / year_info.total_days) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN year_info
        LEFT JOIN observations_day o ON o.sampling_point_id = asp.spo 
            AND EXTRACT(YEAR FROM o.time) = %(year)s
            AND o.val IS NOT NULL
            AND o.cov >= %(coverage)s
        GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, year_info.total_days
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-P1D-per99",
            "year": year,
            "pollutant": pollutant,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================
    # Complex Aggregation Methods
    # ============================================================================

    def generate_p1y_consecutive_days_above_50(self, pollutant, year):
        sql = self._get_consecutive_above("observations_day", pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-3daysAbove50",
            "year": year,
            "pollutant": pollutant,
            "threshold": 50,
            "min_consecutive_days": 3,
            "coverage": 75
        })
        return self.cursor.fetchall()

    def generate_p1y_consecutive_days_above_90(self, pollutant, year):
        sql = self._get_consecutive_above("observations_day", pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-3daysAbove90",
            "year": year,
            "pollutant": pollutant,
            "threshold": 90,
            "min_consecutive_days": 3,
            "coverage": 75
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_3h_above_200(self, pollutant, year):
        if pollutant.upper() != "NO2":
            return []
        return self._generate_consecutive_hours_above_threshold(
            pollutant=pollutant,
            year=year,
            aggregation_process="P1Y-3hAbove200",
            threshold=200
        )

    def generate_p1y_3h_above_350(self, pollutant, year):
        if pollutant.upper() != "SO2":
            return []
        return self._generate_consecutive_hours_above_threshold(
            pollutant=pollutant,
            year=year,
            aggregation_process="P1Y-3hAbove350",
            threshold=350
        )

    def generate_p1y_3h_above_400(self, pollutant, year):
        if pollutant.upper() != "NO2":
            return []
        return self._generate_consecutive_hours_above_threshold(
            pollutant=pollutant,
            year=year,
            aggregation_process="P1Y-3hAbove400",
            threshold=400
        )

    def generate_p1y_3h_above_500(self, pollutant, year):
        if pollutant.upper() != "SO2":
            return []
        return self._generate_consecutive_hours_above_threshold(
            pollutant=pollutant,
            year=year,
            aggregation_process="P1Y-3hAbove500",
            threshold=500
        )

    # ============================================================================
    # 8-Hour Max Exceedance Methods
    # ============================================================================

    def generate_p1y_8hdmx_above_10(self, pollutant, year):
        """
        Count of days where 8-hour daily max exceeds 10 mg/m³ (CO).
        Uses observations_day_8hmax materialized view.
        Applies 75% coverage threshold for valid days.
        """
        sql = self._get_count_observation_data("observations_day_8hmax", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-8hdmxAbove10",
            "year": year,
            "pollutant": pollutant,
            "threshold": 10,
            "coverage": 75  # Apply standard 75% coverage requirement
        })
        return self.cursor.fetchall()

    def generate_p1y_dmax_above_100(self, pollutant, year):
        """
        Count of days where 8-hour daily max exceeds 100 µg/m³ (O3).
        Uses observations_day_8hmax materialized view.
        No daily coverage check needed - 8h max already includes coverage validation.
        """
        sql = self._get_count_observation_data("observations_day_8hmax", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-dmaxAbove100",
            "year": year,
            "pollutant": pollutant,
            "threshold": 100,
            "coverage": 0  # No daily coverage requirement - 8h-max has built-in validation
        })
        return self.cursor.fetchall()

    def generate_p1y_dmax_above_120(self, pollutant, year):
        """
        Count of days where 8-hour daily max exceeds 120 µg/m³ (O3).
        Uses observations_day_8hmax materialized view.
        No daily coverage check needed - 8h max already includes coverage validation.
        """
        sql = self._get_count_observation_data("observations_day_8hmax", pollutant, "val", ">")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-dmaxAbove120",
            "year": year,
            "pollutant": pollutant,
            "threshold": 120,
            "coverage": 0  # No daily coverage requirement - 8h-max has built-in validation
        })
        return self.cursor.fetchall()

    # ============================================================================
    # Percentile Methods
    # ============================================================================

    def generate_p1y_dmax_per99(self, pollutant, year):
        """
        99th percentile of daily 8-hour max values (P1Y-dmax-per99).
        Uses observations_day_8hmax materialized view.
        Calculates the 99th percentile of all daily 8h-max values in the year.
        """
        sql = self._get_percentile_observation_data("observations_day_8hmax", pollutant, "val", 0.99)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-dmax-per99",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

    # ============================================================================
    # Multi-Year Aggregation Methods
    # ============================================================================

    def generate_p3y_dmax_above_120(self, pollutant, year):
        """
        3-year average of days with 8h-max above 120 µg/m³ (P3Y-dmaxAbove120).
        Calculates the average count over 3 consecutive years (year-2, year-1, year).
        Uses observations_day_8hmax materialized view.
        
        Returns:
            - value: Average count over 3 years (NULL if insufficient data)
            - coverage: Percentage of required years available (0-100%, based on 3-year requirement)
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        yearly_counts AS (
            SELECT 
                asp.spo,
                EXTRACT(YEAR FROM o.time)::INTEGER as year,
                COUNT(CASE WHEN o.val > 120 THEN 1 END) as count_above_120
            FROM all_sampling_points asp
            JOIN observations_day_8hmax o ON o.sampling_point_id = asp.spo
                AND EXTRACT(YEAR FROM o.time) BETWEEN %(year)s - 2 AND %(year)s
                AND o.val IS NOT NULL
            GROUP BY asp.spo, EXTRACT(YEAR FROM o.time)
        ),
        aggregated AS (
            SELECT 
                spo,
                COUNT(DISTINCT year) as years_with_data,
                CASE 
                    WHEN COUNT(DISTINCT year) = 3 THEN 
                        ROUND(AVG(count_above_120), 1)
                    ELSE NULL
                END as avg_count
            FROM yearly_counts
            GROUP BY spo
        )
        SELECT 
            asp.network,
            asp.eoi,
            asp.station,
            asp.code,
            asp.spo,
            asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            aggregated.avg_count as value,
            ROUND((COALESCE(aggregated.years_with_data, 0)::numeric / 3) * 100, 2) as coverage
        FROM all_sampling_points asp
        LEFT JOIN aggregated ON aggregated.spo = asp.spo
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        self.cursor.execute(sql, {
            "aggregation_process": "P3Y-dmaxAbove120",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

    # ============================================================================
    # SOMO (Sum of Ozone Means Over threshold) Methods
    # ============================================================================

    def generate_somo10(self, pollutant, year):
        """
        SOMO10: Sum of Ozone Means Over 10 ppb.
        Calculates sum of (daily_8h_max - 20 µg/m³) for all days where daily_8h_max > 20 µg/m³.
        Uses observations_day_8hmax materialized view.
        
        Unit conversion at 20°C: 10 ppb ≈ 20 µg/m³
        
        Returns:
            - value: Sum of excesses over threshold (µg/m³·days)
            - coverage: Percentage of valid days with data (0-100%)
        """
        threshold = 20  # 10 ppb ≈ 20 µg/m³ at 20°C
        
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        year_info AS (
            SELECT 
                CASE 
                    WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                    ELSE 365
                END as total_days
        ),
        daily_excess AS (
            SELECT 
                asp.spo,
                o.time,
                CASE 
                    WHEN o.val > %(threshold)s THEN o.val - %(threshold)s
                    ELSE 0
                END as excess
            FROM all_sampling_points asp
            LEFT JOIN observations_day_8hmax o ON o.sampling_point_id = asp.spo
                AND EXTRACT(YEAR FROM o.time) = %(year)s
                AND o.val IS NOT NULL
        ),
        aggregated AS (
            SELECT 
                spo,
                ROUND(SUM(excess), 1) as total_excess,
                COUNT(*) as total_valid_days
            FROM daily_excess
            GROUP BY spo
        )
        SELECT 
            asp.network,
            asp.eoi,
            asp.station,
            asp.code,
            asp.spo,
            asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            COALESCE(aggregated.total_excess, 0) as value,
            ROUND((COALESCE(aggregated.total_valid_days, 0)::numeric / year_info.total_days) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN year_info
        LEFT JOIN aggregated ON aggregated.spo = asp.spo
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        self.cursor.execute(sql, {
            "aggregation_process": "SOMO10",
            "year": year,
            "pollutant": pollutant,
            "threshold": threshold
        })
        return self.cursor.fetchall()

    def generate_somo35(self, pollutant, year):
        """
        SOMO35: Sum of Ozone Means Over 35 ppb.
        Calculates sum of (daily_8h_max - 70 µg/m³) for all days where daily_8h_max > 70 µg/m³.
        Uses observations_day_8hmax materialized view.
        
        Unit conversion at 20°C: 35 ppb ≈ 70 µg/m³
        
        Returns:
            - value: Sum of excesses over threshold (µg/m³·days)
            - coverage: Percentage of valid days with data (0-100%)
        """
        threshold = 70  # 35 ppb ≈ 70 µg/m³ at 20°C
        
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        year_info AS (
            SELECT 
                CASE 
                    WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                    ELSE 365
                END as total_days
        ),
        daily_excess AS (
            SELECT 
                asp.spo,
                o.time,
                CASE 
                    WHEN o.val > %(threshold)s THEN o.val - %(threshold)s
                    ELSE 0
                END as excess
            FROM all_sampling_points asp
            LEFT JOIN observations_day_8hmax o ON o.sampling_point_id = asp.spo
                AND EXTRACT(YEAR FROM o.time) = %(year)s
                AND o.val IS NOT NULL
        ),
        aggregated AS (
            SELECT 
                spo,
                ROUND(SUM(excess), 1) as total_excess,
                COUNT(*) as total_valid_days
            FROM daily_excess
            GROUP BY spo
        )
        SELECT 
            asp.network,
            asp.eoi,
            asp.station,
            asp.code,
            asp.spo,
            asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            COALESCE(aggregated.total_excess, 0) as value,
            ROUND((COALESCE(aggregated.total_valid_days, 0)::numeric / year_info.total_days) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN year_info
        LEFT JOIN aggregated ON aggregated.spo = asp.spo
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        self.cursor.execute(sql, {
            "aggregation_process": "SOMO35",
            "year": year,
            "pollutant": pollutant,
            "threshold": threshold
        })
        return self.cursor.fetchall()

    # ============================================================================
    # Hourly Exceedance Count Methods
    # ============================================================================

    def generate_p1y_hrs_above_150(self, pollutant, year):
        """
        Count of hours exceeding 150 µg/m³ (NO2).
        Uses hourly observations table.
        """
        sql = self._get_hourly_count_sql(pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-hrsAbove150",
            "year": year,
            "pollutant": pollutant,
            "threshold": 150
        })
        return self.cursor.fetchall()

    def generate_p1y_hrs_above_180(self, pollutant, year):
        """
        Count of hours exceeding 180 µg/m³ (O3).
        Uses hourly observations table.
        """
        sql = self._get_hourly_count_sql(pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-hrsAbove180",
            "year": year,
            "pollutant": pollutant,
            "threshold": 180
        })
        return self.cursor.fetchall()

    def generate_p1y_hrs_above_200(self, pollutant, year):
        """
        Count of hours exceeding 200 µg/m³ (NO2).
        Uses hourly observations table.
        """
        sql = self._get_hourly_count_sql(pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-hrsAbove200",
            "year": year,
            "pollutant": pollutant,
            "threshold": 200
        })
        return self.cursor.fetchall()

    def generate_p1y_hrs_above_240(self, pollutant, year):
        """
        Count of hours exceeding 240 µg/m³ (O3).
        Uses hourly observations table.
        """
        sql = self._get_hourly_count_sql(pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-hrsAbove240",
            "year": year,
            "pollutant": pollutant,
            "threshold": 240
        })
        return self.cursor.fetchall()

    def generate_p1y_hrs_above_275(self, pollutant, year):
        """
        Count of hours exceeding 275 µg/m³ (SO2).
        Uses hourly observations table.
        """
        sql = self._get_hourly_count_sql(pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-hrsAbove275",
            "year": year,
            "pollutant": pollutant,
            "threshold": 275
        })
        return self.cursor.fetchall()

    def generate_p1y_hrs_above_350(self, pollutant, year):
        """
        Count of hours exceeding 350 µg/m³ (SO2).
        Uses hourly observations table.
        """
        sql = self._get_hourly_count_sql(pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-hrsAbove350",
            "year": year,
            "pollutant": pollutant,
            "threshold": 350
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_aot40c_p5y(self, pollutant, year):
        """
        AOT40 vegetation protection (AOT40) averaged over 5 years.
        Following Directive 2008/50/EC: If the three or five year averages cannot be 
        determined on the basis of a full and consecutive set of annual data, the 
        minimum annual data required for checking compliance with the target values 
        will be as follows for the target value for the protection of vegetation: 
        valid data for three years.

        Returns ALL sampling points, with value=NULL for insufficient data.
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        aot40_data AS (
            SELECT 
                asp.spo,
                EXTRACT(YEAR FROM o.time) as data_year,
                o.val as annual_value,
                o.cov as annual_coverage
            FROM all_sampling_points asp
            JOIN observations_aot40v o ON o.sampling_point_id = asp.spo
                AND EXTRACT(YEAR FROM o.time) BETWEEN (%(year)s - 4) AND %(year)s
                AND o.val IS NOT NULL
        ),
        yearly_counts AS (
            SELECT 
                spo,
                COUNT(*) as available_years,
                ARRAY_AGG(data_year ORDER BY data_year) as years_available,
                ROUND(AVG(annual_value), 3) as five_year_avg,
                ROUND(AVG(annual_coverage), 2) as avg_coverage
            FROM aot40_data
            GROUP BY spo
        )
        SELECT 
            asp.network, asp.eoi, asp.station, asp.spo, asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            CASE 
                WHEN yc.available_years >= 5 THEN yc.five_year_avg  -- Full 5-year average
                WHEN yc.available_years >= 3 THEN yc.five_year_avg  -- Minimum 3 years as per directive
                ELSE NULL  -- Insufficient data
            END as value,
            COALESCE(yc.avg_coverage, NULL) as coverage,
            COALESCE(yc.available_years, 0) as available_years,
            COALESCE(yc.years_available, ARRAY[]::integer[]) as years_available
        FROM all_sampling_points asp
        LEFT JOIN yearly_counts yc ON asp.spo = yc.spo
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """

        self.cursor.execute(sql, {
            "aggregation_process": "AOT40c-P5Y",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()
    # ============================================================================
    # Private Helper Methods
    # ============================================================================

    def _get_all_sampling_points_cte(self, pollutant):
        """Common CTE to get all sampling points for a pollutant"""
        return """
        all_sampling_points AS (
            SELECT DISTINCT
                n.name as network, 
                st.eoi_code as eoi, 
                st.name as station, 
                sp.id as code,
                sp.id as spo, 
                p.notation as pollutant
            FROM sampling_points sp
            JOIN eea_pollutants p ON sp.pollutant = p.uri
            JOIN stations st ON sp.station_id = st.id
            JOIN networks n ON st.network_id = n.id
            WHERE LOWER(p.notation) = LOWER(%(pollutant)s)
        )"""

    # ============================================================================

    def _get_simple_observation_data(self, table_name, pollutant, year, value_column="val"):
        """Get simple observation data from a specific table for a year

          Args:
              table_name: Name of the observation table (e.g., 'observations_year')
              pollutant: Pollutant notation to filter by
              year: Year to filter by
              value_column: Column to use for value ('val', 'min', or 'max')
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)}
        SELECT 
            asp.network, asp.eoi, asp.station, asp.spo, asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            ROUND(o.{value_column}, 3) as value,
            ROUND(o.cov, 2) as coverage
        FROM all_sampling_points asp
        LEFT JOIN {table_name} o ON o.sampling_point_id = asp.spo 
            AND EXTRACT(YEAR FROM o.time) = %(year)s
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        return sql

    def _get_count_observation_data(self, table_name, pollutant, value_column="val",  comparison_operator=">"):
        """Get count of observation data above/below a threshold from a specific table for a year

        Args:
            table_name: Name of the observation table (e.g., 'observations_day')
            pollutant: Pollutant notation to filter by
            year: Year to filter by
            threshold: Threshold value to compare against
            comparison_operator: Comparison operator ('>', '>=', '<', '<=', '=')
            value_column: Column to use for comparison ('val', 'min', 'max', 'p99')

        Returns count of values meeting threshold criteria, with coverage as percentage of valid data.
        """
        # Determine expected count based on table type
        if 'day' in table_name:
            expected_count_sql = "CASE WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366 ELSE 365 END"
        else:  # hourly table
            expected_count_sql = "CASE WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 8784 ELSE 8760 END"
        
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        expected_info AS (
            SELECT {expected_count_sql} as expected_count
        )
        SELECT 
            asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            COUNT(CASE WHEN ROUND(o.{value_column}::numeric, 0) {comparison_operator} %(threshold)s AND o.cov >= %(coverage)s THEN 1 END) as value,
            ROUND((COUNT(CASE WHEN o.cov >= %(coverage)s THEN 1 END)::numeric / expected_info.expected_count) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN expected_info
        LEFT JOIN {table_name} o ON o.sampling_point_id = asp.spo 
            AND EXTRACT(YEAR FROM o.time) = %(year)s
            AND o.{value_column} IS NOT NULL
        GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, expected_info.expected_count
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        return sql

    def _get_percentile_observation_data(self, table_name, pollutant, value_column="val", percentile=0.99):
        """Get percentile of observation data from a specific table for a year

        Args:
            table_name: Name of the observation table (e.g., 'observations_day_8hmax')
            pollutant: Pollutant notation to filter by
            value_column: Column to use for percentile calculation ('val', 'min', 'max')
            percentile: Percentile to calculate (0.0-1.0, e.g., 0.99 for 99th percentile)

        Returns percentile value with coverage as percentage of valid observations (0-100%).
        Uses PERCENTILE_DISC (discrete) per EU regulatory standard - no interpolation.
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        year_info AS (
            SELECT 
                CASE 
                    WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                    ELSE 365
                END as total_days
        )
        SELECT 
            asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            ROUND(CAST(PERCENTILE_DISC({percentile}) WITHIN GROUP (ORDER BY o.{value_column}) AS numeric), 3) as value,
            ROUND((COUNT(o.{value_column})::numeric / year_info.total_days) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN year_info
        LEFT JOIN {table_name} o ON o.sampling_point_id = asp.spo 
            AND EXTRACT(YEAR FROM o.time) = %(year)s
            AND o.{value_column} IS NOT NULL
        GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, year_info.total_days
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        return sql

    def _get_consecutive_above(self, table_name, pollutant):
        """
        Count periods of consecutive days above a threshold value.

        Args:
            table_name: Name of the observation table (e.g., 'observations_day')
            pollutant: Pollutant notation


        Returns count of qualifying consecutive periods, with coverage as percentage of valid days.
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        expected_info AS (
            SELECT 
                CASE 
                    WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 366
                    ELSE 365
                END as total_days
        ),
        daily_data AS (
            SELECT 
                asp.spo,
                o.time,
                CASE WHEN o.val > %(threshold)s AND o.cov >= %(coverage)s THEN 1 ELSE 0 END as above_threshold,
                CASE WHEN o.cov >= %(coverage)s THEN 1 ELSE 0 END as valid_day
            FROM all_sampling_points asp
            JOIN {table_name} o ON o.sampling_point_id = asp.spo 
                AND EXTRACT(YEAR FROM o.time) = %(year)s
                AND o.val IS NOT NULL
            ORDER BY asp.spo, o.time
        ),
        valid_day_counts AS (
            SELECT 
                spo,
                SUM(valid_day) as total_valid_days
            FROM daily_data
            GROUP BY spo
        ),
        consecutive_groups AS (
            SELECT 
                spo,
                above_threshold,
                -- Create groups of consecutive days above threshold
                SUM(CASE WHEN above_threshold = 0 THEN 1 ELSE 0 END) 
                    OVER (PARTITION BY spo ORDER BY time) as group_id
            FROM daily_data
        ),
        consecutive_periods AS (
            SELECT 
                spo,
                COUNT(*) as consecutive_days
            FROM consecutive_groups
            WHERE above_threshold = 1
            GROUP BY spo, group_id
            HAVING COUNT(*) >= %(min_consecutive_days)s
        ),
        period_counts AS (
            SELECT 
                spo,
                COUNT(*) as qualifying_periods
            FROM consecutive_periods
            GROUP BY spo
        )
        SELECT 
            asp.network, asp.eoi, asp.station, asp.spo, asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            COALESCE(pc.qualifying_periods, 0) as value,
            ROUND((COALESCE(vdc.total_valid_days, 0)::numeric / expected_info.total_days) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN expected_info
        LEFT JOIN period_counts pc ON asp.spo = pc.spo
        LEFT JOIN valid_day_counts vdc ON asp.spo = vdc.spo
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """

        return sql

    def _generate_consecutive_hours_above_threshold(self, pollutant, year, aggregation_process, threshold):
        sql = self._get_consecutive_hours_sql(pollutant)
        self.cursor.execute(sql, {
            "aggregation_process": aggregation_process,
            "year": year,
            "pollutant": pollutant,
            "threshold": threshold
        })
        return self.cursor.fetchall()

    def _get_consecutive_hours_sql(self, pollutant):
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        hourly_data AS (
            SELECT 
                asp.network,
                asp.eoi,
                asp.station,
                asp.code,
                asp.spo,
                asp.pollutant,
                o.from_time as time,
                o.value as val,
                LAG(o.value, 1) OVER (PARTITION BY asp.spo ORDER BY o.from_time) as prev_val_1,
                LAG(o.value, 2) OVER (PARTITION BY asp.spo ORDER BY o.from_time) as prev_val_2,
                LAG(o.from_time, 1) OVER (PARTITION BY asp.spo ORDER BY o.from_time) as prev_time_1,
                LAG(o.from_time, 2) OVER (PARTITION BY asp.spo ORDER BY o.from_time) as prev_time_2
            FROM all_sampling_points asp
            JOIN observations o ON o.sampling_point_id = asp.spo
                AND EXTRACT(YEAR FROM o.from_time) = %(year)s
                AND o.value IS NOT NULL
                AND o.validation_flag >= 1
        ),
        consecutive_windows AS (
            SELECT 
                network,
                eoi,
                station,
                code,
                spo,
                pollutant,
                CASE 
                    WHEN val > %(threshold)s
                        AND prev_val_1 > %(threshold)s
                        AND prev_val_2 > %(threshold)s
                        AND prev_time_1 IS NOT NULL
                        AND prev_time_2 IS NOT NULL
                        AND time = prev_time_1 + INTERVAL '1 hour'  -- Match production: 'time' column
                        AND prev_time_1 = prev_time_2 + INTERVAL '1 hour'
                    THEN 1 ELSE 0
                END AS is_window
            FROM hourly_data
        ),
        aggregated AS (
            SELECT 
                network,
                eoi,
                station,
                code,
                spo,
                pollutant,
                SUM(is_window)::INTEGER as window_count,
                COUNT(*) as total_hours
            FROM consecutive_windows
            GROUP BY network, eoi, station, code, spo, pollutant
        ),
        expected_info AS (
            SELECT 
                CASE 
                    WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 8784
                    ELSE 8760
                END as expected_hours
        )
        SELECT 
            asp.network,
            asp.eoi,
            asp.station,
            asp.code,
            asp.spo,
            asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            COALESCE(aggregated.window_count, 0) as value,
            ROUND((COALESCE(aggregated.total_hours, 0)::numeric / expected_info.expected_hours) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN expected_info
        LEFT JOIN aggregated ON aggregated.spo = asp.spo
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        return sql

    def _get_hourly_count_sql(self, pollutant):
        """
        Get SQL for counting hourly observations above a threshold.
        
        For hourly observations table, we count validated data (validation_flag >= 1).
        Coverage represents percentage of valid hourly measurements in the year.
        
        Returns SQL string for hourly exceedance counts with coverage percentage.
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        expected_info AS (
            SELECT 
                CASE 
                    WHEN (%(year)s %% 4 = 0 AND %(year)s %% 100 <> 0) OR (%(year)s %% 400 = 0) THEN 8784
                    ELSE 8760
                END as expected_hours
        )
        SELECT 
            asp.network,
            asp.eoi,
            asp.station,
            asp.code,
            asp.spo,
            asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            COUNT(CASE WHEN ROUND(o.value::numeric, 0) > %(threshold)s THEN 1 END) as value,
            ROUND((COUNT(o.value)::numeric / expected_info.expected_hours) * 100, 2) as coverage
        FROM all_sampling_points asp
        CROSS JOIN expected_info
        LEFT JOIN observations o ON o.sampling_point_id = asp.spo 
            AND EXTRACT(YEAR FROM o.from_time) = %(year)s
            AND o.value IS NOT NULL
            AND o.validation_flag >= 1
        GROUP BY asp.network, asp.eoi, asp.station, asp.code, asp.spo, asp.pollutant, expected_info.expected_hours
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        return sql

