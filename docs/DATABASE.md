# IAMS Database Documentation

## Overview

IAMS uses **MariaDB/MySQL** as its production database. The baseline schema is
loaded directly from the supervisor's `database.sql` (via a MariaDB-compatible
derivative), and IAMS-specific extensions are managed by **SQLAlchemy** models
and **Alembic** migrations in the `backend/` directory.

> **Source of truth**
> - `docs/database.mysql.compat.sql` — MariaDB/MySQL executable baseline schema
> - `backend/app/models.py` — SQLAlchemy model definitions
> - `backend/migrations/` — Alembic migration scripts for IAMS extensions
> - `docker-compose.yml` — MariaDB service configuration

## Schema history

### Supervisor's original file

`docs/database.original.mixed.sql` is the file provided by the supervisor,
preserved exactly as-is. It contains:

- MySQL-compatible `CREATE TABLE` statements for the core IAMS schema.
- Report queries that use **SQL Server-style identifier quoting** (`[Column Name]`),
  which is not valid in MySQL/MariaDB.

Because of the mixed syntax, this original file is **not executed directly**.

### MariaDB-compatible derivative

`docs/database.mysql.compat.sql` is a derivative of the supervisor's file. It:

- Keeps every core `CREATE TABLE` statement unchanged.
- Converts `[Column Name]` quoting in the report queries to MySQL backtick
  quoting `` `Column Name` ``.
- Wraps the analytical queries into persistent `CREATE VIEW` statements.

This derivative is mounted into the MariaDB container and executed automatically
on first initialization.

### IAMS extensions

After the baseline schema is loaded, Alembic migrations create extension tables
and columns required by the application but not present in the supervisor's file:

- `roles` — RBAC roles.
- `asset_credentials` — Encrypted asset credentials.
- `incidents` — Incident records.
- `problems` — Problem records.
- `audit_logs` — Audit trail.
- `users.password_hash`, `users.role_id`, `users.is_active`, `users.last_login` —
  Authentication and RBAC fields.

## Tables

| Table | Purpose |
|-------|---------|
| `departments` | Organizational departments (baseline). |
| `locations` | Physical/logical locations (baseline). |
| `categories` | Asset categories (baseline). |
| `brands` | Hardware manufacturers (baseline). |
| `users` | User accounts, extended with auth/RBAC fields. |
| `models` | Device/asset models (baseline). |
| `assets` | Core IT asset records (baseline). |
| `network_details` | Network info for assets, 1:1 with `assets` (baseline). |
| `roles` | RBAC roles (extension). |
| `asset_credentials` | Encrypted credentials per asset (extension). |
| `incidents` | Incident records (extension). |
| `problems` | Problem records (extension). |
| `audit_logs` | Immutable audit trail (extension). |

## Report views

The supervisor's report queries are stored as MariaDB views:

- `v_asset_full_report` — Full asset report with category, brand, model, location,
  user, department, IP, MAC, and remaining warranty in months.
- `v_asset_status_summary` — Asset count grouped by status.

The application also exposes these reports through REST endpoints in
`backend/app/routes/reports.py`.

## Important notes

1. Do not edit the SQL snapshot files and expect the database to change. Update
   `backend/app/models.py` and create a new Alembic migration instead.

2. The original supervisor file is preserved in
   `docs/database.original.mixed.sql`. Any schema changes must be mirrored in
   `docs/database.mysql.compat.sql` if they belong to the baseline.

3. The previous PostgreSQL implementation is archived in `backups/` and in
   `docs/database.current.postgresql.sql` for rollback/reference purposes.

## Security: secret rotation and demo data

The demo `.env` contains AES and JWT secrets that are **not for production**.
If real data has been encrypted with the demo AES key, you have two options
when deploying to production:

1. **Reseed** — Wipe and re-seed the database after rotating secrets. All demo
   data and assets will be regenerated with fresh serial numbers and no
   encrypted credentials.

2. **Re-encryption migration** — If real data has already been entered and
   encrypted with the demo AES key, create an Alembic migration that decrypts
   with the old key and re-encrypts with the new key. This requires having
   both keys available during the migration window.

We recommend option 1 (reseed) for staging/demo deployments; option 2 is
appropriate when the system already holds production data.
