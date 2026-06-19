"""Change Management blueprint."""
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import Asset, ChangeRequest, Incident, Problem, ServiceRequest, User
from app.utils.audit import log_audit
from app.utils.decorators import admin_only, admin_or_operator, require_csrf
from app.utils.pagination import paginate

bp = Blueprint('changes', __name__, url_prefix='/api/changes')

CHANGE_TYPES = {'Standard', 'Normal', 'Emergency', 'Maintenance', 'Configuration', 'Replacement', 'Relocation', 'Other'}
RISK_LEVELS = {'Low', 'Medium', 'High', 'Critical'}
IMPACTS = {'Low', 'Medium', 'High', 'Critical'}
STATUSES = {'Draft', 'Submitted', 'Under Review', 'Approved', 'Rejected', 'Scheduled', 'Implementing', 'Completed', 'Failed', 'Cancelled', 'Closed'}
FINAL_STATUSES = {'Completed', 'Failed', 'Cancelled', 'Closed'}


def _next_number() -> str:
    year = datetime.now(timezone.utc).year
    last = ChangeRequest.query.order_by(ChangeRequest.id.desc()).first()
    n = (last.id + 1) if last else 1
    return f'CHG-{year}-{n:04d}'


def _validate(data, updating=False):
    if not updating:
        required = {'title', 'change_type', 'risk_level', 'impact'}
        missing = required - set(data.keys())
        if missing:
            return {'error': f'Missing fields: {", ".join(missing)}'}, 400
    for field, allowed in [('change_type', CHANGE_TYPES), ('risk_level', RISK_LEVELS), ('impact', IMPACTS), ('status', STATUSES)]:
        if data.get(field) and data[field] not in allowed:
            return {'error': f'Invalid {field}. Allowed: {", ".join(sorted(allowed))}'}, 400
    for fk_field, model in [
        ('asset_id', Asset), ('incident_id', Incident), ('problem_id', Problem),
        ('request_id', ServiceRequest), ('assignee_id', User), ('approver_id', User),
    ]:
        val = data.get(fk_field)
        if val and not db.session.get(model, int(val)):
            return {'error': f'Invalid {fk_field}'}, 400
    return None, None

# ── list / get ──────────────────────────────────────────────────────────────

@bp.route('', methods=['GET'])
@admin_or_operator
def list_changes():
    query = ChangeRequest.query
    for param, col in [
        ('status', ChangeRequest.status), ('change_type', ChangeRequest.change_type),
        ('risk_level', ChangeRequest.risk_level), ('impact', ChangeRequest.impact),
    ]:
        if request.args.get(param):
            query = query.filter(col == request.args.get(param))
    for param, col in [
        ('requester_id', ChangeRequest.requester_id), ('assignee_id', ChangeRequest.assignee_id),
        ('approver_id', ChangeRequest.approver_id), ('asset_id', ChangeRequest.asset_id),
        ('incident_id', ChangeRequest.incident_id), ('problem_id', ChangeRequest.problem_id),
        ('request_id', ChangeRequest.request_id),
    ]:
        val = request.args.get(param, type=int)
        if val:
            query = query.filter(col == val)
    search = (request.args.get('search') or '').strip()
    if search:
        pattern = f'%{search}%'
        query = query.filter(db.or_(ChangeRequest.title.like(pattern), ChangeRequest.change_number.like(pattern), ChangeRequest.description.like(pattern)))
    query = query.order_by(ChangeRequest.created_at.desc())
    return jsonify(paginate(query))

@bp.route('/<int:chg_id>', methods=['GET'])
@admin_or_operator
def get_change(chg_id):
    c = db.session.get(ChangeRequest, chg_id)
    if not c:
        return jsonify({'error': 'Change not found'}), 404
    return jsonify({'data': c.to_dict()})

# ── create ──────────────────────────────────────────────────────────────────

@bp.route('', methods=['POST'])
@admin_or_operator
@require_csrf
def create_change():
    data = request.get_json(silent=True) or {}
    err, code = _validate(data)
    if err:
        return jsonify(err), code
    c = ChangeRequest(
        change_number=_next_number(),
        title=data['title'].strip(),
        description=(data.get('description') or '').strip() or None,
        change_type=data['change_type'],
        risk_level=data.get('risk_level', 'Low'),
        impact=data.get('impact', 'Low'),
        status=data.get('status', 'Submitted'),
        requester_id=data.get('requester_id') or g.current_user_id,
        assignee_id=int(data['assignee_id']) if data.get('assignee_id') else None,
        approver_id=int(data['approver_id']) if data.get('approver_id') else None,
        asset_id=int(data['asset_id']) if data.get('asset_id') else None,
        incident_id=int(data['incident_id']) if data.get('incident_id') else None,
        problem_id=int(data['problem_id']) if data.get('problem_id') else None,
        request_id=int(data['request_id']) if data.get('request_id') else None,
        planned_start=datetime.fromisoformat(data['planned_start']) if data.get('planned_start') else None,
        planned_end=datetime.fromisoformat(data['planned_end']) if data.get('planned_end') else None,
        implementation_notes=(data.get('implementation_notes') or '').strip() or None,
        rollback_plan=(data.get('rollback_plan') or '').strip() or None,
        approval_notes=(data.get('approval_notes') or '').strip() or None,
    )
    db.session.add(c)
    db.session.commit()
    log_audit('CREATE_CHANGE', 'change', resource_id=c.id, status='success',
              metadata={'number': c.change_number, 'type': c.change_type})
    return jsonify({'data': c.to_dict()}), 201

# ── update ──────────────────────────────────────────────────────────────────

@bp.route('/<int:chg_id>', methods=['PUT'])
@admin_or_operator
@require_csrf
def update_change(chg_id):
    c = db.session.get(ChangeRequest, chg_id)
    if not c:
        return jsonify({'error': 'Change not found'}), 404
    data = request.get_json(silent=True) or {}
    err, code = _validate(data, updating=True)
    if err:
        return jsonify(err), code

    changed = []
    for field in ['title', 'description', 'change_type', 'risk_level', 'impact', 'implementation_notes', 'rollback_plan', 'approval_notes']:
        if field in data:
            old = getattr(c, field)
            setattr(c, field, data[field].strip() if isinstance(data[field], str) else data[field])
            if old != getattr(c, field):
                changed.append(field)
    for fk in ['asset_id', 'incident_id', 'problem_id', 'request_id', 'assignee_id', 'approver_id']:
        if fk in data:
            val = data[fk]
            old = getattr(c, fk)
            setattr(c, fk, int(val) if val else None)
            if old != getattr(c, fk):
                changed.append(fk)
    for dt in ['planned_start', 'planned_end']:
        if dt in data:
            v = data[dt]
            setattr(c, dt, datetime.fromisoformat(v) if v else None)
            changed.append(dt)
    if 'status' in data:
        old_status = c.status
        c.status = data['status']
        changed.append('status')
        if c.status in FINAL_STATUSES and old_status not in FINAL_STATUSES:
            c.closed_at = datetime.now(timezone.utc)
        elif c.status not in FINAL_STATUSES and old_status in FINAL_STATUSES:
            c.closed_at = None

    db.session.commit()
    log_audit('UPDATE_CHANGE', 'change', resource_id=c.id, status='success',
              metadata={'number': c.change_number, 'changed': changed})
    return jsonify({'data': c.to_dict()})

# ── approve / reject (admin only) ────────────────────────────────────────────

@bp.route('/<int:chg_id>/approve', methods=['POST'])
@admin_only
@require_csrf
def approve_change(chg_id):
    c = db.session.get(ChangeRequest, chg_id)
    if not c:
        return jsonify({'error': 'Change not found'}), 404
    data = request.get_json(silent=True) or {}
    c.status = 'Approved'
    c.approver_id = g.current_user_id
    if data.get('approval_notes'):
        c.approval_notes = data['approval_notes'].strip()
    db.session.commit()
    log_audit('APPROVE_CHANGE', 'change', resource_id=c.id, status='success',
              metadata={'number': c.change_number, 'approver': g.current_user_id})
    return jsonify({'data': c.to_dict()})

@bp.route('/<int:chg_id>/reject', methods=['POST'])
@admin_only
@require_csrf
def reject_change(chg_id):
    c = db.session.get(ChangeRequest, chg_id)
    if not c:
        return jsonify({'error': 'Change not found'}), 404
    data = request.get_json(silent=True) or {}
    c.status = 'Rejected'
    c.approver_id = g.current_user_id
    if data.get('approval_notes'):
        c.approval_notes = data['approval_notes'].strip()
    db.session.commit()
    log_audit('REJECT_CHANGE', 'change', resource_id=c.id, status='success',
              metadata={'number': c.change_number, 'approver': g.current_user_id})
    return jsonify({'data': c.to_dict()})

# ── delete (admin only) ────────────────────────────────────────────────────

@bp.route('/<int:chg_id>', methods=['DELETE'])
@admin_only
@require_csrf
def delete_change(chg_id):
    c = db.session.get(ChangeRequest, chg_id)
    if not c:
        return jsonify({'error': 'Change not found'}), 404
    db.session.delete(c)
    db.session.commit()
    log_audit('DELETE_CHANGE', 'change', resource_id=chg_id, status='success', metadata={'number': c.change_number})
    return jsonify({'message': 'Change deleted'})
