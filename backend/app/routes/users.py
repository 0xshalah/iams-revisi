"""Users management blueprint (Administrator only)."""
from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import User
from app.utils.audit import log_audit
from app.utils.decorators import admin_only, audit_action, require_csrf
from app.utils.pagination import paginate
from app.utils.security import hash_password

bp = Blueprint('users', __name__, url_prefix='/api/users')


@bp.route('', methods=['GET'])
@admin_only
def list_users():
    users = User.query.order_by(User.name)
    return jsonify(paginate(users))


@bp.route('', methods=['POST'])
@admin_only
@require_csrf
@audit_action('CREATE', 'user')
def create_user():
    data = request.get_json(silent=True) or {}
    required = ('name', 'email', 'password', 'role_id')
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    if User.query.filter_by(email=data['email'].strip().lower()).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        name=data['name'].strip(),
        email=data['email'].strip().lower(),
        password_hash=hash_password(data['password']),
        role_id=int(data['role_id']),
        department_id=data.get('department_id'),
        is_active=data.get('is_active', True),
    )
    db.session.add(user)
    db.session.commit()
    log_audit('CREATE', 'user', resource_id=user.id, status='success',
              metadata={'created_by': g.current_user_id})
    return jsonify({'data': user.to_dict()}), 201


@bp.route('/<int:user_id>', methods=['GET'])
@admin_only
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'data': user.to_dict()})


@bp.route('/<int:user_id>', methods=['PUT'])
@admin_only
@require_csrf
@audit_action('UPDATE', 'user', resource_id_key='user_id')
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        user.name = data['name'].strip()
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if new_email != user.email and User.query.filter_by(email=new_email).first():
            return jsonify({'error': 'Email already registered'}), 409
        user.email = new_email
    if 'password' in data and data['password']:
        user.password_hash = hash_password(data['password'])
    if 'role_id' in data:
        user.role_id = int(data['role_id'])
    if 'department_id' in data:
        user.department_id = data['department_id']
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify({'data': user.to_dict()})


@bp.route('/<int:user_id>', methods=['DELETE'])
@admin_only
@require_csrf
@audit_action('DELETE', 'user', resource_id_key='user_id')
def delete_user(user_id):
    """Hard delete user. Admin utama (ID 1) tidak bisa dihapus."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.role and user.role.name == 'Administrator' and User.query.filter_by(role_id=user.role_id).count() <= 1:
        return jsonify({'error': 'Cannot delete the last Administrator.'}), 409
    db.session.delete(user)
    db.session.commit()
    log_audit('DELETE_USER', 'user', resource_id=user_id, status='success',
              metadata={'email': user.email, 'name': user.name})
    return jsonify({'message': 'User deleted'})
