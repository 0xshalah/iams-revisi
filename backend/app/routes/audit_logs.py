"""Audit logs blueprint (Administrator read-only)."""
from flask import Blueprint, request

from app.models import AuditLog
from app.utils.decorators import admin_only
from app.utils.pagination import paginate

bp = Blueprint('audit_logs', __name__, url_prefix='/api/audit-logs')


@bp.route('', methods=['GET'])
@admin_only
def list_audit_logs():
    query = AuditLog.query
    if request.args.get('action'):
        query = query.filter_by(action=request.args.get('action'))
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    rows = query.order_by(AuditLog.created_at.desc())
    return paginate(rows, max_per_page=100)
