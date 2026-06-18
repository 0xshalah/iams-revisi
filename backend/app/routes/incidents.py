"""Incidents blueprint."""
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Incident
from app.utils.decorators import admin_or_operator, audit_action, require_csrf, require_role
from app.utils.pagination import paginate

bp = Blueprint('incidents', __name__, url_prefix='/api/incidents')

SEVERITIES = {'Critical', 'High', 'Medium', 'Low'}
STATUSES = {'Open', 'In Progress', 'Resolved', 'Closed'}


def _validate(data, updating=False):
    required = {'title', 'severity'}
    if not updating:
        missing = required - set(data.keys())
        if missing:
            return {'error': f'Missing fields: {", ".join(missing)}'}, 400
    if data.get('severity') and data['severity'] not in SEVERITIES:
        return {'error': f'Invalid severity. Allowed: {", ".join(SEVERITIES)}'}, 400
    if data.get('status') and data['status'] not in STATUSES:
        return {'error': f'Invalid status. Allowed: {", ".join(STATUSES)}'}, 400
    return None, None


def _next_code() -> str:
    year = datetime.now(timezone.utc).year
    last = Incident.query.filter(Incident.code.like(f'INC-{year}-%')).order_by(Incident.code.desc()).first()
    n = 1
    if last:
        try:
            n = int(last.code.split('-')[-1]) + 1
        except Exception:
            pass
    return f'INC-{year}-{n:04d}'


@bp.route('', methods=['GET'])
@admin_or_operator
def list_incidents():
    query = Incident.query
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    if request.args.get('severity'):
        query = query.filter_by(severity=request.args.get('severity'))
    rows = query.order_by(Incident.created_at.desc())
    return jsonify(paginate(rows))


@bp.route('', methods=['POST'])
@admin_or_operator
@require_csrf
@audit_action('CREATE', 'incident')
def create_incident():
    data = request.get_json(silent=True) or {}
    err, code = _validate(data)
    if err:
        return jsonify(err), code
    incident = Incident(
        code=_next_code(),
        title=data['title'].strip(),
        description=(data.get('description') or '').strip() or None,
        asset_id=data.get('asset_id'),
        severity=data['severity'],
        status=data.get('status', 'Open'),
        assignee_id=data.get('assignee_id'),
    )
    db.session.add(incident)
    db.session.commit()
    return jsonify({'data': incident.to_dict()}), 201


@bp.route('/<int:incident_id>', methods=['GET'])
@admin_or_operator
def get_incident(incident_id):
    incident = db.session.get(Incident, incident_id)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    return jsonify({'data': incident.to_dict()})


@bp.route('/<int:incident_id>', methods=['PUT'])
@admin_or_operator
@require_csrf
@audit_action('UPDATE', 'incident', resource_id_key='incident_id')
def update_incident(incident_id):
    incident = db.session.get(Incident, incident_id)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    data = request.get_json(silent=True) or {}
    err, code = _validate(data, updating=True)
    if err:
        return jsonify(err), code
    if 'title' in data:
        incident.title = data['title'].strip()
    if 'description' in data:
        incident.description = (data['description'] or '').strip() or None
    if 'asset_id' in data:
        incident.asset_id = data['asset_id']
    if 'severity' in data:
        incident.severity = data['severity']
    if 'status' in data:
        incident.status = data['status']
    if 'assignee_id' in data:
        incident.assignee_id = data['assignee_id']
    incident.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'data': incident.to_dict()})


@bp.route('/<int:incident_id>', methods=['DELETE'])
@require_role('Administrator')
@require_csrf
@audit_action('DELETE', 'incident', resource_id_key='incident_id')
def delete_incident(incident_id):
    incident = db.session.get(Incident, incident_id)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    db.session.delete(incident)
    db.session.commit()
    return jsonify({'message': 'Incident deleted'})
