"""Production-readiness security & RBAC integration tests."""
import os
import pytest

from app import create_app
from app.extensions import db
from app.models import AuditLog, Asset


@pytest.fixture(scope='module')
def app():
    _here = os.path.dirname(os.path.abspath(__file__))
    os.environ.setdefault('DATABASE_URL', f"sqlite:///{os.path.join(_here, 'test_security.db')}")
    os.environ.setdefault('JWT_SECRET', 'test-secret-at-least-32-chars-long-for-jwt')
    os.environ.setdefault('AES_KEY_BASE64', 'MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=')
    os.environ.setdefault('FRONTEND_ORIGIN', 'http://localhost:3000')
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('COOKIE_SECURE', 'false')
    os.environ.setdefault('COOKIE_SAMESITE', 'Lax')
    os.environ['RATELIMIT_ENABLED'] = 'false'

    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        from app.commands import seed_command
        from click.testing import CliRunner
        CliRunner().invoke(seed_command)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin(client):
    r = client.get('/api/auth/csrf-token')
    csrf = r.json['csrf_token']
    r = client.post('/api/auth/login',
                    json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
    assert r.status_code == 200
    return client


@pytest.fixture()
def operator(client):
    r = client.get('/api/auth/csrf-token')
    csrf = r.json['csrf_token']
    r = client.post('/api/auth/login',
                    json={'email': 'operator@iams.local', 'password': 'operator123'},
                    headers={'X-CSRF-Token': csrf})
    assert r.status_code == 200
    return client


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class TestAuth:
    def test_admin_login_success(self, admin):
        r = admin.get('/api/auth/me')
        assert r.status_code == 200
        assert r.json['user']['role_name'] == 'Administrator'

    def test_operator_login_success(self, operator):
        r = operator.get('/api/auth/me')
        assert r.status_code == 200
        assert r.json['user']['role_name'] == 'Operator'

    def test_login_failure_generic(self, client):
        r = client.get('/api/auth/csrf-token')
        csrf = r.json['csrf_token']
        r = client.post('/api/auth/login',
                        json={'email': 'admin@iams.local', 'password': 'wrong'},
                        headers={'X-CSRF-Token': csrf})
        assert r.status_code == 401
        assert 'Invalid credentials' in r.json['error']

    def test_jwt_not_in_response_body(self, admin):
        r = admin.get('/api/auth/me')
        body = r.get_data(as_text=True).lower()
        assert 'access_token' not in body
        assert 'jwt' not in body

    def test_failed_login_audited_no_secret(self, app, client):
        with app.app_context():
            before = AuditLog.query.filter_by(action='LOGIN', status='failure').count()
        r = client.get('/api/auth/csrf-token')
        csrf = r.json['csrf_token']
        client.post('/api/auth/login',
                    json={'email': 'admin@iams.local', 'password': 'secret-password-123'},
                    headers={'X-CSRF-Token': csrf})
        with app.app_context():
            after = AuditLog.query.filter_by(action='LOGIN', status='failure').count()
            assert after == before + 1
            log = AuditLog.query.filter_by(action='LOGIN', status='failure').order_by(
                AuditLog.id.desc()).first()
            meta = (log.metadata_redacted or '').lower()
        for forbidden in ['secret-password-123', 'admin123', 'token', 'secret']:
            assert forbidden not in meta


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

class TestCsrf:
    def test_missing_csrf_rejected(self, client):
        """Unauthenticated POST to protected endpoint should be rejected."""
        r = client.post('/api/assets',
                       json={'asset_tag': 'X', 'serial_number': 'X',
                             'model_id': 1, 'location_id': 1})
        assert r.status_code in (401, 403)

    def test_auth_without_csrf_is_rejected(self, admin):
        """Admin with valid session but no CSRF header on mutating endpoint is rejected."""
        r = admin.post('/api/assets',
                       json={'asset_tag': 'AST-CSRF', 'serial_number': 'SN-CSRF',
                             'model_id': 1, 'location_id': 1})
        assert r.status_code == 403


# ---------------------------------------------------------------------------
# RBAC
# ---------------------------------------------------------------------------

class TestRbac:
    def test_operator_cannot_access_users(self, operator):
        r = operator.get('/api/users')
        assert r.status_code == 403

    def test_operator_cannot_access_roles(self, operator):
        r = operator.get('/api/roles')
        assert r.status_code == 403

    def test_operator_cannot_access_audit_logs(self, operator):
        r = operator.get('/api/audit-logs')
        assert r.status_code == 403

    def test_operator_cannot_delete_asset(self, operator):
        r = operator.delete('/api/assets/1')
        assert r.status_code == 403

    def test_operator_can_list_assets(self, operator):
        r = operator.get('/api/assets')
        assert r.status_code == 200

    def test_admin_can_access_users(self, admin):
        r = admin.get('/api/users')
        assert r.status_code == 200

    def test_admin_can_access_audit_logs(self, admin):
        r = admin.get('/api/audit-logs')
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Credential security
# ---------------------------------------------------------------------------

class TestCredentialSecurity:
    def test_credential_status_no_leak(self, admin, client):
        r = client.get('/api/auth/csrf-token')
        csrf = r.json['csrf_token']
        client.post('/api/auth/login',
                    json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
        asset = client.post('/api/assets', json={
            'asset_tag': 'AST-CRED-TEST', 'serial_number': 'SN-CRED-TEST',
            'model_id': 1, 'location_id': 1
        }, headers={'X-CSRF-Token': csrf}).get_json()['data']
        client.put(f"/api/assets/{asset['id']}/credential",
                   json={'credential': 'my-secret-password'},
                   headers={'X-CSRF-Token': csrf})
        r = client.get(f"/api/assets/{asset['id']}/credential-status")
        assert r.status_code == 200
        body = r.get_data(as_text=True).lower()
        for forbidden in ['my-secret-password', 'encrypted_secret', 'nonce', 'token']:
            assert forbidden not in body


# ---------------------------------------------------------------------------
# Asset validation
# ---------------------------------------------------------------------------

class TestAssetValidation:
    def test_create_requires_serial_number(self, admin, client):
        r = client.get('/api/auth/csrf-token')
        csrf = r.json['csrf_token']
        client.post('/api/auth/login',
                    json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
        r = client.post('/api/assets',
                        json={'asset_tag': 'AST-NOSERIAL', 'model_id': 1, 'location_id': 1},
                        headers={'X-CSRF-Token': csrf})
        assert r.status_code == 400
        assert 'serial_number' in r.json['error'].lower()

    def test_serial_number_must_be_unique(self, admin, client):
        r = client.get('/api/auth/csrf-token')
        csrf = r.json['csrf_token']
        client.post('/api/auth/login',
                    json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
        r = client.post('/api/assets', json={
            'asset_tag': 'AST-UNIQ-1', 'serial_number': 'DEMO-SN-AST-RTR-0001',
            'model_id': 1, 'location_id': 1
        }, headers={'X-CSRF-Token': csrf})
        assert r.status_code == 409

    def test_create_asset_default_status_available(self, admin, client):
        r = client.get('/api/auth/csrf-token')
        csrf = r.json['csrf_token']
        client.post('/api/auth/login',
                    json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
        r = client.post('/api/assets', json={
            'asset_tag': 'AST-DEF-STATUS', 'serial_number': 'SN-DEF-STATUS',
            'model_id': 1, 'location_id': 1
        }, headers={'X-CSRF-Token': csrf})
        assert r.status_code == 201
        assert r.json['data']['status'] == 'Available'


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

class TestAuditLog:
    def test_no_public_mutating_endpoint(self, admin, client):
        r = client.get('/api/auth/csrf-token')
        csrf = r.json['csrf_token']
        client.post('/api/auth/login',
                    json={'email': 'admin@iams.local', 'password': 'admin123'},
                    headers={'X-CSRF-Token': csrf})
        for method, path in [('POST', '/api/audit-logs'), ('PUT', '/api/audit-logs/1'),
                             ('DELETE', '/api/audit-logs/1')]:
            r = client.open(path=path, method=method, headers={'X-CSRF-Token': csrf})
            assert r.status_code in (404, 405)
