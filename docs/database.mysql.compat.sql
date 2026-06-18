-- ============================================================================
-- IAMS - MySQL/MariaDB Compatible Baseline Schema
-- ============================================================================
-- SOURCE: docs/database.original.mixed.sql (supervisor's original file)
--
-- This file is a MariaDB/MySQL-compatible derivative of the supervisor's
-- original schema. The original file is preserved unchanged in
-- docs/database.original.mixed.sql.
--
-- Changes made for MariaDB/MySQL compatibility:
--   1. SQL Server-style identifier quoting [Column Name] in the report queries
--      has been converted to MySQL backtick quoting `Column Name`.
--   2. The standalone analytical SELECT statements have been wrapped into
--      CREATE VIEW statements so they persist in the database and can be used
--      by the reporting endpoints.
--
-- This file is mounted into the MariaDB container at
-- /docker-entrypoint-initdb.d/ and is executed automatically on the first
-- database initialization.
--
-- After this baseline runs, Alembic migrations add IAMS extension tables:
--   roles, asset_credentials, incidents, problems, audit_logs
--   plus required users columns for RBAC and authentication.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Master tables without foreign keys
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 2. Master tables with foreign keys
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(100),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specifications TEXT,
    brand_id INT,
    category_id INT,
    FOREIGN KEY (brand_id) REFERENCES brands(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- ----------------------------------------------------------------------------
-- 3. Core asset table
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_tag VARCHAR(50) NOT NULL UNIQUE,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    po_number VARCHAR(100) NULL,
    model_id INT NOT NULL,
    location_id INT NOT NULL,
    user_id INT NULL,
    status ENUM('Active', 'Available', 'Repair', 'Disposed') DEFAULT 'Available',
    purchase_date DATE,
    warranty_months INT,
    os_license VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- 4. Network details (1:1 with assets)
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS network_details (
    asset_id INT PRIMARY KEY,
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 5. Report views (derived from the supervisor's analytical queries)
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_asset_full_report AS
SELECT
    a.asset_tag AS `Asset Tag`,
    a.serial_number AS `Serial Number`,
    a.po_number AS `PO Number`,
    c.name AS `Kategori`,
    b.name AS `Merk`,
    m.name AS `Model / Tipe`,
    a.status AS `Status`,
    l.name AS `Lokasi Penempatan`,
    COALESCE(u.name, 'IT Inventory / Server') AS `Nama Pengguna`,
    COALESCE(d.name, 'Infrastructure') AS `Departemen`,
    COALESCE(nd.ip_address, '-') AS `IP Address`,
    COALESCE(nd.mac_address, '-') AS `MAC Address`,
    a.purchase_date AS `Tanggal Pembelian`,
    GREATEST(0, a.warranty_months - PERIOD_DIFF(EXTRACT(YEAR_MONTH FROM CURRENT_DATE), EXTRACT(YEAR_MONTH FROM a.purchase_date))) AS `Sisa Garansi (Bulan)`
FROM assets a
INNER JOIN models m ON a.model_id = m.id
INNER JOIN brands b ON m.brand_id = b.id
INNER JOIN categories c ON m.category_id = c.id
INNER JOIN locations l ON a.location_id = l.id
LEFT JOIN users u ON a.user_id = u.id
LEFT JOIN departments d ON u.department_id = d.id
LEFT JOIN network_details nd ON a.id = nd.asset_id
ORDER BY c.name ASC, a.asset_tag ASC;

CREATE OR REPLACE VIEW v_asset_status_summary AS
SELECT
    status AS `Status Perangkat`,
    COUNT(*) AS `Jumlah Unit`
FROM assets
GROUP BY status;
