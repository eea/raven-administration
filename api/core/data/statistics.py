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
        """Winter season average data."""
        sql = self._get_simple_observation_data("observations_winter_season", pollutant, year)
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
        Uses the pre-calculated max value from observations_year_day table.
        """
        sql = self._get_simple_observation_data("observations_year_day", pollutant, year, "max")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-day-max",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_day_min(self, pollutant, year):
        """
        Annual minimum of daily values (P1Y-day-min).
        Uses the pre-calculated min value from observations_year_day table.
        """
        sql = self._get_simple_observation_data("observations_year_day", pollutant, year, "min")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-day-min",
            "year": year,
            "pollutant": pollutant
        })
        return self.cursor.fetchall()

    # ============================================================================

    def generate_p1y_day_per99(self, pollutant, year):
        """
        Annual p99 of daily values (P1Y-day-per99).
        Uses the pre-calculated p99 value from observations_year_day table.
        """
        sql = self._get_simple_observation_data("observations_year_day", pollutant, year, "p99")
        self.cursor.execute(sql, {
            "aggregation_process": "P1Y-day-per99",
            "year": year,
            "pollutant": pollutant
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

        Returns count of values meeting the threshold criteria, with coverage as NULL.
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)}
        SELECT 
            asp.network, asp.eoi, asp.station, asp.spo, asp.pollutant,
            %(aggregation_process)s as aggregation_process,
            %(year)s as year,
            COUNT(CASE WHEN o.{value_column} {comparison_operator} %(threshold)s AND o.cov >= %(coverage)s THEN 1 END) as value,
            NULL as coverage
        FROM all_sampling_points asp
        LEFT JOIN {table_name} o ON o.sampling_point_id = asp.spo 
            AND EXTRACT(YEAR FROM o.time) = %(year)s
            AND o.{value_column} IS NOT NULL
        GROUP BY asp.network, asp.eoi, asp.station, asp.spo, asp.pollutant
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """
        return sql

    def _get_consecutive_above(self, table_name, pollutant):
        """
        Count periods of consecutive days above a threshold value.

        Args:
            table_name: Name of the observation table (e.g., 'observations_day')
            pollutant: Pollutant notation


        Returns count of qualifying consecutive periods, with coverage as None.
        """
        sql = f"""
        WITH {self._get_all_sampling_points_cte(pollutant)},
        daily_data AS (
            SELECT 
                asp.spo,
                o.time,
                CASE WHEN o.val > %(threshold)s AND o.cov >= %(coverage)s THEN 1 ELSE 0 END as above_threshold
            FROM all_sampling_points asp
            JOIN {table_name} o ON o.sampling_point_id = asp.spo 
                AND EXTRACT(YEAR FROM o.time) = %(year)s
                AND o.val IS NOT NULL
            ORDER BY asp.spo, o.time
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
            NULL as coverage
        FROM all_sampling_points asp
        LEFT JOIN period_counts pc ON asp.spo = pc.spo
        ORDER BY asp.network, asp.station, asp.spo, asp.pollutant;
        """

        return sql
