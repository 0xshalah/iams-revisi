"""Final verification script for Paket 2 acceptance criteria."""
import os
import re

_here = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DATABASE_URL', f"sqlite:///{os.path.join(_here, 'verify_package2.db')}")

from app import create_app
from app.extensions import db
from app.models import AuditLog

app = create_app()


def dump_headers(headers):
    return {k: v for k, v in headers}


def check_jwt_only_cookie():
    """3. JWT hanya di HttpOnly cookie, tidak di body JSON."""
    print('\n[3] JWT only via HttpOnly cookie')
    client = app.test_client()
    r = client.get('/api/auth/csrf-token')
    csrf = r.json['csrf_token']
    r = client.post('/api/auth/login', json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
    assert r.status_code == 200
    body = r.get_json()
    assert 'access_token' not in body, 'JWT found in response body'
    assert 'token' not in str(body).lower(), 'Token-like value in response body'
    cookies = {c.key: (c.value, c.http_only) for c in client._cookies.values()}
    assert 'access_token' in cookies, 'access_token cookie missing'
    assert cookies['access_token'][1] is True, 'access_token cookie is not HttpOnly'
    print('PASS: JWT only in HttpOnly cookie')


def check_cors_strict():
    """5. CORS tidak wildcard, hanya FRONTEND_ORIGIN."""
    print('\n[5] CORS strict')
    client = app.test_client()
    # Preflight from allowed origin
    r = client.options('/api/auth/csrf-token', headers={
        'Origin': app.config['FRONTEND_ORIGIN'],
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'X-CSRF-Token',
    })
    acao = r.headers.get('Access-Control-Allow-Origin')
    assert acao == app.config['FRONTEND_ORIGIN'], f'CORS origin mismatch: {acao}'
    assert r.headers.get('Access-Control-Allow-Credentials') == 'true'
    # Disallowed origin
    r2 = client.options('/api/auth/csrf-token', headers={
        'Origin': 'https://evil.example.com',
        'Access-Control-Request-Method': 'POST',
    })
    assert 'Access-Control-Allow-Origin' not in r2.headers, 'CORS allowed disallowed origin'
    print('PASS: CORS only allows FRONTEND_ORIGIN')


def check_operator_rbac():
    """6. Operator tidak bisa akses Users/Roles/AuditLogs dan tidak DELETE Assets/Incidents/Problems."""
    print('\n[6] Operator RBAC')
    op = app.test_client()
    r = op.get('/api/auth/csrf-token')
    csrf = r.json['csrf_token']
    r = op.post('/api/auth/login', json={'email': 'operator@iams.local', 'password': 'operator123'},
                headers={'X-CSRF-Token': csrf})
    assert r.status_code == 200

    forbidden_gets = ['/api/users', '/api/roles', '/api/audit-logs']
    for path in forbidden_gets:
        r = op.get(path)
        assert r.status_code == 403, f'{path} should be forbidden for operator, got {r.status_code}'

    # Create an asset/incident/problem as admin first
    admin = app.test_client()
    r = admin.get('/api/auth/csrf-token')
    csrf_admin = r.json['csrf_token']
    admin.post('/api/auth/login', json={'email': 'admin@iams.local', 'password': 'admin123'},
               headers={'X-CSRF-Token': csrf_admin})
    asset = admin.post('/api/assets', json={
        'asset_tag': 'AST-RBAC-0001', 'model_id': 1, 'location_id': 1, 'status': 'Active'
    }, headers={'X-CSRF-Token': csrf_admin}).get_json()['data']
    incident = admin.post('/api/incidents', json={
        'title': 'RBAC test', 'severity': 'Low'
    }, headers={'X-CSRF-Token': csrf_admin}).get_json()['data']
    problem = admin.post('/api/problems', json={
        'title': 'RBAC test', 'priority': 'Low'
    }, headers={'X-CSRF-Token': csrf_admin}).get_json()['data']

    for path in [f"/api/assets/{asset['id']}", f"/api/incidents/{incident['id']}", f"/api/problems/{problem['id']}"]:
        r = op.delete(path, headers={'X-CSRF-Token': csrf})
        assert r.status_code == 403, f'{path} DELETE should be forbidden for operator, got {r.status_code}'

    print('PASS: Operator RBAC enforced')


def check_audit_append_only():
    """7. AuditLogs append-only, no create/update/delete public endpoints."""
    print('\n[7] AuditLogs append-only')
    client = app.test_client()
    r = client.get('/api/auth/csrf-token')
    csrf = r.json['csrf_token']
    r = client.post('/api/auth/login', json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
    for method, path in [('POST', '/api/audit-logs'), ('PUT', '/api/audit-logs/1'), ('DELETE', '/api/audit-logs/1')]:
        r = client.open(path=path, method=method, headers={'X-CSRF-Token': csrf})
        assert r.status_code in (404, 405), f'{method} {path} should not exist, got {r.status_code}'
    print('PASS: AuditLogs has no public mutating endpoints')


def check_credential_status_no_secret():
    """8. credential-status tidak mengembalikan plaintext/secret."""
    print('\n[8] Credential status no secret leak')
    client = app.test_client()
    r = client.get('/api/auth/csrf-token')
    csrf = r.json['csrf_token']
    client.post('/api/auth/login', json={'email': 'admin@iams.local', 'password': 'admin123'},
                headers={'X-CSRF-Token': csrf})
    asset = client.post('/api/assets', json={
        'asset_tag': 'AST-CRED-0001', 'model_id': 1, 'location_id': 1, 'status': 'Active'
    }, headers={'X-CSRF-Token': csrf}).get_json()['data']
    client.put(f"/api/assets/{asset['id']}/credential", json={'credential': 'super-secret'},
               headers={'X-CSRF-Token': csrf})
    r = client.get(f"/api/assets/{asset['id']}/credential-status")
    assert r.status_code == 200
    body = r.get_data(as_text=True).lower()
    for forbidden in ['super-secret', 'encrypted_secret', 'nonce', 'token', 'password']:
        assert forbidden not in body, f'credential-status leaked: {forbidden}'
    print('PASS: credential-status does not leak secrets')


def check_failed_login_audit():
    """9. Failed login logged without password/token/secret."""
    print('\n[9] Failed login audit')
    client = app.test_client()
    r = client.get('/api/auth/csrf-token')
    csrf = r.json['csrf_token']
    with app.app_context():
        before = AuditLog.query.filter_by(action='LOGIN', status='failure').count()
    r = client.post('/api/auth/login', json={'email': 'admin@iams.local', 'password': 'wrong-password'},
                    headers={'X-CSRF-Token': csrf})
    print('failed login response', r.status_code, r.json)
    with app.app_context():
        after = AuditLog.query.filter_by(action='LOGIN', status='failure').count()
        print('before', before, 'after', after)
        assert after == before + 1, f'Failed login not audited (before={before}, after={after})'
        log = AuditLog.query.filter_by(action='LOGIN', status='failure').order_by(AuditLog.id.desc()).first()
        meta = (log.metadata_redacted or '').lower()
    for forbidden in ['admin123', 'wrong-password', 'password', 'token', 'secret']:
        assert forbidden not in meta, f'Audit log contains sensitive data: {forbidden}'
    print('PASS: Failed login audited without secrets')


def check_error_500_generic():
    """10. Error 500 generic, no internal leak."""
    print('\n[10] Error 500 generic')
    client = app.test_client()
    r = client.get('/api/forced-500')
    assert r.status_code == 500, f'Expected 500, got {r.status_code}'
    body = r.get_json()
    text = r.get_data(as_text=True)
    assert body['error'] == 'Internal server error'
    for forbidden in ['/secret/', 'SELECT', 'database', 'ValueError', 'Traceback', 'JWT_SECRET', 'AES_KEY']:
        assert forbidden not in text, f'500 leaked internal detail: {forbidden}'
    print('PASS: Error 500 is generic')


if __name__ == '__main__':
    # Register temporary error route before app handles any request
    import flask
    test_bp = flask.Blueprint('test_bp', __name__)

    @test_bp.route('/api/forced-500')
    def forced_500():
        raise ValueError('internal database path /secret/query SELECT * FROM users')

    app.register_blueprint(test_bp)

    with app.app_context():
        db.drop_all()
        db.create_all()
        from app.commands import seed_command
        from click.testing import CliRunner
        CliRunner().invoke(seed_command)

    check_failed_login_audit()
    check_jwt_only_cookie()
    check_cors_strict()
    check_operator_rbac()
    check_audit_append_only()
    check_credential_status_no_secret()
    check_error_500_generic()

    print('\n=== All Paket 2 verification checks passed ===')
