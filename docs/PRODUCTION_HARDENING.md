# IAMS Paket 4 — Production Hardening & Security Cleanup

## What changed

### 1. Secret cleanup
- `.env` added to `.gitignore` — will not be tracked by source control.
- `.env.example` rewritten with placeholder values (no real secrets). Points to
  `CHANGE_ME`, `REPLACE_WITH_...` instead of demo keys.
- `.env.production.example` created with production-safe defaults and
  instructions to rotate ALL secrets before first deployment.
- All real secrets in the dev `.env` are documented as demo-only and marked
  for rotation.

### 2. Environment separation
- `config.py`: added hard safety gate that forces `DEBUG = False` when
  `FLASK_ENV != 'development'`. Even if env var is misconfigured, debug
  never leaks in production.
- Development `.env` uses `FLASK_ENV=development`, `COOKIE_SECURE=false`
  (suitable for local HTTP testing).
- Production `.env.production.example` uses `FLASK_ENV=production`,
  `COOKIE_SECURE=true`, `COOKIE_SAMESITE=Strict`.

### 3. Rate limiter production hardening
- Added `redis:7-alpine` service to `docker-compose.yml` with:
  - Append-only persistence
  - RDB snapshots every 15 minutes
  - Health check via `redis-cli ping`
- Backend `depends_on` redis (healthy) before starting.
- `requirements.txt` updated with `redis==5.0.8`.
- Rate limiter configured for production:
  - Dev: `RATELIMIT_STORAGE_URI=memory://` (works with multi-worker via fallback)
  - Prod: `RATELIMIT_STORAGE_URI=redis://redis:6379/0` (shared across gunicorn workers)

### 4. Gunicorn hardening
- Created `backend/gunicorn.conf.py`:
  - `bind = 0.0.0.0:5000`
  - `worker_class = gthread`, `threads = 2`
  - `workers = min(cpu_count, 4)`
  - `timeout = 30`, `max_requests = 5000`, `max_requests_jitter = 500`
  - Structured access log format with request duration
  - Graceful shutdown timeout 30s
- `entrypoint.sh` updated: `exec gunicorn -c /app/gunicorn.conf.py run:app`

### 5. Test coverage
- Added `tests/test_security.py` with 20+ pytest integration tests:
  - Admin/operator login success and failure
  - JWT not leaked in response body
  - Failed login audited without secrets
  - CSRF required and validated
  - Operator RBAC enforcement (users, roles, audit logs, delete operations)
  - Admin access to admin-only resources
  - Credential status endpoint does not leak plaintext or encrypted data
  - Asset serial_number required and unique
  - Asset default status is `Available`
  - Audit log has no public mutating endpoints
- `requirements.txt` updated with `pytest==8.3.5`, `pytest-flask==1.3.0`.
- Original `tests/verify_package2.py` preserved as-is.

### 6. API pagination
- Added `backend/app/utils/pagination.py` — reusable pagination helper.
- Updated list endpoints to support `?page=1&per_page=25`:
  - `GET /api/assets`
  - `GET /api/incidents`
  - `GET /api/problems`
  - `GET /api/users`
  - `GET /api/audit-logs`
- Response format:
  ```json
  {
    "data": [...],
    "page": 1,
    "per_page": 25,
    "total": 42,
    "pages": 2
  }
  ```
- `per_page` capped at 100, page defaults to 1.
- Frontend `apiClient.js` updated to fetch with `per_page=1000` for list
  methods to preserve existing client-side search/filter/pagination.
- All Vue pages updated to extract `response.data.data` (the inner array).

### 7. Health endpoint
- Added `backend/app/routes/health.py`.
- `GET /api/health` returns:
  ```json
  { "status": "healthy", "database": "connected" }
  ```
- No secrets, config values, user counts, or internal state exposed.
- Blueprint registered in `app/__init__.py`.

## Deployment checklist

Before deploying to production:

1. Rotate ALL secrets:
   - `JWT_SECRET`, `AES_KEY_BASE64`
   - `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`
   - `DATABASE_URL`

2. Update `FRONTEND_ORIGIN` to the real production domain.

3. Set environment:
   - `FLASK_ENV=production`
   - `COOKIE_SECURE=true`
   - `COOKIE_SAMESITE=Strict`
   - `RATELIMIT_STORAGE_URI=redis://redis:6379/0`

4. Add TLS termination (nginx/traefik reverse proxy with Let's Encrypt).

5. Configure database backups (automated MariaDB dump).

6. Review and adjust gunicorn workers based on server CPU.

7. Set up log aggregation (ELK, Loki, or equivalent).

8. Run `pytest tests/test_security.py` and ensure all pass.
