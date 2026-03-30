"""
Routes for Documents management
CRUD operations for document metadata
"""
from flask import Blueprint, request, jsonify
from .models import DocumentModel
from core.query import DeleteModel
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.database import CursorFromPool

documents_endpoint = Blueprint("documents", __name__)


@documents_endpoint.route("/api/management/documents/lookups", methods=["GET"])
@jwt_required_with_management_claim()
def get_lookups():
    """Get lookup data for documents form dropdowns"""
    with CursorFromPool() as cursor:
        # Get datatables
        cursor.execute("""
            SELECT id as value, label
            FROM eea_datatable
            ORDER BY LOWER(label)
        """)
        datatables = cursor.fetchall()

        # Get document objects
        cursor.execute("""
            SELECT id as value, label
            FROM eea_documentobject
            ORDER BY LOWER(label)
        """)
        documentobjects = cursor.fetchall()

        return {
            "datatables": datatables,
            "documentobjects": documentobjects
        }, 200


@documents_endpoint.route("/api/management/documents", methods=["GET"])
@jwt_required_with_management_claim()
def get_all():
    """Get all documents with vocabulary lookups"""
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT 
                d.id,
                COALESCE(NULLIF(dt.notation, ''), dt.label) as datatable_label,
                d.datatable_id,
                COALESCE(NULLIF(dobj.notation, ''), dobj.label) as documentobject_label,
                d.documentobject_id,
                d.created_at
            FROM documents d
            LEFT JOIN eea_datatable dt ON d.datatable_id = dt.id
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            ORDER BY d.created_at DESC
        """)

        documents = cursor.fetchall()
        return jsonify(documents)


@documents_endpoint.route("/api/management/documents/insert", methods=["POST"])
@jwt_required_with_management_claim()
def insert():
    """Insert a new document"""
    doc = DocumentModel(**request.json)

    with CursorFromPool() as cursor:
        cursor.execute("""
            INSERT INTO documents (
                id,
                datatable_id,
                documentobject_id
            ) VALUES (
                %(id)s,
                %(datatable_id)s,
                %(documentobject_id)s
            )
        """, doc.dict())

        if cursor.rowcount == 0:
            return {"error": "Failed to insert document"}, 400

        return {"message": "Document inserted successfully", "id": doc.id}, 201


@documents_endpoint.route("/api/management/documents/update", methods=["POST"])
@jwt_required_with_management_claim()
def update():
    """Update an existing document"""
    doc = DocumentModel(**request.json)

    if not doc.id:
        return {"error": "Document ID is required for update"}, 400

    with CursorFromPool() as cursor:
        cursor.execute("""
            UPDATE documents
            SET 
                datatable_id = %(datatable_id)s,
                documentobject_id = %(documentobject_id)s
            WHERE id = %(id)s
        """, doc.dict())

        if cursor.rowcount == 0:
            return {"error": "Document not found or no changes made"}, 404

        return {"message": "Document updated successfully"}, 200


@documents_endpoint.route("/api/management/documents/delete", methods=["POST"])
@jwt_required_with_management_claim()
def delete():
    """Delete documents by IDs"""
    delete_model = DeleteModel(**request.json)

    with CursorFromPool() as cursor:
        # For string IDs, we need to quote them
        ids_tuple = tuple(delete_model.ids)
        placeholders = ','.join(['%s'] * len(ids_tuple))
        cursor.execute(
            f"DELETE FROM documents WHERE id IN ({placeholders})",
            ids_tuple
        )

        if cursor.rowcount == 0:
            return {"error": "No documents found to delete"}, 404

        return {"message": f"Deleted {cursor.rowcount} document(s)"}, 200
