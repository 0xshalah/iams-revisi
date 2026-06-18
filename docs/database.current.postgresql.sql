-- ============================================================================
-- IAMS - Current PostgreSQL Schema Representation
-- ============================================================================
-- WARNING: This file is documentation-only. It is NOT executed during
-- deployment or application startup. The actual schema is managed by
-- SQLAlchemy models and Alembic migrations in backend/app/models.py and
-- backend/migrations/versions/.
--
-- Purpose:
--   Provide a human-readable DDL snapshot of the PostgreSQL schema currently
--   used by the IAMS backend, generated from the Alembic initial migration
--   (8204aec45f61_initial_schema.py).
--
-- Source of truth:
--   backend/app/models.py  (SQLAlchemy model definitions)
--   backend/migrations/    (Alembic migration scripts)
--   docker-compose.yml     (PostgreSQL 16 service configuration)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Master tables without foreign keys
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS locations (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS brands (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 2. RBAC and user management
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS roles (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id       INTEGER NOT NULL REFERENCES roles(id),
    department_id INTEGER REFERENCES departments(id),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    last_login    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 3. Asset product specification master
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS models (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name           VARCHAR(150) NOT NULL,
    brand_id       INTEGER NOT NULL REFERENCES brands(id),
    category_id    INTEGER NOT NULL REFERENCES categories(id),
    specifications TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 4. Core asset table
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assets (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_tag       VARCHAR(50) NOT NULL UNIQUE,
    serial_number   VARCHAR(100) NOT NULL UNIQUE,
    po_number       VARCHAR(100),
    model_id        INTEGER NOT NULL REFERENCES models(id),
    location_id     INTEGER NOT NULL REFERENCES locations(id),
    user_id         INTEGER REFERENCES users(id),
    status          VARCHAR(50) NOT NULL DEFAULT 'Available',
    purchase_date   DATE,
    warranty_months INTEGER,
    os_license      VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 5. Asset extensions (network, encrypted credentials)
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS network_details (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_id   INTEGER NOT NULL UNIQUE REFERENCES assets(id),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    hostname   VARCHAR(100),
    vlan       VARCHAR(50),
    notes      TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS asset_credentials (
    id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_id         INTEGER NOT NULL UNIQUE REFERENCES assets(id),
    encrypted_secret TEXT NOT NULL,
    nonce            VARCHAR(200) NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 6. Incident and problem management
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS incidents (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code        VARCHAR(50) NOT NULL UNIQUE,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    asset_id    INTEGER REFERENCES assets(id),
    severity    VARCHAR(50) NOT NULL,
    status      VARCHAR(50) NOT NULL DEFAULT 'Open',
    assignee_id INTEGER REFERENCES users(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS problems (
    id                 INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code               VARCHAR(50) NOT NULL UNIQUE,
    title              VARCHAR(255) NOT NULL,
    root_cause_summary TEXT,
    priority           VARCHAR(50) NOT NULL,
    status             VARCHAR(50) NOT NULL DEFAULT 'Open',
    owner_id           INTEGER REFERENCES users(id),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 7. Audit trail
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_logs (
    id                 INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_user_id      INTEGER REFERENCES users(id),
    action             VARCHAR(50) NOT NULL,
    resource_type      VARCHAR(100) NOT NULL,
    resource_id        VARCHAR(255),
    status             VARCHAR(50) NOT NULL,
    ip_address         VARCHAR(45),
    user_agent         TEXT,
    metadata_redacted  TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Optional helper view (informational only): complete asset report
-- Equivalent in spirit to the analytical query in database.original.mysql.sql
-- ============================================================================

CREATE OR REPLACE VIEW v_asset_full_report AS
SELECT
    a.id AS asset_id,
    a.asset_tag      AS "Asset Tag",
    a.serial_number  AS "Serial Number",
    a.po_number      AS "PO Number",
    c.name           AS "Kategori",
    b.name           AS "Merk",
    m.name           AS "Model / Tipe",
    a.status         AS "Status",
    l.name           AS "Lokasi Penempatan",
    COALESCE(u.name, 'IT Inventory / Server')    AS "Nama Pengguna",
    COALESCE(d.name, 'Infrastructure')           AS "Departemen",
    COALESCE(nd.ip_address, '-')                 AS "IP Address",
    COALESCE(nd.mac_address, '-')                AS "MAC Address",
    a.purchase_date                              AS "Tanggal Pembelian",
    GREATEST(
        0,
        a.warranty_months - (
            (EXTRACT(YEAR FROM CURRENT_DATE)::int * 12 + EXTRACT(MONTH FROM CURRENT_DATE)::int)
            - (EXTRACT(YEAR FROM a.purchase_date)::int * 12 + EXTRACT(MONTH FROM a.purchase_date)::int)
        )
    ) AS "Sisa Garansi (Bulan)"
FROM assets a
INNER JOIN models m ON a.model_id = m.id
INNER JOIN brands b ON m.brand_id = b.id
INNER JOIN categories c ON m.category_id = c.id
INNER JOIN locations l ON a.location_id = l.id
LEFT JOIN users u ON a.user_id = u.id
LEFT JOIN departments d ON u.department_id = d.id
LEFT JOIN network_details nd ON a.id = nd.asset_id
ORDER BY c.name ASC, a.asset_tag ASC;
