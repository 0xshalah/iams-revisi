"""Auth, CSRF, and RBAC decorators."""
import functools

import jwt
from flask import current_app, g, jsonify, request

from app.extensions import db
from app.models import User
from app.utils.audit import get_client_ip, log_audit
from app.utils.security import redact, sanitize_error_message


def _set_auth_error(status: int, message: str):
    response = jsonify({'error': message})
    response.status_code = status
    return response


def require_auth(f):
    """Verify JWT from HttpOnly cookie and load current user."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get(current_app.config['JWT_COOKIE_NAME'])
        if not token:
            log_audit('ACCESS_DENIED', 'auth', status='failure',
                      metadata={'reason': 'missing_token', 'ip': get_client_ip()})
            return _set_auth_error(401, 'Unauthorized')
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET'],
                algorithms=[current_app.config['JWT_ALGORITHM']],
            )
            user_id = payload.get('sub')
            if not user_id:
                raise jwt.InvalidTokenError('missing sub')
            user = db.session.get(User, int(str(user_id)))
            if not user or not user.is_active:
                raise jwt.InvalidTokenError('user inactive')
            g.current_user = user
            g.current_user_id = user.id
            g.current_role = user.role.name if user.role else None
        except jwt.ExpiredSignatureError:
            log_audit('ACCESS_DENIED', 'auth', status='failure',
                      metadata={'reason': 'expired_token'})
            return _set_auth_error(401, 'Unauthorized')
        except jwt.InvalidTokenError:
            log_audit('ACCESS_DENIED', 'auth', status='failure',
                      metadata={'reason': 'invalid_token'})
            return _set_auth_error(401, 'Unauthorized')
        return f(*args, **kwargs)
    return decorated


def require_csrf(f):
    """Validate CSRF token header against readable cookie for state-changing methods."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return f(*args, **kwargs)
        csrf_cookie = request.cookies.get(current_app.config['CSRF_COOKIE_NAME'])
        csrf_header = request.headers.get('X-CSRF-Token') or request.headers.get('X-Csrf-Token')
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            log_audit('ACCESS_DENIED', 'csrf', status='failure',
                      metadata={'reason': 'csrf_mismatch', 'ip': get_client_ip()})
            return _set_auth_error(403, 'Invalid CSRF token')
        return f(*args, **kwargs)
    return decorated


def require_role(*allowed_roles: str):
    """Restrict endpoint to users with one of the allowed roles."""
    def decorator(f):
        @functools.wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            role = getattr(g, 'current_role', None)
            if role not in allowed_roles:
                log_audit('ACCESS_DENIED', 'rbac', status='failure',
                          metadata={'required_roles': list(allowed_roles), 'actual_role': role})
                return _set_auth_error(403, 'Forbidden')
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_only(f):
    return require_role('Administrator')(f)


def admin_or_operator(f):
    return require_role('Administrator', 'Operator')(f)


def audit_action(action: str, resource_type: str, resource_id_key: str | None = None):
    """Decorator factory to automatically audit state-changing actions."""
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            try:
                response = f(*args, **kwargs)
                status_code = getattr(response, 'status_code', 200)
                status = 'success' if status_code < 400 else 'failure'
            except Exception as exc:
                log_audit(action, resource_type, status='failure',
                          metadata={'error': sanitize_error_message(str(exc))})
                raise
            rid = kwargs.get(resource_id_key) if resource_id_key else None
            if rid is None and request.is_json:
                rid = (request.get_json(silent=True) or {}).get('id')
            log_audit(action, resource_type, resource_id=rid, status=status,
                      metadata={'status_code': status_code})
            return response
        return decorated
    return decorator


def safe_json():
    """Return JSON body with sensitive values redacted."""
    data = request.get_json(silent=True) or {}
    return redact(data)
