"""What is still outstanding before this database can be submitted.

Serves the same catalogue the migration wizard writes into its run report, but
evaluated against the database as it is now -- so an item disappears the moment
the operator actually fixes it, instead of lingering as a snapshot of the day the
database was converted.

A migrated database is not finished when the rows land. Several AQR3 tables have
no v3 source at all and are filled here afterwards, and a v3 deployment can carry
identifiers and references that v4 refuses outright. This endpoint is how the
operator finds out which of those apply to them.
"""
from flask import Blueprint, jsonify

from core.database import CursorFromPool
from core.eea.upgrade_tasks import live_tasks
from core.jwt_ext_custom import (jwt_required_with_allnetworks_claim,
                                 jwt_required_with_management_claim)

upgrade_endpoint = Blueprint("upgrade", __name__)


@upgrade_endpoint.route("/api/management/upgrade/tasks", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def get_upgrade_tasks():
    """Everything still to do, most serious first.

    Read-only and side-effect free, so it is safe to poll and safe to open at any
    time -- including on a database that was never migrated, where it simply
    comes back empty.
    """
    with CursorFromPool() as cursor:
        tasks = live_tasks(cursor)
    return jsonify({
        'tasks': tasks,
        'blockers': sum(1 for t in tasks if t['severity'] == 'blocker'),
        'total': len(tasks),
    })
