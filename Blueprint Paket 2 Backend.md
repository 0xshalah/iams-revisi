### PAKET 2: Eksekusi Backend, Database, Security, dan Integrasi Frontend

[PRODUCT REQUIREMENTS DOCUMENT (PRD) - BACKEND & SECURITY CONTEXT]

Product Name:  
Infrastructure Asset Management System (IAMS)

Objective:  
Menyediakan RESTful API yang aman, terukur, dan terpusat untuk melayani frontend Vue 3 + Vite hasil Paket 1, dengan fokus utama pada pengelolaan aset infrastruktur IT, integrasi schema SQL pembimbing, perlindungan kredensial aset jaringan, RBAC, audit log, dan deployment berbasis Docker Compose.

Data Entities & Scope (MVP):

- Users & Roles
    
- Departments
    
- Locations
    
- Categories
    
- Brands
    
- Models
    
- Assets
    
- NetworkDetails
    
- AssetCredentials
    
- Incidents
    
- Problems
    
- AuditLogs
    

Security Requirements (Non-Functional Requirements):

- Aplikasi mengikuti prinsip OWASP Top 10 untuk hardening aplikasi web.
    
- MITRE ATT&CK digunakan sebagai referensi threat modeling, terutama terkait credential at-rest, akses mencurigakan, dan audit trail.
    
- Zero-trust principle di level API: frontend tidak dipercaya sebagai tempat enforcement keamanan.
    
- Semua enforcement keamanan, RBAC, validasi, audit log, dan secret handling wajib berada di backend Flask.
    
- Backend tidak boleh mengembalikan plaintext credential aset jaringan ke frontend.
    

---

[IMPLEMENTATION PROMPT]

!!! PERINGATAN KETAT:  
Seluruh instruksi teknis di bawah ini WAJIB diimplementasikan dengan mengacu pada PRD, schema SQL pembimbing, dan hasil frontend Paket 1.  
!!!

[ROLE]  
Kamu adalah Senior Backend Engineer dan DevSecOps. Kamu ahli dalam Python Flask, PostgreSQL, SQLAlchemy, Flask-Migrate/Alembic, Docker, Docker Compose, secure API design, RBAC, JWT cookie-based authentication, CSRF protection, CORS hardening, audit logging, dan encryption at-rest.

[TASK]  
Saya memiliki frontend hasil Paket 1 berbasis Vue 3 + Vite + Tailwind + Pinia di direktori `/frontend` atau `/app/frontend`.

Tugasmu:

1. Jangan generate ulang frontend dari nol.
    
2. Bangun backend Flask modular di direktori `/backend`.
    
3. Bangun schema PostgreSQL berdasarkan schema SQL pembimbing dan kebutuhan IAMS.
    
4. Integrasikan backend dengan frontend melalui RESTful API.
    
5. Ganti atau siapkan `src/services/apiClient.js` dari mock adapter menjadi fetch/axios API client dengan `credentials: "include"` untuk cookie-based auth.
    
6. Orkestrasi frontend, backend, dan PostgreSQL menggunakan Docker Compose.
    
7. Terapkan security guardrail secara ketat.
    

[CONSTRAINTS & TECH STACK]

- Backend: Python Flask.
    
- Database: PostgreSQL.
    
- ORM: SQLAlchemy.
    
- Migration: Flask-Migrate/Alembic.
    
- Deployment: Docker & Docker Compose.
    
- API: RESTful API dengan JSON response.
    
- Frontend: Vue 3 + Vite hasil Paket 1.
    
- Jangan gunakan MongoDB.
    
- Jangan gunakan FastAPI.
    
- Jangan mengganti frontend ke React/Next/Angular.
    
- Jika frontend menggunakan `.js`, jangan memaksa migrasi ke TypeScript.
    
- Ikuti struktur frontend yang sudah ada.
    

---

[FRONTEND INTEGRATION NOTE]

Frontend Paket 1 sudah selesai dengan:

- Vue 3 + Vite + Tailwind + Pinia.
    
- Login simulasi.
    
- Role-based sidebar Administrator/Operator.
    
- Halaman Dashboard, Assets, Incidents, Problems, Users/Roles, dan Audit Logs.
    
- Search, filter, pagination, status badges, detail dialog, delete confirmation.
    
- Theme Light/Dark/System.
    
- API adapter di `src/services/apiClient.js`.
    

Instruksi integrasi:

1. Jangan rebuild UI dari nol.
    
2. Jangan hapus struktur frontend yang sudah bekerja.
    
3. Ubah `src/services/apiClient.js` agar siap menggunakan backend Flask.
    
4. Gunakan `credentials: "include"` pada request agar HttpOnly Cookie dapat dikirim browser.
    
5. Jangan menyimpan JWT di localStorage/sessionStorage.
    
6. Pastikan endpoint frontend diarahkan ke base URL backend dari environment variable, misalnya `VITE_API_BASE_URL`.

Tambahan penting:

Frontend Paket 1 sudah difinalkan dengan Dashboard compact/no-scroll untuk desktop. Jangan mengubah ulang layout Dashboard, Sidebar, Header, MobileSidebar, atau struktur UI yang sudah selesai. Jangan mengembalikan widget "Insiden Terbaru" atau "Recent Activity" ke Dashboard pada Paket 2. Jika data tersebut dibutuhkan nanti, cukup sediakan API backend dan biarkan integrasi UI dilakukan di fase terpisah.

---

[SCHEMA ALIGNMENT - SUPERVISOR SQL]

Backend WAJIB mengacu pada schema SQL dari pembimbing sebagai fondasi utama modul aset.

Schema pembimbing mencakup tabel:

- departments
    
- locations
    
- categories
    
- brands
    
- users
    
- models
    
- assets
    
- network_details
    

Implementasikan schema tersebut dalam bentuk SQLAlchemy models yang kompatibel dengan PostgreSQL.

Jangan copy mentah sintaks MySQL apabila ada, seperti:

- AUTO_INCREMENT
    
- ENUM MySQL
    
- Tipe data yang tidak kompatibel langsung
    
- Alias query dengan format non-PostgreSQL
    

Sesuaikan menjadi idiom PostgreSQL/SQLAlchemy.

Mapping utama:

1. Departments:
    
    - Master departemen.
        
    - Digunakan untuk mengelompokkan user/person in charge atau aset.
        
2. Locations:
    
    - Master lokasi aset.
        
    - Digunakan oleh Assets.
        
3. Categories:
    
    - Master kategori aset.
        
    - Contoh: Router, Switch, Firewall, AP, Printer, Server, Laptop, Monitor.
        
4. Brands:
    
    - Master merk/vendor.
        
    - Contoh: Cisco, MikroTik, Fortinet, HP, Dell, Lenovo.
        
5. Models:
    
    - Master model perangkat.
        
    - Berelasi ke Brands dan Categories.
        
6. Users:
    
    - Digunakan untuk login/RBAC dan juga dapat berperan sebagai person in charge aset.
        
    - Wajib memiliki minimal field:
        
        - id
            
        - name
            
        - email
            
        - password_hash
            
        - role_id
            
        - department_id
            
        - is_active
            
        - created_at
            
        - updated_at
            
7. Roles:
    
    - Minimal role bawaan:
        
        - Administrator
            
        - Operator
            
    - Role bawaan tidak boleh dihapus.
        
8. Assets:
    
    - Tabel utama aset.
        
    - Wajib memiliki minimal field:
        
        - id
            
        - asset_tag
            
        - serial_number
            
        - po_number
            
        - model_id
            
        - location_id
            
        - user_id
            
        - status
            
        - purchase_date
            
        - warranty_months
            
        - os_license
            
        - created_at
            
        - updated_at
            
9. NetworkDetails:
    
    - Detail jaringan 1:1 dengan Assets.
        
    - Wajib memiliki minimal field:
        
        - id
            
        - asset_id
            
        - ip_address
            
        - mac_address
            
        - hostname
            
        - vlan
            
        - notes
            
        - created_at
            
        - updated_at
            
10. AssetCredentials:
    

- Tabel terpisah untuk kredensial sensitif aset jaringan.
    
- JANGAN campur password router/switch/firewall ke NetworkDetails.
    
- Wajib memiliki minimal field:
    
    - id
        
    - asset_id
        
    - encrypted_secret
        
    - nonce
        
    - created_at
        
    - updated_at
        
- Plaintext credential tidak boleh dikembalikan ke frontend.
    

11. Incidents:
    

- Digunakan untuk mencatat gangguan operasional.
    
- Wajib memiliki minimal field:
    
    - id
        
    - title
        
    - description
        
    - asset_id
        
    - severity
        
    - status
        
    - assignee_id
        
    - created_at
        
    - updated_at
        

12. Problems:
    

- Digunakan untuk root cause dan problem management.
    
- Wajib memiliki minimal field:
    
    - id
        
    - title
        
    - root_cause_summary
        
    - priority
        
    - status
        
    - owner_id
        
    - created_at
        
    - updated_at
        

13. AuditLogs:
    

- Append-only.
    
- Tidak boleh ada endpoint create/update/delete publik.
    
- Dibuat otomatis oleh backend.
    

Status asset minimal:

- Active
    
- Available
    
- Repair
    
- Disposed
    

---

[RBAC MATRIX - MVP]

Gunakan minimal dua role:

1. Administrator:
    
    - Full access Read/Create/Update/Delete ke:
        
        - Users
            
        - Roles
            
        - Assets
            
        - Incidents
            
        - Problems
            
    - Read-only access ke:
        
        - AuditLogs
            
        - Reports
            
        - Master Data
            
    - Tidak boleh mengubah atau menghapus AuditLogs karena AuditLogs bersifat append-only.
        
2. Operator:
    
    - Read/Create/Update untuk:
        
        - Assets
            
        - Incidents
            
        - Problems
            
    - Read-only untuk master data yang dibutuhkan dropdown:
        
        - Departments
            
        - Locations
            
        - Categories
            
        - Brands
            
        - Models
            
    - DILARANG mengelola Users/Roles.
        
    - DILARANG menghapus Assets/Incidents/Problems.
        
    - DILARANG mengakses AuditLogs.
        
    - DILARANG melihat plaintext credential.
        

---

[MINIMUM API ENDPOINTS]

Auth:

- POST /api/auth/login
    
- POST /api/auth/logout
    
- GET /api/auth/me
    
- GET /api/auth/csrf-token
    

Users:

- GET /api/users
    
- POST /api/users
    
- GET /api/users/:id
    
- PUT /api/users/:id
    
- DELETE /api/users/:id
    

Roles:

- GET /api/roles
    
- POST /api/roles
    
- GET /api/roles/:id
    
- PUT /api/roles/:id
    
- DELETE /api/roles/:id
    

Master Data:

- GET /api/departments
    
- GET /api/locations
    
- GET /api/categories
    
- GET /api/brands
    
- GET /api/models
    

Assets:

- GET /api/assets
    
- POST /api/assets
    
- GET /api/assets/:id
    
- PUT /api/assets/:id
    
- DELETE /api/assets/:id
    
- GET /api/assets/:id/credential-status
    

Asset Network Details:

- GET /api/assets/:id/network-details
    
- PUT /api/assets/:id/network-details
    

Incidents:

- GET /api/incidents
    
- POST /api/incidents
    
- GET /api/incidents/:id
    
- PUT /api/incidents/:id
    
- DELETE /api/incidents/:id
    

Problems:

- GET /api/problems
    
- POST /api/problems
    
- GET /api/problems/:id
    
- PUT /api/problems/:id
    
- DELETE /api/problems/:id
    

Audit Logs:

- GET /api/audit-logs
    

Reports:

- GET /api/reports/assets/full
    
- GET /api/reports/assets/status-summary
    
- GET /api/reports/assets/by-po?po_number=
    
- GET /api/reports/assets/warranty-expiring?months=3
    

Endpoint yang DILARANG:

- DILARANG membuat endpoint yang mengembalikan plaintext credential aset.
    
- DILARANG membuat endpoint create/update/delete untuk AuditLogs.
    
- DILARANG membuat endpoint yang menghapus user secara hard delete.
    
- DILARANG membuat endpoint yang menghapus role bawaan Administrator/Operator.
    

---

[USER & ROLE MANAGEMENT SAFETY]

1. Endpoint DELETE /api/users/:id:
    
    - JANGAN lakukan hard delete.
        
    - Implementasikan sebagai deactivate/soft delete user dengan `is_active=false`.
        
    - Tujuannya agar audit trail dan referensi historis tidak orphaned/rusak.
        
2. Endpoint DELETE /api/roles/:id:
    
    - JANGAN lakukan hard delete jika role masih digunakan user.
        
    - Role bawaan `Administrator` dan `Operator` TIDAK BOLEH dihapus.
        
    - Jika role custom perlu dinonaktifkan, gunakan soft delete/deactivate dengan `is_active=false`.
        

---

[CRITICAL SECURITY & CREDENTIAL MANAGEMENT]

Frontend hanya untuk UX. Semua enforcement keamanan, RBAC, validasi, audit log, dan secret handling WAJIB berada di backend Flask.

1. Password Hashing:
    
    - Password login user wajib di-hash menggunakan Argon2 atau bcrypt.
        
    - Jangan pernah menyimpan password plaintext.
        
2. Asset Credential Encryption:
    
    - Secure authentication notes/password router/switch/firewall wajib disimpan menggunakan enkripsi at-rest simetris AES-256-GCM.
        
    - Gunakan nonce/IV unik untuk setiap proses enkripsi.
        
    - Simpan encrypted secret dan nonce di tabel AssetCredentials.
        
3. AES Key Format:
    
    - Kunci AES-256-GCM wajib 32 bytes.
        
    - Dibaca dari environment variable dalam format base64.
        
    - Validasi panjang key saat startup.
        
    - Jika key tidak valid, backend harus fail fast dengan error konfigurasi yang aman.
        
    - Jangan bocorkan nilai key di log/error response.
        
4. JWT Cookie Security:
    
    - JWT wajib disimpan dalam HttpOnly Cookie.
        
    - JWT tidak boleh dikembalikan dalam response body JSON.
        
    - Jangan gunakan localStorage/sessionStorage.
        
    - Untuk production, cookie wajib:
        
        - Secure
            
        - SameSite=Lax atau Strict
            
        - expiry jelas
            
        - hanya dikirim melalui HTTPS
            
5. SPA CSRF Protection:
    
    - Session/JWT cookie harus HttpOnly.
        
    - CSRF token cookie boleh readable oleh JavaScript.
        
    - Frontend mengirim CSRF token melalui header, misalnya `X-CSRF-Token`.
        
    - Request POST/PUT/PATCH/DELETE wajib divalidasi CSRF token-nya.
        
6. CORS:
    
    - CORS hanya mengizinkan origin frontend spesifik dari environment variable.
        
    - DILARANG menggunakan wildcard `*`.
        
    - Wajib mendukung cookie credentials secara aman.
        
7. Audit Log Requirement:
    
    - AuditLogs bersifat append-only.
        
    - Jangan buat endpoint update/delete audit log.
        
    - Field minimal:
        
        - actor_user_id
            
        - action
            
        - resource_type
            
        - resource_id
            
        - status
            
        - ip_address
            
        - user_agent
            
        - created_at
            
        - metadata_redacted
            
    - AuditLogs tidak boleh menyimpan:
        
        - plaintext credential
            
        - token
            
        - AES key
            
        - JWT secret
            
        - password
            
        - secret lain
            
    - Gunakan `metadata_redacted` untuk menyimpan konteks aktivitas yang sudah disamarkan.
        
8. Credential Exposure Policy:
    
    - Backend DILARANG mengembalikan plaintext credential aset jaringan ke frontend.
        
    - Jika dekripsi diperlukan untuk proses internal server, lakukan hanya untuk operasi yang sah.
        
    - Minimalkan masa hidup plaintext secret di memori.
        
    - Jangan simpan plaintext secret di global/cache/session.
        
    - Catat akses credential ke AuditLogs dengan metadata yang sudah disamarkan.
        
    - Endpoint API hanya boleh mengembalikan status/metadata seperti `has_credential: true`.
        
9. Secret Redaction:
    
    - Semua secret wajib di-redact dari:
        
        - console log server
            
        - error response HTTP
            
        - stack trace
            
        - audit log
            
    - Error response tidak boleh membocorkan query database, path server, environment config, atau secret.
        
10. Database Migration:
    

- Gunakan Flask-Migrate/Alembic.
    
- Siapkan script inisialisasi migration.
    
- Siapkan seed minimal untuk role Administrator dan Operator.
    
- Siapkan seed contoh master data jika diperlukan.
    

11. Docker Healthcheck:
    

- Tambahkan healthcheck untuk container PostgreSQL.
    
- Tambahkan healthcheck untuk container Flask.
    
- Backend wajib menunggu database siap menerima koneksi sebelum menjalankan migration atau menerima request.
    

12. RBAC Enforcement:
    

- Setiap endpoint API sensitif wajib dilindungi decorator/middleware otorisasi berbasis role.
    
- Jangan mengandalkan role dari frontend.
    
- Role harus diverifikasi dari server-side token/session.
    

13. API Response Security:
    

- Semua error 500 harus generik.
    
- Jangan bocorkan query DB, stack trace, path server, atau config environment.
    

14. JWT Secret Management:
    

- JWT signing secret wajib dibaca dari environment variable.
    
- Tidak boleh di-hardcode.
    
- Wajib divalidasi saat startup.
    
- Jika tidak tersedia atau terlalu lemah, backend harus fail fast dengan error konfigurasi yang aman.
    

15. Login Rate Limiting & Authentication Hardening:
    

- Endpoint POST /api/auth/login wajib memiliki rate limiting atau mekanisme pembatasan percobaan login.
    
- Percobaan login gagal wajib dicatat ke AuditLogs tanpa menyimpan password, token, atau secret.
    
- Response login gagal harus generik, misalnya `Invalid credentials`.
    
- Jangan membedakan apakah email/username tidak ditemukan atau password salah.
    
- Tujuannya untuk mencegah brute-force dan user enumeration.
    

---

[DELIVERABLES YANG DIHARAPKAN]

1. File `docker-compose.yml`:
    
    - Mengorkestrasi:
        
        - frontend
            
        - backend
            
        - postgres
            
    - Lengkap dengan healthcheck.
        
    - Menggunakan network isolation.
        
    - Tidak mengekspos database ke publik jika tidak perlu.
        
2. Direktori `/backend`:
    
    - Struktur modular.
        
    - Inisialisasi Flask.
        
    - Konfigurasi database.
        
    - Blueprint API.
        
    - Middleware auth.
        
    - Middleware RBAC.
        
    - Middleware CSRF.
        
    - Error handler aman.
        
3. SQLAlchemy Models:  
    Wajib mencakup:
    
    - Roles
        
    - Users
        
    - Departments
        
    - Locations
        
    - Categories
        
    - Brands
        
    - Models
        
    - Assets
        
    - NetworkDetails
        
    - AssetCredentials
        
    - Incidents
        
    - Problems
        
    - AuditLogs
        
4. Migration:
    
    - Flask-Migrate/Alembic setup.
        
    - Initial migration.
        
    - Optional seed data untuk roles dan master data.
        
5. File `.env.example`:
    
    - Template environment variable tanpa secret asli.
        
    - Sertakan instruksi generate AES key base64.
        
    - Sertakan variabel:
        
        - DATABASE_URL
            
        - JWT_SECRET
            
        - AES_KEY_BASE64
            
        - FRONTEND_ORIGIN
            
        - FLASK_ENV
            
        - COOKIE_SECURE
            
        - COOKIE_SAMESITE
            
6. File `.gitignore`:
    
    - Pastikan `.env` tidak masuk source control.
        
7. Modul utility Python:  
    Contoh `security.py` atau `utils/security.py`, berisi:
    
    - Password hashing.
        
    - Password verification.
        
    - AES-256-GCM encryption.
        
    - AES-256-GCM decryption.
        
    - Secret redaction.
        
    - AES key validation.
        
    - JWT secret validation.
        
8. Integrasi frontend:
    
    - Update `src/services/apiClient.js` agar siap request ke backend.
        
    - Gunakan `credentials: "include"`.
        
    - Jangan simpan token di localStorage/sessionStorage.
        
    - Gunakan CSRF header untuk request state-changing.
        

---

[ACCEPTANCE CRITERIA]

General:

- Aplikasi DB, backend, dan frontend dapat di-build dan berjalan via `docker-compose up` tanpa crash.
- Backend berjalan sebagai Flask app.
- Database menggunakan PostgreSQL.
- Migration berhasil dijalankan.
- Struktur folder sesuai instruksi.
- Backend tidak mengubah ulang layout Dashboard compact/no-scroll hasil Paket 1.
- Backend tidak menambahkan kembali widget "Insiden Terbaru" atau "Recent Activity" ke Dashboard pada fase Paket 2.
- Paket 2 fokus pada backend, database, security, API, Docker, dan integrasi `apiClient.js`, bukan redesign UI.

Schema & Data:

- SQLAlchemy models mengikuti schema pembimbing.
    
- Tabel Departments, Locations, Categories, Brands, Models, Assets, NetworkDetails dibuat.
    
- AssetCredentials dipisah dari NetworkDetails.
    
- NetworkDetails hanya menyimpan data jaringan seperti IP/MAC/hostname/VLAN, bukan password.
    
- Assets memiliki field penting seperti asset_tag, serial_number, po_number, model_id, location_id, user_id, status, purchase_date, warranty_months, dan os_license.
    

API:

- Endpoint dibuat sesuai Minimum API Endpoints.
    
- Endpoint master data tersedia untuk dropdown frontend.
    
- Endpoint report asset tersedia minimal untuk full report dan status summary.
    
- Endpoint GET /api/roles/:id tersedia dan hanya dapat diakses Administrator.
    
- Tidak ada endpoint API yang mengembalikan plaintext credential aset jaringan.
    
- JWT tidak dikembalikan dalam response body JSON, melainkan murni via Set-Cookie HttpOnly.
    

RBAC:

- Endpoint Users dan Roles hanya dapat diakses Administrator.
    
- AuditLogs hanya dapat dibaca Administrator.
    
- AuditLogs tidak memiliki endpoint create/update/delete publik.
    
- Operator tidak dapat mengakses endpoint AuditLogs.
    
- Operator tidak dapat melakukan DELETE pada Assets, Incidents, dan Problems.
    
- Operator tidak dapat mengelola Users/Roles.
    
- Role bawaan Administrator dan Operator tidak dapat dihapus.
    
- Role yang masih digunakan user tidak dapat di-hard-delete.
    
- Penghapusan user menggunakan soft delete `is_active=false`.
    

Security:

- Tidak ada secret yang di-hardcode dalam source code.
    
- File `.env` tidak masuk source control.
    
- Tidak ada wildcard CORS.
    
- Request POST/PUT/PATCH/DELETE wajib divalidasi CSRF token-nya.
    
- Password user di-hash menggunakan Argon2 atau bcrypt.
    
- AES key base64 divalidasi saat startup.
    
- JWT secret divalidasi saat startup.
    
- Backend fail fast jika AES key atau JWT secret tidak valid.
    
- Endpoint login memiliki rate limiting atau pembatasan percobaan login.
    
- Percobaan login gagal tercatat di AuditLogs tanpa mengekspos password, token, atau secret.
    
- Response login gagal bersifat generik dan tidak membocorkan apakah username/email terdaftar atau tidak.
    
- Semua aksi state-changing tercatat di AuditLogs tanpa mengekspos data sensitif.
    
- AuditLogs tidak menyimpan plaintext credential, token, AES key, JWT secret, atau password.
    
- Semua error response bersifat generik dan tidak membocorkan detail internal.
    

Frontend Integration:

- `src/services/apiClient.js` menggunakan `credentials: "include"`.
    
- Frontend tidak menyimpan JWT di localStorage/sessionStorage.
    
- Frontend siap memakai CSRF token header untuk POST/PUT/PATCH/DELETE.
    
- Backend tidak mengubah ulang struktur UI frontend hasil Paket 1.
    

Final Instruction:  
Jalankan implementasi secara bertahap:

1. Validasi struktur frontend yang sudah ada.
    
2. Bangun backend Flask modular.
    
3. Implementasikan database models dan migration.
    
4. Implementasikan security utility.
    
5. Implementasikan auth, CSRF, RBAC, dan audit log.
    
6. Implementasikan API endpoints.
    
7. Integrasikan `apiClient.js`.
    
8. Jalankan docker-compose.
    
9. Pastikan seluruh acceptance criteria terpenuhi.