# IAMS — Infrastructure Asset Management System

[![Vue 3](https://img.shields.io/badge/Vue-3-4FC08D?logo=vue.js)](https://vuejs.org)
[![Flask](https://img.shields.io/badge/Flask-3-000?logo=flask)](https://flask.palletsprojects.com)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.11-003545?logo=mariadb)](https://mariadb.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green)](/LICENSE)

Dashboard internal untuk tim IT — pantau aset jaringan, tindak insiden, telusuri akar masalah, dan audit setiap perubahan. Dibangun dengan **Vue 3 + Flask + MariaDB + Docker Compose**.

![](https://img.shields.io/badge/PRD-100%25-brightgreen) ![](https://img.shields.io/badge/Tests-19%20passing-success) ![](https://img.shields.io/badge/Languages-ID%20%7C%20EN-blue)

---

## Fitur

| Modul | Deskripsi |
|-------|-----------|
| Dashboard | KPI cards, distribusi aset, status breakdown, compact no-scroll |
| Asset Management | CRUD + serial unique + network detail + credential AES-256-GCM |
| Incident Management | ITSM tracking, severity/status, assignee |
| Problem Management | Root cause analysis, priority, owner |
| Request Management | 7 tipe request, filter status/priority, due date |
| Change Management | Approve/reject workflow, risk/impact assessment |
| Master Data | Departments, Locations, Categories, Brands, Models — CRUD + delete safety |
| Users & Roles | RBAC Administrator/Operator, deactivate, delete |
| Reports | Full report, status summary, warranty watch, CSV export |
| Audit Logs | Append-only, metadata redacted, admin-only |
| Multi-language | Bahasa Indonesia & English, realtime switcher |
| Theme | Light / Dark, View Transitions API 120fps |
| Landing Page | Hero, features, FAQ, CTA — motion-v animations |

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend | Vue 3 + Vite + Pinia + TailwindCSS + vue-i18n + motion-v |
| Backend | Flask 3 + SQLAlchemy + Alembic + Gunicorn |
| Database | MariaDB 10.11 (MySQL-compatible) |
| Cache | Redis 7 (rate limiter) |
| Reverse Proxy | Nginx (TLS 1.2/1.3, gzip, security headers) |
| Container | Docker Compose |
| Security | JWT HttpOnly, CSRF, CORS, bcrypt, AES-256-GCM, rate limiting |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/0xshalah/iams-revisi.git
cd iams-revisi

# 2. Setup environment
cp .env.example .env
# Edit .env — generate JWT_SECRET and AES_KEY_BASE64

# 3. Run
docker compose up --build -d

# 4. Open
# Landing:  https://localhost
# Login:    https://localhost/login
# Admin:    admin@iams.local / admin123
# Operator: operator@iams.local / operator123
```

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Administrator | admin@iams.local | admin123 |
| Operator | operator@iams.local | operator123 |

## Project Structure

```
├── frontend/          Vue 3 + Vite + Tailwind
├── backend/           Flask + SQLAlchemy
│   ├── app/
│   │   ├── models.py       SQLAlchemy models
│   │   ├── routes/         API blueprints
│   │   └── utils/          Security, audit, pagination, decorators
│   ├── migrations/    Alembic migrations
│   └── tests/         19 pytest integration tests
├── nginx/             Reverse proxy + SSL config
├── docs/              DATABASE.md, DATABASE_MAPPING.md, PRODUCTION_HARDENING.md
├── backups/           PostgreSQL rollback files
├── database.sql       Supervisor's original schema
└── docker-compose.yml
```

## Documentation

- [`docs/DATABASE.md`](docs/DATABASE.md) — Schema overview & history
- [`docs/DATABASE_MAPPING.md`](docs/DATABASE_MAPPING.md) — Strict mapping database.sql ↔ MariaDB
- [`docs/PRODUCTION_HARDENING.md`](docs/PRODUCTION_HARDENING.md) — Deployment checklist

## Test

```bash
docker exec -e RATELIMIT_ENABLED=false iams_backend python -m pytest tests/test_security.py -v
# 19 passed
```

## License

MIT
