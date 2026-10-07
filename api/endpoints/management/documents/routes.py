"""
Routes for Documents management
CRUD operations for document metadata, plus PDF upload and its public download.

An uploaded PDF is kept in document_files and served without login at
/api/public/documents/<token>.pdf. That URL is written to documentattachment
(AQR3 DOC_05), which Reportnet 3.0 takes by URL.
"""
import hashlib
import io
import os
import secrets

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import BadRequest, NotFound
from .models import DocumentModel
from core.query import DeleteModel
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.database import CursorFromPool
from core.reporting.aqr3.attachments import AttachmentReferenceError, MAX_LENGTH, validate_reference

documents_endpoint = Blueprint("documents", __name__)

MAX_FILE_BYTES = 20 * 1024 * 1024
PUBLIC_PATH = "/api/public/documents/"


def _public_base_url():
    """Scheme and host the public URL is built on.

    PUBLIC_BASE_URL wins when set. Otherwise the request's own: behind Traefik
    that is http to the pod, so the forwarded scheme and host are preferred.
    """
    configured = os.environ.get("PUBLIC_BASE_URL")
    if configured:
        return configured.rstrip("/")
    scheme = request.headers.get("X-Forwarded-Proto", request.scheme).split(",")[0].strip()
    host = request.headers.get("X-Forwarded-Host", request.host).split(",")[0].strip()
    return f"{scheme}://{host}"


def _validated(doc):
    """DOC_05 must name a PDF, and one Reportnet3 will accept."""
    try:
        validate_reference('DOC_05', doc.documentattachment)
    except AttachmentReferenceError as e:
        raise BadRequest(str(e))
    return doc


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
                d.documentattachment,
                d.document_original_url,
                d.created_at,
                f.filename as file_name,
                f.file_size,
                f.uploaded_at as file_uploaded_at
            FROM documents d
            LEFT JOIN eea_datatable dt ON d.datatable_id = dt.id
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            LEFT JOIN LATERAL (
                SELECT filename, file_size, uploaded_at FROM document_files
                WHERE document_id = d.id
                ORDER BY uploaded_at DESC LIMIT 1
            ) f ON true
            ORDER BY d.created_at DESC
        """)

        documents = cursor.fetchall()
        return jsonify(documents)


@documents_endpoint.route("/api/management/documents/insert", methods=["POST"])
@jwt_required_with_management_claim()
def insert():
    """Insert a new document"""
    doc = _validated(DocumentModel(**request.json))

    with CursorFromPool() as cursor:
        cursor.execute("""
            INSERT INTO documents (
                id,
                datatable_id,
                documentobject_id,
                documentattachment,
                document_original_url
            ) VALUES (
                %(id)s,
                %(datatable_id)s,
                %(documentobject_id)s,
                %(documentattachment)s,
                %(document_original_url)s
            )
        """, doc.dict())

        if cursor.rowcount == 0:
            return {"error": "Failed to insert document"}, 400

        return {"message": "Document inserted successfully", "id": doc.id}, 201


@documents_endpoint.route("/api/management/documents/update", methods=["POST"])
@jwt_required_with_management_claim()
def update():
    """Update an existing document"""
    doc = _validated(DocumentModel(**request.json))

    if not doc.id:
        return {"error": "Document ID is required for update"}, 400

    with CursorFromPool() as cursor:
        cursor.execute("""
            UPDATE documents
            SET
                datatable_id = %(datatable_id)s,
                documentobject_id = %(documentobject_id)s,
                documentattachment = %(documentattachment)s,
                document_original_url = %(document_original_url)s
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


@documents_endpoint.route("/api/management/documents/<path:document_id>/file", methods=["POST"])
@jwt_required_with_management_claim()
def upload_file(document_id):
    """Store a PDF for a document and point its DOC_05 attachment at the file's public URL.

    Every upload gets a new token, so a URL that has been submitted keeps
    serving what it served then.
    """
    upload = request.files.get("file")
    if upload is None:
        raise BadRequest("File form does not contain the key 'file'")
    filename = os.path.basename((upload.filename or "").replace("\\", "/"))
    if not filename.lower().endswith(".pdf"):
        raise BadRequest("Only PDF files can be uploaded for a document")

    content = upload.read(MAX_FILE_BYTES + 1)
    if len(content) > MAX_FILE_BYTES:
        raise BadRequest(f"The file is larger than {MAX_FILE_BYTES // (1024 * 1024)} MB")
    if not content.startswith(b"%PDF-"):
        raise BadRequest(f"{filename} is not a PDF")

    token = secrets.token_hex(16)
    url = f"{_public_base_url()}{PUBLIC_PATH}{token}.pdf"
    if len(url) > MAX_LENGTH:
        raise BadRequest(
            f"The public URL would be {len(url)} characters; DOC_05 allows {MAX_LENGTH}. "
            f"Set PUBLIC_BASE_URL to a shorter address.")

    with CursorFromPool() as cursor:
        cursor.execute("SELECT 1 FROM documents WHERE id = %s", (document_id,))
        if cursor.fetchone() is None:
            raise NotFound(f"Document {document_id} not found")

        cursor.execute("""
            INSERT INTO document_files
                (token, document_id, filename, mime_type, file_size, sha256, content, uploaded_by)
            VALUES (%(token)s, %(document_id)s, %(filename)s, 'application/pdf',
                    %(size)s, %(sha256)s, %(content)s, %(user)s)
        """, {
            "token": token,
            "document_id": document_id,
            "filename": filename[:255],
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "content": content,
            "user": get_jwt_identity(),
        })
        cursor.execute(
            "UPDATE documents SET documentattachment = %s WHERE id = %s",
            (url, document_id))

    return {"message": "File uploaded", "id": document_id, "url": url,
            "file_name": filename, "file_size": len(content)}, 201


@documents_endpoint.route(PUBLIC_PATH + "<token>.pdf", methods=["GET"])
def public_file(token):
    """Serve an uploaded document without login: the permanent URL in DOC_05."""
    if len(token) != 32 or any(c not in "0123456789abcdef" for c in token):
        raise NotFound()
    with CursorFromPool() as cursor:
        cursor.execute(
            "SELECT filename, mime_type, content FROM document_files WHERE token = %s",
            (token,))
        row = cursor.fetchone()
    if row is None:
        raise NotFound()

    response = send_file(io.BytesIO(bytes(row["content"])), mimetype=row["mime_type"],
                         as_attachment=False, download_name=row["filename"])
    # A token's bytes never change, so the file may be cached for good.
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response
