"""Authentication blueprint."""
import datetime as _dt
import secrets

import jwt
from flask import Blueprint, current_app, g, jsonify, request

from app.extensions import db, limiter
from app.models import User
from app.utils.audit import get_client_ip, log_audit
from app.utils.decorators import require_auth, require_csrf
from app.utils.security import verify_password

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _set_cookie(response, name: str, value: str, max_age: int, httponly: bool):
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        httponly=httponly,
        secure=current_app.config['COOKIE_SECURE'],
        samesite=current_app.config['COOKIE_SAMESITE'],
        path='/',
    )
    return response


@bp.route('/csrf-token', methods=['GET'])
def csrf_token():
    """Return a new CSRF token in a readable cookie + JSON body."""
    token = secrets.token_urlsafe(32)
    response = jsonify({'csrf_token': token})
    _set_cookie(response, current_app.config['CSRF_COOKIE_NAME'], token,
                max_age=8 * 60 * 60, httponly=False)
    return response


@bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def login():
    """Authenticate user and set HttpOnly JWT cookie."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first()
    valid = user and user.is_active and verify_password(password, user.password_hash)

    if not valid:
        log_audit('LOGIN', 'session', status='failure',
                  metadata={'email_prefix': email.split('@')[0] if '@' in email else '[redacted]',
                            'ip': get_client_ip()})
        return jsonify({'error': 'Invalid credentials'}), 401

    payload = {
        'sub': str(user.id),
        'role': user.role.name if user.role else None,
        'iat': _dt.datetime.now(_dt.timezone.utc),
        'exp': _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(
            seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES_SECONDS']
        ),
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET'],
                       algorithm=current_app.config['JWT_ALGORITHM'])

    user.last_login = _dt.datetime.now(_dt.timezone.utc)
    db.session.commit()

    log_audit('LOGIN', 'session', status='success',
              metadata={'user_id': user.id, 'role': user.role.name, 'ip': get_client_ip()})

    response = jsonify({'message': 'Login successful', 'user': user.to_dict()})
    _set_cookie(response, current_app.config['JWT_COOKIE_NAME'], token,
                max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES_SECONDS'], httponly=True)
    return response


@bp.route('/logout', methods=['POST'])
@require_auth
@require_csrf
def logout():
    """Clear JWT cookie."""
    response = jsonify({'message': 'Logout successful'})
    response.delete_cookie(current_app.config['JWT_COOKIE_NAME'], path='/')
    log_audit('LOGOUT', 'session', status='success',
              metadata={'user_id': getattr(g, 'current_user_id', None)})
    return response


@bp.route('/me', methods=['GET'])
@require_auth
def me():
    """Return current authenticated user."""
    return jsonify({'user': g.current_user.to_dict()})
