"""Request Management blueprint."""
from datetime import date, datetime, timezone

from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import Asset, Department, ServiceRequest, User
from app.utils.audit import log_audit
from app.utils.decorators import admin_only, admin_or_operator, require_csrf
from app.utils.pagination import paginate

bp = Blueprint('requests', __name__, url_prefix='/api/requests')

REQUEST_TYPES = {
    'Asset Request', 'Repair Request', 'Replacement Request',
    'Relocation Request', 'Access Request', 'Network Request', 'Other',
}
PRIORITIES = {'Low', 'Medium', 'High', 'Critical'}
STATUSES = {
    'Open', 'In Progress', 'Waiting Approval', 'Approved',
    'Rejected', 'Fulfilled', 'Closed', 'Cancelled',
}

# ── helpers ─────────────────────────────────────────────────────────────────

def _next_number() -> str:
    year = datetime.now(timezone.utc).year
    last = ServiceRequest.query.order_by(ServiceRequest.id.desc()).first()
    n = (last.id + 1) if last else 1
    return f'REQ-{year}-{n:04d}'


def _validate(data, updating=False):
    if not updating:
        required = {'title', 'request_type', 'priority'}
        missing = required - set(data.keys())
        if missing:
            return {'error': f'Missing fields: {", ".join(missing)}'}, 400
    for field, allowed in [('request_type', REQUEST_TYPES), ('priority', PRIORITIES), ('status', STATUSES)]:
        if data.get(field) and data[field] not in allowed:
            return {'error': f'Invalid {field}. Allowed: {", ".join(sorted(allowed))}'}, 400
    for fk_field, model in [('asset_id', Asset), ('department_id', Department), ('assigned_to_id', User)]:
        val = data.get(fk_field)
        if val and not db.session.get(model, int(val)):
            return {'error': f'Invalid {fk_field}'}, 400
    return None, None


# ── list ───────────────────────────────────────────────────────────────────

@bp.route('', methods=['GET'])
@admin_or_operator
def list_requests():
    query = ServiceRequest.query
    for param, column in [
        ('status', ServiceRequest.status),
        ('priority', ServiceRequest.priority),
        ('request_type', ServiceRequest.request_type),
    ]:
        if request.args.get(param):
            query = query.filter(column == request.args.get(param))
    for param, column in [
        ('requester_id', ServiceRequest.requester_id),
        ('assigned_to_id', ServiceRequest.assigned_to_id),
        ('asset_id', ServiceRequest.asset_id),
    ]:
        val = request.args.get(param, type=int)
        if val:
            query = query.filter(column == val)
    search = (request.args.get('search') or '').strip()
    if search:
        pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                ServiceRequest.title.like(pattern),
                ServiceRequest.request_number.like(pattern),
                ServiceRequest.description.like(pattern),
            )
        )
    query = query.order_by(ServiceRequest.created_at.desc())
    return jsonify(paginate(query))


@bp.route('/<int:req_id>', methods=['GET'])
@admin_or_operator
def get_request(req_id):
    sr = db.session.get(ServiceRequest, req_id)
    if not sr:
        return jsonify({'error': 'Request not found'}), 404
    return jsonify({'data': sr.to_dict()})

# ── create ─────────────────────────────────────────────────────────────────

@bp.route('', methods=['POST'])
@admin_or_operator
@require_csrf
def create_request():
    data = request.get_json(silent=True) or {}
    err, code = _validate(data)
    if err:
        return jsonify(err), code

    sr = ServiceRequest(
        request_number=_next_number(),
        title=data['title'].strip(),
        description=(data.get('description') or '').strip() or None,
        request_type=data['request_type'],
        priority=data.get('priority', 'Medium'),
        status=data.get('status', 'Open'),
        requester_id=data.get('requester_id') or g.current_user_id,
        assigned_to_id=data.get('assigned_to_id') if data.get('assigned_to_id') else None,
        asset_id=data.get('asset_id') if data.get('asset_id') else None,
        department_id=data.get('department_id') if data.get('department_id') else None,
        due_date=date.fromisoformat(data['due_date']) if data.get('due_date') else None,
        resolution_notes=(data.get('resolution_notes') or '').strip() or None,
    )
    db.session.add(sr)
    db.session.commit()
    log_audit('CREATE_REQUEST', 'request', resource_id=sr.id, status='success',
              metadata={'number': sr.request_number, 'type': sr.request_type})
    return jsonify({'data': sr.to_dict()}), 201

# ── update ─────────────────────────────────────────────────────────────────

@bp.route('/<int:req_id>', methods=['PUT'])
@admin_or_operator
@require_csrf
def update_request(req_id):
    sr = db.session.get(ServiceRequest, req_id)
    if not sr:
        return jsonify({'error': 'Request not found'}), 404
    data = request.get_json(silent=True) or {}
    err, code = _validate(data, updating=True)
    if err:
        return jsonify(err), code

    changed = []
    for field in ['title', 'description', 'request_type', 'priority', 'resolution_notes']:
        if field in data:
            setattr(sr, field, data[field].strip() if isinstance(data[field], str) else data[field])
            changed.append(field)
    for fk in ['asset_id', 'department_id', 'assigned_to_id']:
        if fk in data:
            val = data[fk]
            old = getattr(sr, fk)
            setattr(sr, fk, int(val) if val else None)
            if old != getattr(sr, fk):
                changed.append(fk)
    for date_field in ['due_date']:
        if date_field in data:
            v = data[date_field]
            setattr(sr, date_field, date.fromisoformat(v) if v else None)
            changed.append(date_field)
    if 'status' in data:
        old_status = sr.status
        sr.status = data['status']
        changed.append('status')
        if sr.status == 'Closed' and old_status != 'Closed':
            sr.closed_at = datetime.now(timezone.utc)
        elif sr.status != 'Closed' and old_status == 'Closed':
            sr.closed_at = None

    db.session.commit()
    log_audit('UPDATE_REQUEST', 'request', resource_id=sr.id, status='success',
              metadata={'number': sr.request_number, 'changed': changed})
    return jsonify({'data': sr.to_dict()})

# ── delete (admin only) ────────────────────────────────────────────────────

@bp.route('/<int:req_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_request(req_id):
    sr = db.session.get(ServiceRequest, req_id)
    if not sr:
        return jsonify({'error': 'Request not found'}), 404
    db.session.delete(sr)
    db.session.commit()
    log_audit('DELETE_REQUEST', 'request', resource_id=req_id, status='success',
              metadata={'number': sr.request_number})
    return jsonify({'message': 'Request deleted'})
