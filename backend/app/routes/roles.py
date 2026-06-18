"""Roles management blueprint (Administrator only)."""
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Role, User
from app.utils.decorators import admin_only, audit_action, require_csrf

bp = Blueprint('roles', __name__, url_prefix='/api/roles')

PROTECTED_ROLES = ('Administrator', 'Operator')


@bp.route('', methods=['GET'])
@admin_only
def list_roles():
    roles = Role.query.all()
    return jsonify({'data': [r.to_dict() for r in roles]})


@bp.route('', methods=['POST'])
@admin_only
@require_csrf
@audit_action('CREATE', 'role')
def create_role():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Role name is required'}), 400
    if Role.query.filter_by(name=name).first():
        return jsonify({'error': 'Role already exists'}), 409
    role = Role(name=name)
    db.session.add(role)
    db.session.commit()
    return jsonify({'data': role.to_dict()}), 201


@bp.route('/<int:role_id>', methods=['GET'])
@admin_only
def get_role(role_id):
    role = db.session.get(Role, role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    return jsonify({'data': role.to_dict()})


@bp.route('/<int:role_id>', methods=['PUT'])
@admin_only
@require_csrf
@audit_action('UPDATE', 'role', resource_id_key='role_id')
def update_role(role_id):
    role = db.session.get(Role, role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        new_name = data['name'].strip()
        if new_name != role.name and Role.query.filter_by(name=new_name).first():
            return jsonify({'error': 'Role already exists'}), 409
        role.name = new_name
    if 'is_active' in data:
        if role.name in PROTECTED_ROLES and not data['is_active']:
            return jsonify({'error': 'Cannot deactivate built-in role'}), 403
        role.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify({'data': role.to_dict()})


@bp.route('/<int:role_id>', methods=['DELETE'])
@admin_only
@require_csrf
@audit_action('DELETE', 'role', resource_id_key='role_id')
def delete_role(role_id):
    """Soft delete if role is in use; hard delete only if unused and not built-in."""
    role = db.session.get(Role, role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    if role.name in PROTECTED_ROLES:
        return jsonify({'error': 'Cannot delete built-in role'}), 403
    in_use = User.query.filter_by(role_id=role.id).first()
    if in_use:
        role.is_active = False
        db.session.commit()
        return jsonify({'data': role.to_dict(), 'note': 'Role deactivated because it is still in use'})
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': 'Role deleted'})
