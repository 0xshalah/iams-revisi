# IAMS Strict Schema Compliance Mapping

## Executive summary

`database.sql` (from the supervisor) is the **schema/model contract** for IAMS.
It defines the tables, columns, relationships, and report queries that the
application must implement. It does **not** contain seed data (`INSERT`
statements); data is populated by the application seed command and user input.

The IAMS runtime now uses **MariaDB 10.11** so that the supervisor's
MySQL-oriented schema can be executed natively. The final schema is built in
two layers:

1. **Baseline schema** — `docs/database.mysql.compat.sql` is executed raw by
   MariaDB on first initialization. It contains the supervisor's core tables
   with SQL Server-style identifiers converted to MySQL backticks.
2. **IAMS extensions** — Alembic migration `001_mysql_extensions` adds tables
   and columns required for authentication, RBAC, credential encryption,
   incident/problem management, and audit trail.

**Verdict:** All core tables, fields, and relationships from `database.sql` are
present in the MariaDB implementation. Extension tables and columns do not
break the core schema.

## Source files

| File | Purpose |
|------|---------|
| `docs/database.original.mixed.sql` | Supervisor's original file (preserved as-is; MySQL DDL + SQL Server report queries) |
| `docs/database.mysql.compat.sql` | MariaDB/MySQL-compatible executable baseline |
| `docs/database.current.postgresql.sql` | Archived DDL snapshot of the previous PostgreSQL implementation |
| `backend/app/models.py` | SQLAlchemy model definitions |
| `backend/migrations/versions/001_mysql_extensions.py` | Alembic migration for IAMS extensions |
| `backend/app/routes/reports.py` | Report endpoints |

## Runtime architecture

```
MariaDB container
  └─ /docker-entrypoint-initdb.d/01_baseline.sql
       └─ executes docs/database.mysql.compat.sql
              ├─ core tables (departments, locations, categories, brands,
              │   users, models, assets, network_details)
              └─ report views (v_asset_full_report, v_asset_status_summary)

Backend container (after baseline is ready)
  └─ flask db upgrade
       └─ creates extension tables/columns
  └─ flask seed
       └─ inserts default roles, admin, operator, master data, sample assets
```

## Core table mapping

### 1. departments

| Field in `database.sql` | Implemented in MariaDB | Status |
|-------------------------|------------------------|--------|
| `id` INT AUTO_INCREMENT PK | `id` INT AUTO_INCREMENT PK | ✅ Match |
| `name` VARCHAR(100) NOT NULL | `name` VARCHAR(100) NOT NULL + UNIQUE | ✅ Match (unique added as extension) |

**Extension fields:** `description`, `created_at`, `updated_at`

### 2. locations

| Field in `database.sql` | Implemented in MariaDB | Status |
|-------------------------|------------------------|--------|
| `id` INT AUTO_INCREMENT PK | `id` INT AUTO_INCREMENT PK | ✅ Match |
| `name` VARCHAR(100) NOT NULL | `name` VARCHAR(100) NOT NULL | ✅ Match |
| `description` TEXT | `description` TEXT | ✅ Match |

**Extension fields:** `created_at`, `updated_at`

### 3. categories

| Field in `database.sql` | Implemented in MariaDB | Status |
|-------------------------|------------------------|--------|
| `id` INT AUTO_INCREMENT PK | `id` INT AUTO_INCREMENT PK | ✅ Match |
| `name` VARCHAR(50) NOT NULL | `name` VARCHAR(50) NOT NULL + UNIQUE | ✅ Match (unique added as extension) |

**Extension fields:** `description`, `created_at`, `updated_at`

### 4. brands

| Field in `database.sql` | Implemented in MariaDB | Status |
|-------------------------|------------------------|--------|
| `id` INT AUTO_INCREMENT PK | `id` INT AUTO_INCREMENT PK | ✅ Match |
| `name` VARCHAR(50) NOT NULL | `name` VARCHAR(50) NOT NULL + UNIQUE | ✅ Match (unique added as extension) |

**Extension fields:** `description`, `created_at`, `updated_at`

### 5. users

| Field in `database.sql` | Implemented in MariaDB | Status |
|-------------------------|------------------------|--------|
| `id` INT AUTO_INCREMENT PK | `id` INT AUTO_INCREMENT PK | ✅ Match |
| `name` VARCHAR(150) NOT NULL | `name` VARCHAR(150) NOT NULL | ✅ Match |
| `email` VARCHAR(100) | `email` VARCHAR(100) + UNIQUE | ✅ Match (unique added as extension) |
| `department_id` INT FK | `department_id` INT FK | ✅ Match |

**Extension fields:**

| Field | Rationale |
|-------|-----------|
| `password_hash` | JWT cookie-based authentication |
| `role_id` FK → `roles.id` | RBAC (Admin / Operator) |
| `is_active` | Soft-disable accounts |
| `last_login` | Security/audit tracking |
| `created_at`, `updated_at` | ORM timestamps |

### 6. models (device/asset models)

| Field in `database.sql` | Implemented in MariaDB | Status |
|-------------------------|------------------------|--------|
| `id` INT AUTO_INCREMENT PK | `id` INT AUTO_INCREMENT PK | ✅ Match |
| `name` VARCHAR(100) NOT NULL | `name` VARCHAR(100) NOT NULL | ✅ Match |
| `specifications` TEXT | `specifications` TEXT | ✅ Match |
| `brand_id` INT FK | `brand_id` INT FK | ✅ Match (nullable — strict match) |
| `category_id` INT FK | `category_id` INT FK | ✅ Match (nullable — strict match) |

**Extension fields:** `created_at`, `updated_at`

**Clarification:** The table name `models` refers to **device/asset models**
(e.g., "ISR 4331", "Catalyst 9300"), not AI/ML models.

### 7. assets

| Field in `database.sql` | Implemented in MariaDB | Status |
|-------------------------|------------------------|--------|
| `id` INT AUTO_INCREMENT PK | `id` INT AUTO_INCREMENT PK | ✅ Match |
| `asset_tag` VARCHAR(50) NOT NULL UNIQUE | `asset_tag` VARCHAR(50) NOT NULL UNIQUE | ✅ Match |
| `serial_number` VARCHAR(100) NOT NULL UNIQUE | `serial_number` VARCHAR(100) NOT NULL UNIQUE | ✅ Match |
| `po_number` VARCHAR(100) NULL | `po_number` VARCHAR(100) NULL | ✅ Match |
| `model_id` INT NOT NULL FK | `model_id` INT NOT NULL FK | ✅ Match |
| `location_id` INT NOT NULL FK | `location_id` INT NOT NULL FK | ✅ Match |
| `user_id` INT NULL FK | `user_id` INT NULL FK | ✅ Match |
| `status` ENUM('Active','Available','Repair','Disposed') DEFAULT 'Available' | `status` ENUM(...) DEFAULT 'Available' | ✅ Match |
| `purchase_date` DATE | `purchase_date` DATE | ✅ Match |
| `warranty_months` INT | `warranty_months` INT | ✅ Match |
| `os_license` VARCHAR(100) | `os_license` VARCHAR(100) | ✅ Match |
| `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP | `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP | ✅ Match |

**Extension fields:** `updated_at`

### 8. network_details

| Field in `database.sql` | Implemented in MariaDB | Status |
|-------------------------|------------------------|--------|
| `asset_id` INT PK FK | `asset_id` INT PK FK | ✅ Match (strict 1:1) |
| `ip_address` VARCHAR(45) | `ip_address` VARCHAR(45) | ✅ Match |
| `mac_address` VARCHAR(17) | `mac_address` VARCHAR(17) | ✅ Match |

**Extension fields:** `hostname`, `vlan`, `notes`, `created_at`, `updated_at`

**Design decision:** `network_details` follows `database.sql` strictly:
`asset_id` is the primary key, preserving the 1:1 relationship with `assets`.

## Relationship mapping

All foreign-key relationships from `database.sql` are preserved:

| Relationship | Status |
|--------------|--------|
| `users.department_id` → `departments.id` | ✅ |
| `models.brand_id` → `brands.id` | ✅ |
| `models.category_id` → `categories.id` | ✅ |
| `assets.model_id` → `models.id` | ✅ |
| `assets.location_id` → `locations.id` | ✅ |
| `assets.user_id` → `users.id` | ✅ |
| `network_details.asset_id` → `assets.id` | ✅ |

## Extension tables

| Table | Purpose |
|-------|---------|
| `roles` | RBAC roles (Administrator, Operator) |
| `asset_credentials` | Encrypted credentials per asset (AES-256-GCM) |
| `incidents` | Operational incident records |
| `problems` | Root-cause/problem records |
| `audit_logs` | Immutable audit trail |

## Report query coverage

The supervisor's report queries are stored as MariaDB views and also exposed as
REST endpoints:

| Query in `database.sql` | View | Endpoint | Status |
|-------------------------|------|----------|--------|
| Full asset report | `v_asset_full_report` | `GET /api/reports/assets/full` | ✅ |
| Count assets by status | `v_asset_status_summary` | `GET /api/reports/assets/status-summary` | ✅ |
| Find assets by PO | — | `GET /api/reports/assets/by-po?po_number=` | ✅ |
| Warranty expiring within N months | — | `GET /api/reports/assets/warranty-expiring?months=3` | ✅ |

## MySQL compatibility notes

The supervisor's original file uses SQL Server-style identifier quoting
(`[Column Name]`) in the report queries. The executable derivative
`docs/database.mysql.compat.sql` converts these to MySQL backticks
(`` `Column Name` ``) and wraps the queries in `CREATE OR REPLACE VIEW`
statements. The original file remains untouched in
`docs/database.original.mixed.sql`.

## Rollback

The previous PostgreSQL implementation is archived in:

- `backups/postgresql_backup_*.sql`
- `backups/docker-compose.postgresql.yml`
- `backups/.env.postgresql`
- `backups/migrations_postgresql/`
- `docs/database.current.postgresql.sql`

To rollback to PostgreSQL, restore the backed-up `docker-compose.yml`, `.env`,
and migrations, then restart the PostgreSQL containers.
