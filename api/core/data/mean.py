from enum import IntEnum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import parse_obj_as
from typing import List


# class MeanValue(BaseModel):
#     sp_id: str
#     oc_id: str
#     datetime: datetime
#     value: Optional[float]
#     coverage: int
#     count: int
#     meantype: int
#     est_value: Optional[float]
#     station: Optional[str]
#     component: Optional[str]
#     unit: Optional[str]
#     timestep: Optional[str]
#     lng: Optional[float]
#     lat: Optional[float]

#     def __getitem__(self, key):
#         return super().__getattribute__(key)


# class MeanValues(BaseModel):
#     meanvalues: list[MeanValue]


class MeanType(IntEnum):
    Original = 0,
    Hour = 1,
    Day = 2,
    MovingEightHour = 3,
    Year = 4,
    MovingDay = 5,
    MovingEightHourMax = 6,
    Month = 7,
    WinterYear = 8,
    Aot40Vegetation = 9,
    Aot40ForestProtection = 10,
    WinterSeason = 11,
    SummerYear = 12,
    Period = 999,
    Raw = 1000


class Mean:
    def __init__(self, sql, params):
        self.Sql = sql
        self.Params = params

    Sql = None
    Params = None

    @staticmethod
    def Aggregate(cursor: any, meanType: MeanType, ids: tuple, fromTime: str, toTime: str, coverage: int = 75, verificationFlag: int = 3, fraction: int = 10, addMetadata: bool = False, useInvalidValues: bool = False):
        sql = ""
        params = {"ids": ids, "fromTime": fromTime, "toTime": toTime, "verificationFlag": verificationFlag, "coverage": coverage, "fraction": fraction, "useInvalidValues": useInvalidValues}

        if meanType == MeanType.Original:
            sql = Mean.Original()
        elif meanType == MeanType.Hour:
            sql = Mean.Hour()
        elif meanType == MeanType.Day:
            sql = Mean.Day()
        elif meanType == MeanType.MovingEightHour:
            sql = Mean.MovingEightHour()
        elif meanType == MeanType.Year:
            sql = Mean.Year()
        elif meanType == MeanType.MovingDay:
            sql = Mean.MovingDay()
        elif meanType == MeanType.MovingEightHourMax:
            sql = Mean.MovingEightHourMax()
        elif meanType == MeanType.Month:
            sql = Mean.Month()
        elif meanType == MeanType.WinterYear:
            sql = Mean.WinterYear()
        elif meanType == MeanType.Aot40Vegetation:
            sql = Mean.Aot40Vegetation()
        elif meanType == MeanType.Aot40ForestProtection:
            sql = Mean.Aot40ForestProtection()
        elif meanType == MeanType.WinterSeason:
            sql = Mean.WinterSeason()
        elif meanType == MeanType.SummerYear:
            sql = Mean.SummerYear()
        elif meanType == MeanType.Period:
            sql = Mean.Period()
        elif meanType == MeanType.Raw:
            sql = Mean.Raw()
        else:
            raise Exception("Meantype not found")

        m = Mean(sql, params)
        cursor.execute(m.Sql, m.Params)
        rows = cursor.fetchall()

        if addMetadata:
            timeseries = Mean.GetTimeseries(ids, cursor)
            for r in rows:
                t = next(filter(lambda x: x["sampling_point_id"] == r["sampling_point_id"], timeseries))
                r["station"] = t["station"]
                r["component"] = t["component"]
                r["unit"] = t["unit"]
                r["timestep"] = t["timestep"]
                r["lng"] = t["lng"]
                r["lat"] = t["lat"]

        return rows
        # return MeanValues(meanvalues=rows)

    @staticmethod
    def GetTimeseries(ids: tuple, cursor: any):
        sql = """
            select spo.id "sampling_point_id", sta.name "station", COALESCE(NULLIF(po.notation, ''), po.label) "component", ti.label "timestep", con.notation "unit", sta.longitude "lng", sta.latitude "lat"
            from stations sta, sampling_points spo, eea_pollutants po, eea_times ti, eea_concentrations con
            where 1=1
            and sta.id = spo.station_id
            and spo.pollutant_id = po.id
            and spo.time_resolution_id = ti.id
            and spo.unit_id = con.id
            and spo.id in %(ids)s
        """
        cursor.execute(sql, {"ids": ids})
        return cursor.fetchall()

    ##########
    ## SQLS ##
    ##########

    @staticmethod
    def Raw():
        sql = """
            SELECT
                to_char (o.to_time, 'YYYY-MM-DD HH24:MI:SS') as "datetime", 
                CASE
                    WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.import_value != -9900)
                    THEN  ROUND(o.import_value,%(fraction)s)::double PRECISION
                    ELSE NULL
                END as "value",
                100 as "coverage",                   
                1 as "cnt",                 
                o.sampling_point_id as "sampling_point_id",   
                0 "meantype"             
            FROM
                observations o
            WHERE 1=1
            AND o.from_time >= %(fromTime)s
            AND o.from_time < %(toTime)s
            AND  o.sampling_point_id IN %(ids)s
        """
        return sql

    @staticmethod
    def Original():
        sql = """
            SELECT
                to_char (o.to_time, 'YYYY-MM-DD HH24:MI:SS') as "datetime", 
                CASE
                    WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900)
                    THEN  ROUND(o.value,%(fraction)s)::double PRECISION
                    ELSE NULL
                END as "value",
                100 as "coverage",                   
                1 as "cnt",                 
                o.sampling_point_id as "sampling_point_id",   
                0 "meantype"             
            FROM
                observations o
            WHERE 1=1
            AND o.from_time >= %(fromTime)s
            AND o.from_time < %(toTime)s
            AND  o.sampling_point_id IN %(ids)s
        """
        return sql

    @staticmethod
    def Hour():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1 
                AND o.from_time >= %(fromTime)s
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
            )
            SELECT 
                to_char (DATETIME + interval '1' HOUR, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN ROUND(cnt/(3600/TM.timestep::float)*100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                    ELSE NULL 
                END "value",
                ROUND(cnt/(3600/TM.timestep::float)*100) "coverage",
                CNT "cnt",
                SP.ID "sampling_point_id",
                1 "meantype"                    
            FROM
            (
                SELECT 
                    DATE_TRUNC('hour',TE.from_time) DATETIME, 
                    AVG(TE.val) val,
                    COUNT(TE.val) cnt,
                    TE.sampling_point_id
                FROM
                    TIMEVALUES TE
                WHERE 1=1                        
                GROUP BY TE.sampling_point_id, DATE_TRUNC('hour',TE.from_time)
                ORDER BY TE.sampling_point_id, DATE_TRUNC('hour',TE.from_time)
            ) C,
            sampling_points SP,  eea_times TM
            WHERE C.sampling_point_id = SP.id
            AND SP.time_resolution_id = TM.id  
        """
        return sql

    @staticmethod
    def Day():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1 
                AND o.from_time >= %(fromTime)s
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
            )
            SELECT 
                to_char (DateTime, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN ROUND(cnt/(86400/TM.timestep::float)*100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                    ELSE NULL 
                END "value",
                ROUND(cnt/(86400/TM.timestep::float)*100) "coverage",
                CNT "cnt",
                SP.ID "sampling_point_id",
                2 "meantype"                      
            FROM
            (
                SELECT 
                    DATE_TRUNC('day',TE.from_time) DATETIME, 
                    AVG(TE.val) val,
                    COUNT(TE.val) cnt,
                    TE.sampling_point_id
                FROM
                    TIMEVALUES TE
                WHERE 1=1
                GROUP BY TE.sampling_point_id, DATE_TRUNC('day',TE.from_time)
                ORDER BY TE.sampling_point_id, DATE_TRUNC('day',TE.from_time)
            ) C,
            sampling_points SP, eea_times TM
            WHERE C.sampling_point_id = SP.id
            AND SP.time_resolution_id = TM.id
        """
        return sql

    @staticmethod
    def MovingEightHour():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1  
                AND o.from_time >= %(fromTime)s::timestamp - interval '7' hour
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
            )
            SELECT             
                to_char (C.DATETIME + interval '1' HOUR, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN ROUND(cnt/(28800/TM.timestep::float)*100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                    ELSE NULL 
                END "value",
                ROUND(cnt/(28800/TM.timestep::float)*100) "coverage",
                CNT "cnt",
                SP.ID "sampling_point_id",
                3 "meantype"     
            FROM
            (
                SELECT 
                    A.from_time DATETIME, 
                    AVG(A.val) OVER (partition by A.sampling_point_id ORDER BY A.from_time RANGE BETWEEN '7 hour' PRECEDING AND current row) val,
                    COUNT(A.val) OVER (partition by A.sampling_point_id ORDER BY A.from_time RANGE BETWEEN '7 hour' PRECEDING AND current row) cnt,
                    A.sampling_point_id
                FROM TIMEVALUES A
            ) C,
            sampling_points SP, eea_times TM
            WHERE C.sampling_point_id = SP.id
            AND SP.time_resolution_id = TM.id
            AND C.DATETIME >= %(fromTime)s
            ORDER BY SP.id,C.DATETIME
        """
        return sql

    @staticmethod
    def Year():
        sql = """
            WITH timevalues as 
            (
                    SELECT 
                        o.from_time, o.to_time, o.sampling_point_id,
                        CASE 
                            WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s)  AND (o.value != -9900) THEN  o.value
                            ELSE NULL 
                        END val
                    FROM
                        observations o 
                    WHERE 1=1 
                    AND o.from_time >= %(fromTime)s
                    AND o.from_time < %(toTime)s
                    AND o.sampling_point_id IN %(ids)s
            )
            SELECT 
                to_char (DateTime, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN ROUND(cnt*TM.timestep / ((extract(days from(DateTime + interval '12 month') - DateTime))*86400)::float*100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION                        
                    ELSE NULL 
                END "value",
                CASE TM.timestep
                    WHEN 31536000 THEN 
                        CASE cnt 
                            WHEN 0 THEN 0 ELSE 100 
                        END 
                    ELSE ROUND(cnt*TM.timestep / ((extract(days from(DateTime + interval '12 month') - DateTime))*86400)::float*100) 
                END "coverage",
                CNT "cnt",
                SP.ID "sampling_point_id",
                4 "meantype"                      
            FROM
            (
                SELECT 
                    DATE_TRUNC('year',TE.from_time) DATETIME, 
                    AVG(TE.val) val,
                    COUNT(TE.val) cnt,
                    TE.sampling_point_id
                FROM
                    TIMEVALUES TE
                WHERE 1=1
                GROUP BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
                ORDER BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
            ) C,
            sampling_points SP, eea_times TM
            WHERE C.sampling_point_id = SP.id
            AND SP.time_resolution_id = TM.id
        """
        return sql

    @staticmethod
    def MovingEightHourMax():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1 
                AND o.from_time >= %(fromTime)s::timestamp - interval '7' hour
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id  IN %(ids)s
            )
            SELECT            
                to_char (DATE_TRUNC('day',B.DATETIME), 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN ROUND(COUNT(B.val)/(86400/B.timestep::float)*100) >= %(coverage)s THEN ROUND(MAX(B.val),%(fraction)s)::double PRECISION
                    ELSE NULL 
                END "value",
                ROUND(COUNT(B.val)/(86400/B.timestep::float)*100) "coverage",
                COUNT(B.val) "cnt",
                B.sampling_point_id "sampling_point_id",
                6 "meantype" 
            FROM
            ( 
                SELECT C.DATETIME, C.cnt, TM.timestep, C.sampling_point_id,
                CASE WHEN C.cnt >= (75*(28800/TM.timestep::float)/100) THEN C.val ELSE NULL END val
                FROM
                (
                    SELECT 
                        A.from_time DATETIME, 
                        AVG(A.val) OVER (partition by A.sampling_point_id ORDER BY A.from_time RANGE BETWEEN '7 hour' PRECEDING AND current row) val,
                        COUNT(A.val) OVER (partition by A.sampling_point_id ORDER BY A.from_time RANGE BETWEEN '7 hour' PRECEDING AND current row) cnt,
                        A.sampling_point_id
                    FROM TIMEVALUES A                   
                ) C,
                sampling_points SP, eea_times TM
                WHERE C.sampling_point_id = SP.id
                AND SP.time_resolution_id = TM.id
                AND C.DATETIME >= %(fromTime)s
            ) B
            GROUP BY DATE_TRUNC('day',B.DATETIME), B.timestep, B.sampling_point_id
            ORDER BY B.sampling_point_id , DATE_TRUNC('day',B.DATETIME)
        """
        return sql

    @staticmethod
    def MovingDay():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1 
                AND o.from_time >= %(fromTime)s::timestamp - interval '23' hour
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
            )
            SELECT 
                to_char (DateTime + interval '1' hour, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN ROUND(cnt/(86400/TM.timestep::float)*100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                    ELSE NULL 
                END "value",
                ROUND(cnt/(86400/TM.timestep::float)*100) "coverage",
                CNT "cnt",
                SP.ID "sampling_point_id",
                5 "meantype"                      
            FROM
            (
                SELECT 
                    TE.from_time DATETIME, 
                    AVG(TE.val) OVER (partition by TE.sampling_point_id ORDER BY TE.from_time RANGE BETWEEN '23 hour' PRECEDING AND current row) val,
                    COUNT(TE.val) OVER (partition by TE.sampling_point_id ORDER BY TE.from_time RANGE BETWEEN '23 hour' PRECEDING AND current row) cnt,
                    TE.sampling_point_id
                FROM
                    TIMEVALUES TE
            ) C,
            sampling_points SP, eea_times TM
            WHERE C.sampling_point_id = SP.id
            AND C.DATETIME >= %(fromTime)s
            AND SP.time_resolution_id = TM.id
        """
        return sql

    @staticmethod
    def Month():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s)  AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1 
                AND o.from_time >= %(fromTime)s
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
            )
            SELECT 
                to_char (DateTime, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN ROUND(cnt/(extract(days from (DateTime + interval '1 MONTH - 1 day'))/(1/(86400/TM.timestep::float)))*100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                    ELSE NULL 
                END "value",
                ROUND(cnt/(extract(days from (DateTime + interval '1 MONTH - 1 day'))/(1/(86400/TM.timestep::float)))*100) "coverage",
                CNT "cnt",
                SP.ID "sampling_point_id",
                7 "meantype"                      
            FROM
            (
                SELECT 
                    DATE_TRUNC('month',TE.from_time) DATETIME, 
                    AVG(TE.val) val,
                    COUNT(TE.val) cnt,
                    TE.sampling_point_id
                FROM
                    TIMEVALUES TE
                WHERE 1=1
                GROUP BY TE.sampling_point_id, DATE_TRUNC('month',TE.from_time)
                ORDER BY TE.sampling_point_id, DATE_TRUNC('month',TE.from_time)
            ) C,
            sampling_points SP,  eea_times TM
            WHERE C.sampling_point_id = SP.id
            AND SP.time_resolution_id = TM.id
        """
        return sql

    @staticmethod
    def WinterYear():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1  
                AND o.from_time >= %(fromTime)s
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
                AND to_char(o.from_time, 'MM') IN ( '01','02','03','10','11','12')
            )
            SELECT 
                to_char (DateTime, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN TM.timestep = 31536000 THEN
                        CASE WHEN cnt = 0 THEN NULL ELSE ROUND(val,%(fraction)s)::double PRECISION END
                    ELSE
                        CASE
                            WHEN ROUND(cnt / ((extract(days from ((DateTime + interval '3 MONTH') - DateTime))) / (1 / (86400 / TM.timestep::float)) + ((extract(days from ((DateTime + interval '12 MONTH') - DateTime)))  / (1 / (86400 / TM.timestep::float)) - (extract(days from ((DateTime + interval '9 MONTH') - DateTime))) / (1 / (86400 / TM.timestep::float)))) * 100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                            ELSE NULL 
                        END
                END "value",
                CASE TM.timestep WHEN 31536000 THEN 
                    CASE WHEN cnt = 0 THEN 0 ELSE 100 END 
                    ELSE ROUND(cnt / ((extract(days from ((DateTime + interval '3 MONTH') - DateTime))) / (1 / (86400 / TM.timestep::float)) + ((extract(days from ((DateTime + interval '12 MONTH') - DateTime)))  / (1 / (86400 / TM.timestep::float)) - (extract(days from ((DateTime + interval '9 MONTH') - DateTime))) / (1 / (86400 / TM.timestep::float)))) * 100) END "coverage",
                CNT "cnt",
                SP.ID "sampling_point_id",
                8 "meantype"  
            FROM
            (
                SELECT 
                    DATE_TRUNC('year',TE.from_time) DATETIME,
                    AVG(TE.val) val,
                    COUNT(TE.val) cnt,
                    TE.sampling_point_id
                FROM
                        TIMEVALUES TE
                WHERE 1=1
                GROUP BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
                ORDER BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
            ) C,
            sampling_points SP, eea_times TM
            WHERE C.sampling_point_id = SP.id
            AND SP.time_resolution_id = TM.id
        """
        return sql

    @staticmethod
    def Aot40Vegetation():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1 
                AND o.from_time >= %(fromTime)s
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
                AND to_char(o.from_time, 'MM') IN ('05', '06', '07')
		        AND to_char(o.from_time, 'HH24') IN ('08', '09', '10','11','12','13','14','15','16','17','18','19')
            ),
            timeseries as
            (
                select sp.id as "sampling_point_id", tm.timestep
                from sampling_points SP, eea_times TM
                WHERE SP.time_resolution_id = TM.id
            )
            SELECT
                to_char (HOURCOUNT.DATETIME, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                WHEN ROUND(HOURCOUNT / (1104/((3600/HOURCOUNT.timestep))) * 100) < %(coverage)s  THEN NULL
                ELSE  
                    CASE
                        WHEN HOURCOUNT < 100*(1104/((3600/HOURCOUNT.timestep)))/100 THEN ROUND(val*(1104/((3600/HOURCOUNT.timestep)))/HOURCOUNT,%(fraction)s)::double PRECISION
                        ELSE ROUND(val,%(fraction)s)::double PRECISION
                    END 
                END "value",
                CASE 
                WHEN ROUND(HOURCOUNT / (1104/((3600/HOURCOUNT.timestep))) * 100) >= %(coverage)s THEN ROUND(val*(2196/((3600/HOURCOUNT.timestep)))/HOURCOUNT,%(fraction)s)::double PRECISION
                ELSE NULL END "EstVal",
                ROUND(HOURCOUNT / (1104/((3600/HOURCOUNT.timestep))) * 100) "coverage",
                HOURCOUNT "cnt",
                HOURCOUNT.sampling_point_id "sampling_point_id",
                9 "meantype"
            FROM   
            timeseries TS,             
            (
                SELECT 
                    DATE_TRUNC('year',TE.from_time) DATETIME,
                    COUNT(TE.val) HOURCOUNT,
                    TE.sampling_point_id,    
                    MAX(TS.timestep) timestep    
                FROM
                    TIMEVALUES TE, timeseries TS
                WHERE 1=1               
                AND TE.sampling_point_id = TS.sampling_point_id     
                GROUP BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
            ) HOURCOUNT 
            LEFT OUTER JOIN
            (
                SELECT 
                    DATE_TRUNC('year',TE.from_time) DATETIME, 
                    SUM(TE.val - 80) val,            
                    COUNT(TE.val) EXCEEDANCES,
                    TE.sampling_point_id        
                FROM
                (
                    SELECT 
                        TE.from_time, TE.sampling_point_id,
                        CASE WHEN (TE.val - 80) > 0 THEN TE.val ELSE NULL END val
                    FROM TIMEVALUES TE                            
                ) TE
                WHERE 1=1                    
                GROUP BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
            ) C ON HOURCOUNT.DATETIME = C.DATETIME
            WHERE 1=1
            AND C.sampling_point_id = HOURCOUNT.sampling_point_id
            AND C.sampling_point_id = TS.sampling_point_id
            ORDER BY C.sampling_point_id, HOURCOUNT.DATETIME
        """
        return sql

    @staticmethod
    def Aot40ForestProtection():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s)  AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1  
                AND o.from_time >= %(fromTime)s
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
                AND to_char(o.from_time, 'MM') IN ('04', '05', '06', '07', '08', '09')
		        AND to_char(o.from_time, 'HH24') IN ('08', '09', '10','11','12','13','14','15','16','17','18','19')
            ),
            timeseries as
            (
                select sp.id as "sampling_point_id", tm.timestep
                from sampling_points SP,  eea_times TM
                WHERE SP.time_resolution_id = TM.id
            )
            SELECT
                to_char (HOURCOUNT.DATETIME, 'YYYY-MM-DD HH24:MI:SS') as "datetime", 
                CASE 
                WHEN ROUND(HOURCOUNT / (2196/((3600/HOURCOUNT.timestep))) * 100) < %(coverage)s  THEN NULL
                ELSE  
                    CASE
                        WHEN HOURCOUNT < 100*(2196/((3600/HOURCOUNT.timestep)))/100 THEN ROUND(val*(2196/((3600/HOURCOUNT.timestep)))/HOURCOUNT,%(fraction)s)::double PRECISION
                        ELSE ROUND(val,%(fraction)s)::double PRECISION
                    END 
                END "value",
                CASE 
                WHEN ROUND(HOURCOUNT / (2196/((3600/HOURCOUNT.timestep))) * 100) >= %(coverage)s THEN ROUND(val*(2196/((3600/HOURCOUNT.timestep)))/HOURCOUNT,%(fraction)s)::double PRECISION
                ELSE NULL END "EstVal",
                ROUND(HOURCOUNT / (2196/((3600/HOURCOUNT.timestep))) * 100) "coverage",
                HOURCOUNT "cnt",
                HOURCOUNT.sampling_point_id "sampling_point_id",
                10 "meantype"
            FROM   
            timeseries TS,             
            (
                SELECT 
                    DATE_TRUNC('year',TE.from_time) DATETIME,
                    COUNT(TE.val) HOURCOUNT,
                    TE.sampling_point_id,  
                    MAX(TS.timestep) timestep    
                FROM
                    TIMEVALUES TE, timeseries TS
                WHERE 1=1               
                AND TE.sampling_point_id = TS.sampling_point_id     
                GROUP BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
            ) HOURCOUNT 
            LEFT OUTER JOIN
            (
                SELECT 
                    DATE_TRUNC('year',TE.from_time) DATETIME, 
                    SUM(TE.val - 80) val,            
                    COUNT(TE.val) EXCEEDANCES,
                    TE.sampling_point_id        
                FROM
                (
                    SELECT 
                        TE.from_time, TE.sampling_point_id,
                        CASE WHEN (TE.val - 80) > 0 THEN TE.val ELSE NULL END val
                    FROM TIMEVALUES TE                            
                ) TE
                WHERE 1=1                    
                GROUP BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
            ) C ON HOURCOUNT.DATETIME = C.DATETIME
            WHERE 1=1
            AND C.sampling_point_id = HOURCOUNT.sampling_point_id
            AND C.sampling_point_id = TS.sampling_point_id
            ORDER BY C.sampling_point_id, HOURCOUNT.DATETIME
        """
        return sql

    @staticmethod
    def WinterSeason():
        sql = """
            WITH timevalues as
            (
                SELECT 
                    CASE EXTRACT(MONTH FROM o.from_time)					
                        WHEN 10 THEN (o.from_time + interval '12 MONTH')
                        WHEN 11 THEN (o.from_time + interval '12 MONTH')
                        WHEN 12 THEN (o.from_time + interval '12 MONTH')
                        ELSE o.from_time
                    END from_time,
                    o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s)  AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1   
                AND o.from_time >= (%(fromTime)s::timestamp - interval '12 MONTH')
                AND o.from_time < %(toTime)s::timestamp
                AND o.sampling_point_id IN %(ids)s
                AND to_char(o.from_time, 'MM') IN ('01','02','03','10','11','12') 
            ),
            timeseries as
            (
                select sp.id  "sampling_point_id", tm.timestep
                from sampling_points SP, eea_times TM
                WHERE SP.time_resolution_id = TM.id
            )
            SELECT
              to_char (DATETIME, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
              CASE 
                  WHEN TS.timestep = 31536000 THEN 
                      CASE WHEN cnt = 0 THEN NULL ELSE ROUND(val,%(fraction)s)::double PRECISION END 
                  ELSE 
                      CASE WHEN ROUND(cnt / ((extract(days from(DateTime + interval '3 month') - DateTime)) / (1 / (86400 / TS.timestep::float)) + ((extract(days from(DateTime + interval '12 month') - DateTime))  / (1 / (86400 / TS.timestep::float)) - (extract(days from(DateTime + interval '9 month') - DateTime)) / (1 / (86400 / TS.timestep::float)))) * 100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                      ELSE NULL END 
              END "value",                       
              CASE TS.timestep WHEN 31536000 THEN CASE WHEN cnt = 0 THEN 0 ELSE 100 END ELSE ROUND(cnt / ((extract(days from(DateTime + interval '3 month') - DateTime)) / (1 / (86400 / TS.timestep::float)) + ((extract(days from(DateTime + interval '12 month') - DateTime))  / (1 / (86400 / TS.timestep::float)) - (extract(days from(DateTime + interval '9 month') - DateTime)) / (1 / (86400 / TS.timestep::float)))) * 100) END "coverage",
              cnt "cnt",
              TS.sampling_point_id "sampling_point_id",
              11 "meantype"     
            FROM
            (
                SELECT 
                    DATE_TRUNC('year',A.from_time) DATETIME,
                    AVG(A.val) val,
                    COUNT(A.val) cnt,
                    A.sampling_point_id
                FROM TIMEVALUES A
                WHERE EXTRACT(YEAR FROM A.from_time) >= EXTRACT(YEAR FROM %(fromTime)s::timestamp)
                AND EXTRACT(YEAR FROM A.from_time) < EXTRACT(YEAR FROM %(toTime)s::timestamp)
                GROUP BY A.sampling_point_id, DATE_TRUNC('year',A.from_time)
                ORDER BY A.sampling_point_id, DATE_TRUNC('year',A.from_time)
            )  C,
            timeseries TS
            WHERE C.sampling_point_id = TS.sampling_point_id
            ORDER BY TS.sampling_point_id, datetime
        """
        return sql

    @staticmethod
    def SummerYear():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1 
                AND o.from_time >= %(fromTime)s
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
                AND to_char(o.from_time, 'MM') IN ('04','05','06','07','08','09')
            )
            SELECT 
                to_char (DateTime, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN TM.timestep = 31536000 THEN
                        CASE WHEN cnt = 0 THEN NULL ELSE ROUND(val,%(fraction)s)::double PRECISION END
                    ELSE
                        CASE
                            WHEN ROUND(cnt / ( (extract(days from ((DateTime + interval '12 MONTH') - DateTime)))  / (1 / (86400 / TM.timestep::float)) -(extract(days from ((DateTime + interval '3 MONTH') - DateTime))) / (1 / (86400 / TM.timestep::float))-((extract(days from ((DateTime + interval '12 MONTH') - DateTime)))  / (1 / (86400 / TM.timestep::float))-(extract(days from ((DateTime + interval '9 MONTH') - DateTime)))  / (1 / (86400 / TM.timestep::float)))) * 100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                            ELSE NULL 
                        END
                END "value",
                CASE TM.timestep WHEN 31536000 THEN 
                    CASE WHEN cnt = 0 THEN 0 ELSE 100 END 
                    ELSE ROUND(cnt / ( (extract(days from ((DateTime + interval '12 MONTH') - DateTime)))  / (1 / (86400 / TM.timestep::float)) -(extract(days from ((DateTime + interval '3 MONTH') - DateTime))) / (1 / (86400 / TM.timestep::float))-((extract(days from ((DateTime + interval '12 MONTH') - DateTime)))  / (1 / (86400 / TM.timestep::float))-(extract(days from ((DateTime + interval '9 MONTH') - DateTime)))  / (1 / (86400 / TM.timestep::float)))) * 100) END "coverage",
                CNT "cnt",
                SP.ID "sampling_point_id",
                12 "meantype"  
            FROM
            (
                SELECT 
                    DATE_TRUNC('year',TE.from_time) DATETIME,
                    AVG(TE.val) val,
                    COUNT(TE.val) cnt,
                    TE.sampling_point_id
                FROM
                        TIMEVALUES TE
                WHERE 1=1
                GROUP BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
                ORDER BY TE.sampling_point_id, DATE_TRUNC('year',TE.from_time)
            ) C,
            sampling_points SP, eea_times TM
            WHERE C.sampling_point_id = SP.id
            AND SP.time_resolution_id = TM.id
        """
        return sql

    @staticmethod
    def Period():
        sql = """
            WITH timevalues as 
            (
                SELECT 
                    o.from_time, o.to_time, o.sampling_point_id,
                    CASE 
                        WHEN o.observationverification_id <= %(verificationFlag)s AND (o.observationvalidity_id in (1,2,3,4) or %(useInvalidValues)s) AND (o.value != -9900) THEN  o.value
                        ELSE NULL 
                    END val
                FROM
                    observations o 
                WHERE 1=1 
                AND o.from_time >= %(fromTime)s
                AND o.from_time < %(toTime)s
                AND o.sampling_point_id IN %(ids)s
            ),
            timeseries as
            (
                select sp.id  "sampling_point_id", tm.timestep
                from sampling_points SP, eea_times TM
                WHERE SP.time_resolution_id = TM.id
            )
            SELECT
                to_char (DATETIME, 'YYYY-MM-DD HH24:MI:SS') as "datetime",
                CASE 
                    WHEN ROUND((cnt/cnt_total::float)*100) >= %(coverage)s THEN ROUND(val,%(fraction)s)::double PRECISION
                ELSE NULL END "value",
                ROUND((cnt/cnt_total::float)*100) "coverage", 
                TS.sampling_point_id "sampling_point_id",
                999 "meantype" 
            FROM
            (
                SELECT 
                    MAX(TE.from_time) DATETIME,
                    AVG(TE.val) val,
                    COUNT(TE.val) cnt,
                    COUNT(*) cnt_total,
                    TE.sampling_point_id
                FROM TIMEVALUES TE        
                GROUP BY TE.sampling_point_id                
            ) C,
            timeseries TS
            WHERE C.sampling_point_id = TS.sampling_point_id
        """
        return sql
