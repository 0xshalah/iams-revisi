-- DDL (Data Definition Language)

-- 1. Tabel Master Tanpa Foreign Key
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- 2. Tabel Master Dengan Foreign Key
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(100),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specifications TEXT,
    brand_id INT,
    category_id INT,
    FOREIGN KEY (brand_id) REFERENCES brands(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 3. Tabel Utama Aset
CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_tag VARCHAR(50) NOT NULL UNIQUE,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    po_number VARCHAR(100) NULL, -- Menyimpan Nomor Purchase Order keuangan
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

-- 4. Tabel Detail Jaringan (1:1 dengan Assets)
CREATE TABLE network_details (
    asset_id INT PRIMARY KEY,
    ip_address VARCHAR(45), -- Mengakomodasi IPv4 atau IPv6
    mac_address VARCHAR(17),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- VIEWS

-- Skrip Query SQL (Laporan Lengkap Aset)
SELECT 
    a.asset_tag AS [Asset Tag],
    a.serial_number AS [Serial Number],
    a.po_number AS [PO Number],
    c.name AS [Kategori],
    b.name AS [Merk],
    m.name AS [Model / Tipe],
    a.status AS [Status],
    l.name AS [Lokasi Penempatan],
    COALESCE(u.name, 'IT Inventory / Server') AS [Nama Pengguna],
    COALESCE(d.name, 'Infrastructure') AS [Departemen],
    COALESCE(nd.ip_address, '-') AS [IP Address],
    COALESCE(nd.mac_address, '-') AS [MAC Address],
    a.purchase_date AS [Tanggal Pembelian],
    -- Rumus untuk menghitung sisa masa garansi dalam satuan bulan
    GREATEST(0, a.warranty_months - PERIOD_DIFF(EXTRACT(YEAR_MONTH FROM CURRENT_DATE), EXTRACT(YEAR_MONTH FROM a.purchase_date))) AS [Sisa Garansi (Bulan)]
FROM 
    assets a
-- Menghubungkan ke tabel spesifikasi produk
INNER JOIN models m ON a.model_id = m.id
INNER JOIN brands b ON m.brand_id = b.id
INNER JOIN categories c ON m.category_id = c.id
-- Menghubungkan ke tabel lokasi
INNER JOIN locations l ON a.location_id = l.id
-- Menggunakan LEFT JOIN karena tidak semua aset memiliki pengguna/karyawan
LEFT JOIN users u ON a.user_id = u.id
LEFT JOIN departments d ON u.department_id = d.id
-- Menggunakan LEFT JOIN karena tidak semua aset terhubung ke IP statis jaringan
LEFT JOIN network_details nd ON a.id = nd.asset_id
ORDER BY 
    c.name ASC, a.asset_tag ASC;


-- Variasi Query Analitis untuk Manajemen IT
-- Variasi A: Menghitung Total Aset Berdasarkan Status (Untuk Monitor Stok Gudang)
SELECT 
    status AS [Status Perangkat],
    COUNT(*) AS [Jumlah Unit]
FROM 
    assets
GROUP BY 
    status;

-- Melacak Semua Perangkat yang Dibeli Menggunakan PO Tertentu
SELECT 
    a.po_number AS [PO Number],
    a.asset_tag AS [Asset Tag],
    b.name AS [Merk],
    m.name AS [Model],
    a.status AS [Status]
FROM 
    assets a
INNER JOIN models m ON a.model_id = m.id
INNER JOIN brands b ON m.brand_id = b.id
WHERE 
    a.po_number = 'PO/2026/05/0014'; -- Ganti dengan nomor PO yang dicari