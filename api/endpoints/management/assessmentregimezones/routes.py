from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim

assessmentregimezones_endpoint = Blueprint('assessmentregimezones', __name__)


@assessmentregimezones_endpoint.route('/api/management/assessmentregimezones/years', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def get_years():
    """Get available classification years (just return current and previous years)"""
    from datetime import datetime
    current_year = datetime.now().year
    years = [current_year, current_year - 1, current_year - 2]
    return jsonify(years)


@assessmentregimezones_endpoint.route('/api/management/assessmentregimezones', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def get_assessment_regime_zones():
    """
    Get zone × environmental objective combinations with saved threshold data.
    Shows simplified view for user to set thresholds.
    """
    data = request.json
    year = data.get('year')

    if not year:
        return jsonify({"error": "Year is required"}), 400

    with CursorFromPool() as cursor:
        # Get zone × objective combinations with saved data
        cursor.execute("""
            SELECT 
                -- Hidden ID for saving
                eo.id as environmental_objective_id,
                
                -- Display columns
                z.id as zone_id,
                z.name as zone_name,
                COALESCE(p.notation, p.label) as pollutant_name,
                COALESCE(pt.notation, pt.label) as protection_target,
                eo.objective_type,
                COALESCE(rm.notation, rm.label) as reporting_metric,
                
                -- Editable fields (from saved data or defaults)
                COALESCE(arz.classification_year, %s) as classification_year,
                arz.document_id as classification_report_id,
                arz.assessment_threshold_exceedance_id as assessment_threshold_exceedance,
                
                -- Valid dropdown options
                eo.assessment_threshold,
                
                -- Saved record ID (null if not saved yet)
                arz.id as saved_id
                
            FROM zones z
            CROSS JOIN eea_environmentalobjective eo
            LEFT JOIN eea_pollutants p ON p.id = eo.related_pollutant
            LEFT JOIN eea_protectiontargets pt ON eo.protection_target = pt.uri
            LEFT JOIN eea_reportingmetrics rm ON eo.reporting_metric = rm.uri
            LEFT JOIN assessmentregime_zones arz ON arz.zone_id = z.id 
                AND arz.environmental_objective_id = eo.id 
                AND arz.classification_year = %s
            WHERE (
                eo.assessment_threshold LIKE %s OR
                eo.assessment_threshold LIKE %s OR
                eo.assessment_threshold LIKE %s
            )
            ORDER BY z.code, p.notation, eo.objective_type
        """, (year, year, '%UAT%', '%LAT%', '%LTO%'))

        results = cursor.fetchall()

        # Parse assessment_threshold to extract valid exceedance options
        for row in results:
            if row['assessment_threshold']:
                threshold_uris = row['assessment_threshold'].split(',')
                valid_options = [uri.strip().split('/')[-1] for uri in threshold_uris]
                row['valid_exceedance_options'] = valid_options
            else:
                row['valid_exceedance_options'] = []

        return jsonify(results)


@assessmentregimezones_endpoint.route('/api/management/assessmentregimezones/update-rows', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def update_assessment_regime_zone_rows():
    """
    Update or delete specific assessment regime zone rows.
    Used for context menu updates.
    """
    data = request.json
    records = data.get('records', [])

    if not records:
        return jsonify({"error": "No records provided"}), 400

    with CursorFromPool() as cursor:
        updated_count = 0
        deleted_count = 0
        inserted_count = 0

        for record in records:
            zone_id = record.get('zone_id')
            env_obj_id = record.get('environmental_objective_id')
            year = record.get('classification_year')
            report_id = record.get('classification_report_id')
            threshold_exceedance = record.get('assessment_threshold_exceedance')

            if not all([zone_id, env_obj_id, year]):
                continue

            # Check if record exists
            cursor.execute("""
                SELECT id FROM assessmentregime_zones 
                WHERE zone_id = %s AND environmental_objective_id = %s AND classification_year = %s
            """, (zone_id, env_obj_id, year))
            existing = cursor.fetchone()

            if report_id and threshold_exceedance:
                # Both filled - upsert
                if existing:
                    cursor.execute("""
                        UPDATE assessmentregime_zones 
                        SET document_id = %s, assessment_threshold_exceedance_id = %s
                        WHERE zone_id = %s AND environmental_objective_id = %s AND classification_year = %s
                    """, (report_id, threshold_exceedance, zone_id, env_obj_id, year))
                    updated_count += 1
                else:
                    cursor.execute("""
                        INSERT INTO assessmentregime_zones 
                            (zone_id, environmental_objective_id, classification_year, 
                             document_id, assessment_threshold_exceedance_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (zone_id, env_obj_id, year, report_id, threshold_exceedance))
                    inserted_count += 1
            elif not report_id and not threshold_exceedance:
                # Both empty - delete if exists
                if existing:
                    cursor.execute("""
                        DELETE FROM assessmentregime_zones 
                        WHERE zone_id = %s AND environmental_objective_id = %s AND classification_year = %s
                    """, (zone_id, env_obj_id, year))
                    deleted_count += 1

        cursor.connection.commit()

        return jsonify({
            "message": f"Updated {updated_count}, inserted {inserted_count}, deleted {deleted_count} records"
        })


@assessmentregimezones_endpoint.route('/api/management/assessmentregimezones/exceedance-options', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def get_exceedance_options():
    """Get all available assessment threshold exceedance options for dropdown"""
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT 
                id as value,
                notation as text,
                label
            FROM eea_assessmentthresholdexceedances
            ORDER BY notation
        """)
        options = cursor.fetchall()
        return jsonify(options)


@assessmentregimezones_endpoint.route('/api/management/assessmentregimezones/document-options', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def get_document_options():
    """Get all available documents for classification report dropdown"""
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
                d.id as value,
                d.id || ' - ' || dobj.label as text
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            WHERE d.datatable_id = 'assessmentregimezone'
            ORDER BY d.id
        """)
        documents = cursor.fetchall()
        return jsonify(documents)
