:# IAMS — IT Asset Management System

## Database

IAMS runs on **MariaDB/MySQL**. The database schema is built in two layers:

1. **Baseline schema** — `docs/database.mysql.compat.sql` is executed raw on
   first MariaDB initialization. It contains the supervisor's core tables.
2. **IAMS extensions** — Additional tables and columns for RBAC, authentication,
   credential encryption, incident/problem management, and audit trail are
   managed by **SQLAlchemy** models and **Alembic** migrations in `backend/`.

For full database documentation, see:

- [`docs/DATABASE.md`](docs/DATABASE.md) — schema overview, history, and
  important notes.
- [`docs/DATABASE_MAPPING.md`](docs/DATABASE_MAPPING.md) — strict mapping
  between the supervisor's schema and the MariaDB implementation.
- [`docs/database.original.mixed.sql`](docs/database.original.mixed.sql) —
  supervisor's original file (MySQL DDL + SQL Server-style report queries;
  preserved as-is, not executed directly).
- [`docs/database.mysql.compat.sql`](docs/database.mysql.compat.sql) —
  MariaDB/MySQL-compatible executable baseline schema.
- [`docs/database.current.postgresql.sql`](docs/database.current.postgresql.sql)
  — archived DDL snapshot of the previous PostgreSQL implementation.

### Source of truth

The active database schema is defined in:

- `docs/database.mysql.compat.sql` — baseline schema
- `backend/app/models.py` — SQLAlchemy models
- `backend/migrations/versions/001_mysql_extensions.py` — extension migration

Do not edit the SQL snapshot files and expect the database to change; update
the SQLAlchemy models and create a new Alembic migration instead.

### Rollback

The previous PostgreSQL implementation is archived in `backups/` for rollback
purposes.

## Deployment

See [`docs/PRODUCTION_HARDENING.md`](docs/PRODUCTION_HARDENING.md) for the
production hardening checklist and security cleanup guide.
