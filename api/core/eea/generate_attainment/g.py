from core.database import CursorFromPool
from core.data.mean import Mean, MeanType
from core.eea.generate_attainment.directives.lv import get_lv
from core.eea.generate_attainment.directives.tv import get_tv
from core.eea.generate_attainment.directives.cl import get_cl
from core.eea.generate_attainment.directives.int import get_int
from core.eea.generate_attainment.directives.alt import get_alt
from core.eea.generate_attainment.directives.eco import get_eco
from core.eea.generate_attainment.directives.ert import get_ert
from core.eea.generate_attainment.directives.lto import get_lto
from core.eea.generate_attainment.directives.limitvalues import limitvalues
import time

start = time.time()


def unique_spos(assessmentregimes):
    spos = []  # list of unique sampling points
    for regime in assessmentregimes:
        if regime["samplingpoints"] is not None:
            for spo in regime["samplingpoints"]:
                if spo not in spos:
                    spos.append(spo)
    return spos


def get_assessmentregimes(year):
    with CursorFromPool() as cursor:
        sql = """
          WITH spos as (
              select assessmentregime_id, array_agg(assessmentlocal_id) as samplingpoints
              from assessmentdata
              group by assessmentregime_id
          )
          SELECT ar.*, a.samplingpoints
          FROM assessmentregimes ar left join spos a on ar.id = a.assessmentregime_id
          WHERE ar.thresholdclassificationyear = %(year)s
        """
        cursor.execute(sql, {"year": year})
        assessmentregimes = cursor.fetchall()
        return assessmentregimes


def insert_attainments(attainments, deleteExistingAttainments):
    with CursorFromPool() as cursor:
        if deleteExistingAttainments:
            cursor.execute("DELETE FROM attainments")

        for attainment in attainments:
            cursor.execute(
                """
                INSERT INTO attainments 
                (id, name, assessmentregime_id, comment) 
                VALUES 
                (%(id)s, %(name)s, %(assessmentregime_id)s, %(comment)s)
                """,
                attainment)

            cursor.execute(
                """
                INSERT INTO exceedancedescriptions 
                (id, attainment_id, exceedancedescription_element, max_value, exceedances, excedance_type, adjustment_type, area_classification, exceedance_reason, population_reference_year, exposed_population, surface_area) 
                VALUES 
                (%(id)s, %(attainment_id)s, %(exceedancedescription_element)s, %(max_value)s, %(exceedances)s, %(exceedance_type)s, %(adjustment_type)s, %(area_classification)s, %(exceedance_reason)s, %(population_reference_year)s, %(exposed_population)s, %(surface_area)s)
                """,
                attainment["exceedance"])


def generate(year, deleteExistingAttainments):

    assessmentregimes = get_assessmentregimes(year)

    spos = unique_spos(assessmentregimes)
    exceedances = []
    attainments = []

    for regime in assessmentregimes:
        directives = list(filter(lambda x: x["pollutant_uri"] == regime["pollutant"] and x["reportingmetric"] == regime["reportingmetric"] and x["objectivetype"] == regime["objecttype"], limitvalues))
        if len(directives) == 0:
            continue

        directive = directives[0]

        # Return empty if no sampling points
        if regime["samplingpoints"] is None:
            exceedances.append({"regime": regime, "value": 0, "exceedance_type":  1 if directive["count"] != None else 2, "has_exceedances": False})
            continue

        # LV
        if directive["objectivetype"] == "LV":  # and regime["samplingpoints"] is not None:
            lv = get_lv(directive, regime, year)
            if lv != None:
                exceedances.append(lv)

        # TV
        if directive["objectivetype"] == "TV":  # and regime["samplingpoints"] is not None:
            tv = get_tv(directive, regime, year)
            if tv != None:
                exceedances.append(tv)

        # CL
        if directive["objectivetype"] == "CL":  # and regime["samplingpoints"] is not None:
            cl = get_cl(directive, regime, year)
            if cl != None:
                exceedances.append(cl)

        # INT
        if directive["objectivetype"] == "INT":  # and regime["samplingpoints"] is not None:
            int = get_int(directive, regime, year)
            if int != None:
                exceedances.append(int)

        # ALT
        if directive["objectivetype"] == "ALT":  # and regime["samplingpoints"] is not None:
            alt = get_alt(directive, regime, year)
            if alt != None:
                exceedances.append(alt)

        # ECO
        if directive["objectivetype"] == "ECO":  # and regime["samplingpoints"] is not None:
            eco = get_eco(directive, regime, year)
            if eco != None:
                exceedances.append(eco)

        # ERT
        if directive["objectivetype"] == "ERT":  # and regime["samplingpoints"] is not None:
            ert = get_ert(directive, regime, year)
            if ert != None:
                exceedances.append(ert)

        # LTO
        if directive["objectivetype"] == "LTO":  # and regime["samplingpoints"] is not None:
            lto = get_lto(directive, regime, year)
            if lto != None:
                exceedances.append(lto)

    for exceedance in exceedances:
        att_id = exceedance["regime"]["id"].replace("ARE", "ATT")
        exc_id = exceedance["regime"]["id"].replace("ATT", "EXC")
        attainment_exceedance = {
            "id": exc_id,
            "attainment_id": att_id,
            "exceedancedescription_element": 3,
            "exceedance_type": exceedance["exceedance_type"],
            "max_value": exceedance["value"],
            "exceedances": exceedance["has_exceedances"],
            "adjustment_type": "noneApplicable" if exceedance["has_exceedances"] else None,
            "area_classification": "http://dd.eionet.europa.eu/vocabulary/aq/areaclassification/rural" if exceedance["has_exceedances"] else None,
            "exceedance_reason": "S1" if exceedance["has_exceedances"] else None,
            "population_reference_year": year if exceedance["has_exceedances"] else None,
            "exposed_population": 0 if exceedance["has_exceedances"] else None,
            "surface_area": 0 if exceedance["has_exceedances"] else None,
        }

        attainment = {"id": att_id, "name": att_id, "assessmentregime_id": exceedance["regime"]["id"], "comment": None, "exceedance": attainment_exceedance}
        attainments.append(attainment)

    insert_attainments(attainments, deleteExistingAttainments)

    # print("Attainments:\t", len(exceedances))
    end = time.time()
    # print("Done in " + str(end - start) + " seconds")

# print("Attainments:\t\t\t", len(exceedances))
# None = 0, LimitValue = 1, MarginOfTolerance = 2, UpperAssessmentThreshold = 3, LowerAssessment Threshold = 4, TargetValue = 5, LongTermObjective = 6, ATF = 7, ITF = 8, CL=9, NorLimitValue = 98, AirqualityCriteria=99, ECO = 10, ERT = 11, INT = 12
# None = 0, Hour = 1, Day = 2, MovingEightHour = 3, Year = 4, MovingDay = 5, MovingEightHourMax = 6, Month = 7, WinterYear = 8,  Aot40Vegetation = 9, Aot40ForestProtection = 10, WinterSeason = 11
