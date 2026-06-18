"""Problems blueprint."""
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Problem
from app.utils.decorators import admin_or_operator, audit_action, require_csrf, require_role
from app.utils.pagination import paginate

bp = Blueprint('problems', __name__, url_prefix='/api/problems')

PRIORITIES = {'Critical', 'High', 'Medium', 'Low'}
STATUSES = {'Open', 'Investigating', 'Known Error', 'Closed'}


def _validate(data, updating=False):
    required = {'title', 'priority'}
    if not updating:
        missing = required - set(data.keys())
        if missing:
            return {'error': f'Missing fields: {", ".join(missing)}'}, 400
    if data.get('priority') and data['priority'] not in PRIORITIES:
        return {'error': f'Invalid priority. Allowed: {", ".join(PRIORITIES)}'}, 400
    if data.get('status') and data['status'] not in STATUSES:
        return {'error': f'Invalid status. Allowed: {", ".join(STATUSES)}'}, 400
    return None, None


def _next_code() -> str:
    year = datetime.now(timezone.utc).year
    last = Problem.query.filter(Problem.code.like(f'PRB-{year}-%')).order_by(Problem.code.desc()).first()
    n = 1
    if last:
        try:
            n = int(last.code.split('-')[-1]) + 1
        except Exception:
            pass
    return f'PRB-{year}-{n:04d}'


@bp.route('', methods=['GET'])
@admin_or_operator
def list_problems():
    query = Problem.query
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    if request.args.get('priority'):
        query = query.filter_by(priority=request.args.get('priority'))
    rows = query.order_by(Problem.created_at.desc())
    return jsonify(paginate(rows))


@bp.route('', methods=['POST'])
@admin_or_operator
@require_csrf
@audit_action('CREATE', 'problem')
def create_problem():
    data = request.get_json(silent=True) or {}
    err, code = _validate(data)
    if err:
        return jsonify(err), code
    problem = Problem(
        code=_next_code(),
        title=data['title'].strip(),
        root_cause_summary=(data.get('root_cause_summary') or '').strip() or None,
        priority=data['priority'],
        status=data.get('status', 'Open'),
        owner_id=data.get('owner_id'),
    )
    db.session.add(problem)
    db.session.commit()
    return jsonify({'data': problem.to_dict()}), 201


@bp.route('/<int:problem_id>', methods=['GET'])
@admin_or_operator
def get_problem(problem_id):
    problem = db.session.get(Problem, problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404
    return jsonify({'data': problem.to_dict()})


@bp.route('/<int:problem_id>', methods=['PUT'])
@admin_or_operator
@require_csrf
@audit_action('UPDATE', 'problem', resource_id_key='problem_id')
def update_problem(problem_id):
    problem = db.session.get(Problem, problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404
    data = request.get_json(silent=True) or {}
    err, code = _validate(data, updating=True)
    if err:
        return jsonify(err), code
    if 'title' in data:
        problem.title = data['title'].strip()
    if 'root_cause_summary' in data:
        problem.root_cause_summary = (data['root_cause_summary'] or '').strip() or None
    if 'priority' in data:
        problem.priority = data['priority']
    if 'status' in data:
        problem.status = data['status']
    if 'owner_id' in data:
        problem.owner_id = data['owner_id']
    problem.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'data': problem.to_dict()})


@bp.route('/<int:problem_id>', methods=['DELETE'])
@require_role('Administrator')
@require_csrf
@audit_action('DELETE', 'problem', resource_id_key='problem_id')
def delete_problem(problem_id):
    problem = db.session.get(Problem, problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404
    db.session.delete(problem)
    db.session.commit()
    return jsonify({'message': 'Problem deleted'})
