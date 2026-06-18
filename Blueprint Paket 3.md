### PAKET 3 — Frontend API Integration & Operational Enhancements

**Status:** Backlog / jangan dieksekusi sebelum Paket 2 selesai.  
**Target eksekusi:** Setelah backend Flask + PostgreSQL + Docker + RBAC + CSRF + AuditLogs dari Paket 2 berjalan stabil.

---

[PRODUCT REQUIREMENTS DOCUMENT (PRD) - PAKET 3 CONTEXT]

Product Name:  
Infrastructure Asset Management System (IAMS)

Objective:  
Mengintegrasikan frontend Vue 3 hasil Paket 1 dengan backend Flask hasil Paket 2 secara penuh, lalu menambahkan enhancement operasional yang relevan untuk tim IT tanpa merusak dashboard compact/no-scroll yang sudah disetujui.

Paket 3 bukan untuk membangun ulang frontend atau backend dari nol. Paket 3 hanya untuk:

1. Menyambungkan UI ke API nyata.
    
2. Mengganti mock data menjadi data dari backend.
    
3. Menambahkan fitur operasional lanjutan yang bergantung pada backend.
    
4. Menjaga tampilan tetap compact, rapi, dan enterprise.
    

---

[PREREQUISITES - WAJIB SEBELUM EKSEKUSI]

Jangan mulai Paket 3 sebelum semua kondisi berikut terpenuhi:

1. Paket 1 sudah selesai:
    
    - Frontend Vue 3 + Vite + Tailwind + Pinia sudah berjalan.
        
    - Dashboard compact/no-scroll sudah final.
        
    - Sidebar role-based Administrator/Operator sudah berjalan.
        
    - Halaman Dashboard, Assets, Incidents, Problems, Users/Roles, Audit Logs sudah ada.
        
    - Tidak ada `v-html`.
        
    - Tidak ada JWT/token di localStorage/sessionStorage.
        
2. Paket 2 sudah selesai:
    
    - Backend Flask berjalan.
        
    - PostgreSQL berjalan.
        
    - Docker Compose berjalan.
        
    - Migration berhasil.
        
    - Login backend berjalan dengan HttpOnly Cookie.
        
    - CSRF protection berjalan.
        
    - RBAC backend berjalan.
        
    - AuditLogs berjalan.
        
    - CORS tidak wildcard.
        
    - Endpoint API utama sudah tersedia.
        
    - `src/services/apiClient.js` sudah siap memakai `credentials: "include"`.
        
3. Acceptance criteria Paket 2 sudah lulus:
    
    - Tidak ada plaintext credential aset yang dikembalikan ke frontend.
        
    - Users/Roles hanya Administrator.
        
    - Operator tidak bisa DELETE Assets/Incidents/Problems.
        
    - AuditLogs hanya read-only untuk Administrator.
        
    - Login gagal generik dan rate-limited.
        
    - Failed login masuk AuditLogs tanpa secret.
        

---

[IMPLEMENTATION PROMPT]

!!! PERINGATAN KETAT:  
Paket 3 adalah fase integrasi dan enhancement. Jangan rebuild frontend dari nol. Jangan rebuild backend dari nol. Jangan merusak Dashboard compact/no-scroll yang sudah final.  
!!!

[ROLE]  
Kamu adalah Senior Frontend Engineer dan Full-Stack Integration Engineer. Kamu ahli dalam Vue 3, Vite, Pinia, Tailwind CSS, API integration, cookie-based authentication, CSRF handling, enterprise dashboard UX, dan integrasi frontend-backend secara aman.

[TASK]  
Lanjutkan project IAMS yang sudah memiliki:

- Frontend Vue 3 + Vite + Tailwind + Pinia.
    
- Backend Flask + PostgreSQL.
    
- Auth berbasis HttpOnly Cookie.
    
- CSRF protection.
    
- RBAC backend.
    
- AuditLogs.
    
- RESTful API.
    

Tugasmu adalah:

1. Mengganti mock data frontend menjadi data API nyata secara bertahap.
    
2. Menyambungkan halaman Assets, Incidents, Problems, Users/Roles, AuditLogs, dan Reports ke backend.
    
3. Menambahkan form Create/Edit yang benar-benar tersambung ke API.
    
4. Menambahkan fitur operasional: Warranty Watch, Recent Activity, Insiden Terbaru, Export CSV, dan Asset Change History.
    
5. Menjaga UI tetap compact, rapi, dan enterprise.
    
6. Menjaga seluruh guardrail security frontend.
    

---

[CONSTRAINTS & TECH STACK]

- Frontend tetap Vue 3 + Vite.
    
- State management tetap Pinia.
    
- Styling tetap Tailwind CSS.
    
- Jangan migrasi ke React/Next/Angular.
    
- Jangan migrasi ke TypeScript jika project masih `.js`.
    
- Jangan membuat backend baru.
    
- Jangan mengubah schema database besar-besaran.
    
- Jangan menaruh token di localStorage/sessionStorage.
    
- Jangan menggunakan `v-html`.
    
- Jangan menampilkan plaintext credential aset.
    
- Jangan mengubah Dashboard compact/no-scroll secara besar-besaran.
    
- Jangan mengembalikan widget tambahan ke Dashboard jika membuat scroll desktop muncul kembali.
    

---

[API INTEGRATION REQUIREMENTS]

Update `src/services/apiClient.js` agar menjadi pusat komunikasi API.

Ketentuan `apiClient.js`:

1. Gunakan `fetch` atau `axios`.
    
2. Semua request ke backend memakai `credentials: "include"`.
    
3. Base URL dibaca dari environment variable:
    
    - `VITE_API_BASE_URL`
        
4. Jangan menyimpan JWT/token di localStorage/sessionStorage.
    
5. Ambil CSRF token dari endpoint:
    
    - `GET /api/auth/csrf-token`
        
6. Untuk request state-changing, kirim CSRF token melalui header:
    
    - `X-CSRF-Token`
        
7. Request yang wajib memakai CSRF:
    
    - POST
        
    - PUT
        
    - PATCH
        
    - DELETE
        
8. Error response harus ditangani dengan aman dan user-friendly.
    
9. Jangan tampilkan raw stack trace atau detail internal backend ke UI.
    
10. Jika sesi habis atau 401, arahkan user ke halaman login.
    

---

[AUTH INTEGRATION REQUIREMENTS]

Ganti login simulasi menjadi login backend nyata.

Endpoint:

- POST /api/auth/login
    
- POST /api/auth/logout
    
- GET /api/auth/me
    
- GET /api/auth/csrf-token
    

Ketentuan:

1. Login form mengirim email/password ke backend.
    
2. Backend mengatur HttpOnly Cookie.
    
3. Frontend tidak membaca JWT.
    
4. Frontend hanya memanggil `/api/auth/me` untuk mengetahui user aktif dan role.
    
5. Setelah login sukses, redirect ke Dashboard.
    
6. Setelah logout, panggil backend logout lalu redirect ke Login.
    
7. Login gagal tampilkan pesan generik:
    
    - "Email atau password tidak valid."
        
8. Jangan tampilkan apakah email terdaftar atau tidak.
    
9. Jangan simpan password di state global.
    
10. Jangan simpan token di storage.
    

---

[RBAC UI INTEGRATION]

Frontend tetap hanya melakukan role-based UI visibility. Enforcement tetap di backend.

Role:

1. Administrator:
    
    - Dashboard
        
    - Assets
        
    - Incidents
        
    - Problems
        
    - Users/Roles
        
    - Audit Logs
        
    - Reports / Warranty Watch jika ditambahkan
        
2. Operator:
    
    - Dashboard
        
    - Assets
        
    - Incidents
        
    - Problems
        
    - Warranty Watch jika hanya read-only
        
    - Tidak melihat Users/Roles
        
    - Tidak melihat Audit Logs
        
    - Tidak melihat endpoint/admin action
        

Ketentuan:

- Sidebar mengikuti role dari `/api/auth/me`.
    
- Jika operator mencoba membuka route admin-only, tampilkan halaman 403 sederhana atau redirect ke Dashboard.
    
- Jangan hanya mengandalkan frontend. Backend tetap sumber kebenaran.
    

---

[PAGE INTEGRATION SCOPE]

1. Dashboard
    
    - Pertahankan layout compact/no-scroll.
        
    - Jangan mengembalikan widget besar yang menyebabkan scroll desktop.
        
    - KPI cards boleh mengambil data dari API summary jika tersedia.
        
    - Jangan ubah struktur utama dashboard:
        
        - 4 KPI cards
            
        - Distribusi Aset
            
        - Status Aset
            
    - Jika ingin menambahkan "Insiden Terbaru" atau "Recent Activity", gunakan mini-card compact hanya jika tetap no-scroll.
        
    - Jika menyebabkan scroll, pindahkan ke halaman Incidents atau Audit Logs.
        
2. Assets Page  
    Integrasikan dengan:
    
    - GET /api/assets
        
    - POST /api/assets
        
    - GET /api/assets/:id
        
    - PUT /api/assets/:id
        
    - DELETE /api/assets/:id
        
    - GET /api/assets/:id/network-details
        
    - PUT /api/assets/:id/network-details
        
    - GET /api/assets/:id/credential-status
        
    
    Fitur:
    
    - Data table dari API nyata.
        
    - Search/filter tetap berjalan.
        
    - Pagination bisa server-side atau client-side.
        
    - Form Create Asset.
        
    - Form Edit Asset.
        
    - Delete confirmation dialog.
        
    - Operator tidak boleh melihat tombol Delete.
        
    - Administrator boleh Delete.
        
    - Jangan tampilkan plaintext credential.
        
    - Tampilkan credential status hanya sebagai metadata:
        
        - `has_credential: true/false`
            
3. Incidents Page  
    Integrasikan dengan:
    
    - GET /api/incidents
        
    - POST /api/incidents
        
    - GET /api/incidents/:id
        
    - PUT /api/incidents/:id
        
    - DELETE /api/incidents/:id
        
    
    Fitur:
    
    - Form Create Incident.
        
    - Form Edit Incident.
        
    - Delete hanya Administrator.
        
    - Operator hanya Read/Create/Update.
        
    - Severity badge.
        
    - Status badge.
        
    - Filter berdasarkan severity/status/asset.
        
4. Problems Page  
    Integrasikan dengan:
    
    - GET /api/problems
        
    - POST /api/problems
        
    - GET /api/problems/:id
        
    - PUT /api/problems/:id
        
    - DELETE /api/problems/:id
        
    
    Fitur:
    
    - Form Create Problem.
        
    - Form Edit Problem.
        
    - Delete hanya Administrator.
        
    - Operator hanya Read/Create/Update.
        
    - Priority badge.
        
    - Status badge.
        
    - Filter berdasarkan priority/status/owner.
        
5. Users/Roles Page  
    Integrasikan dengan:
    
    - GET /api/users
        
    - POST /api/users
        
    - GET /api/users/:id
        
    - PUT /api/users/:id
        
    - DELETE /api/users/:id
        
    - GET /api/roles
        
    - GET /api/roles/:id
        
    
    Ketentuan:
    
    - Hanya Administrator.
        
    - Delete user berarti deactivate/soft delete di backend.
        
    - Tampilkan status user aktif/nonaktif.
        
    - Jangan tampilkan password hash.
        
    - Jangan tampilkan token.
        
    - Jangan tampilkan secret.
        
    - Role bawaan Administrator/Operator tidak boleh dihapus.
        
6. Audit Logs Page  
    Integrasikan dengan:
    
    - GET /api/audit-logs
        
    
    Ketentuan:
    
    - Hanya Administrator.
        
    - Read-only.
        
    - Tidak ada tombol create/edit/delete.
        
    - Tampilkan metadata yang sudah tersamarkan.
        
    - Jangan tampilkan secret.
        
    - Tambahkan filter sederhana:
        
        - actor
            
        - action
            
        - resource_type
            
        - status
            
        - date range jika mudah
            
7. Master Data Dropdowns  
    Gunakan endpoint:
    
    - GET /api/departments
        
    - GET /api/locations
        
    - GET /api/categories
        
    - GET /api/brands
        
    - GET /api/models
        
    
    Digunakan untuk:
    
    - Form Asset.
        
    - Filter Asset.
        
    - User department.
        
    - Model/brand/category display.
        

---

[OPERATIONAL ENHANCEMENTS]

Tambahkan enhancement berikut setelah integrasi API dasar stabil.

1. Warranty Watch  
    Tujuan:
    
    - Menampilkan aset yang masa garansinya akan habis.
        
    
    Endpoint:
    
    - GET /api/reports/assets/warranty-expiring?months=3
        
    
    UI:
    
    - Buat halaman atau card compact.
        
    - Jangan merusak Dashboard compact/no-scroll.
        
    - Jika dimasukkan ke Dashboard, harus berupa mini-card ringkas.
        
    - Jika membuat scroll, pindahkan ke halaman Reports atau Assets.
        
    
    Data minimal:
    
    - asset_tag
        
    - model
        
    - category
        
    - location
        
    - purchase_date
        
    - warranty_months
        
    - warranty_expiry_date
        
    - remaining_days
        
2. Recent Activity  
    Sumber data:
    
    - GET /api/audit-logs
        
    
    UI:
    
    - Tampilkan aktivitas terbaru dari AuditLogs.
        
    - Hanya Administrator jika mengikuti aturan AuditLogs.
        
    - Jangan tampilkan secret.
        
    - Gunakan metadata_redacted.
        
    
    Catatan:
    
    - Jika ingin ditampilkan ke Operator, backend harus menyediakan endpoint activity khusus yang sudah difilter dan aman. Jika belum ada, jangan tampilkan ke Operator.
        
3. Insiden Terbaru  
    Sumber data:
    
    - GET /api/incidents
        
    
    UI:
    
    - Bisa tampil di halaman Dashboard sebagai mini-widget compact jika tidak menyebabkan scroll.
        
    - Jika menyebabkan scroll, tampilkan hanya di halaman Incidents.
        
    - Tampilkan title, severity, status, related asset, created_at.
        
4. Export CSV Laporan Aset  
    Endpoint:
    
    - GET /api/reports/assets/full
        
    
    Implementasi:
    
    - Tambahkan tombol Export CSV di halaman Assets atau Reports.
        
    - Jangan export credential.
        
    - Jangan export token.
        
    - Jangan export secret.
        
    - Field aman:
        
        - asset_tag
            
        - serial_number
            
        - po_number
            
        - category
            
        - brand
            
        - model
            
        - location
            
        - department
            
        - user
            
        - ip_address
            
        - mac_address masked jika perlu
            
        - status
            
        - purchase_date
            
        - warranty_months
            
5. Asset Change History  
    Sumber:
    
    - AuditLogs dengan filter resource_type = "asset" dan resource_id = asset_id
        
    
    UI:
    
    - Tambahkan tab atau dialog "History" pada detail asset.
        
    - Hanya tampilkan aktivitas yang sudah redacted.
        
    - Jangan tampilkan credential.
        
    - Cocok untuk Administrator.
        
    - Operator boleh melihat history asset hanya jika backend mengizinkan dan data sudah aman.
        
6. Form Create/Edit  
    Tambahkan form nyata untuk:
    
    - Assets
        
    - Incidents
        
    - Problems
        
    
    Ketentuan:
    
    - Gunakan Dialog/Modal yang sudah ada.
        
    - Validasi format di frontend untuk UX.
        
    - Validasi final tetap di backend.
        
    - Tampilkan loading saat submit.
        
    - Tampilkan toast sukses/gagal.
        
    - Jangan simpan form secret di global state.
        

---

[UI/UX GUARDRAILS]

1. Jangan merusak Dashboard compact/no-scroll.
    
2. Jangan membuat sidebar melebar lagi.
    
3. Jangan memperbesar header/topbar.
    
4. Jangan menambah terlalu banyak widget di Dashboard.
    
5. Prioritaskan UI compact, rapi, dan enterprise.
    
6. Table pages boleh scroll karena datanya panjang.
    
7. Dashboard desktop harus tetap terlihat penuh dalam satu layar normal.
    
8. Mobile layout tetap boleh scroll.
    
9. Dark/Light/System theme harus tetap berfungsi.
    
10. Role-based menu tetap berfungsi.
    

---

[SECURITY GUARDRAILS]

1. Jangan gunakan `v-html`.
    
2. Jangan simpan JWT di localStorage.
    
3. Jangan simpan JWT di sessionStorage.
    
4. Jangan tampilkan plaintext credential.
    
5. Jangan tampilkan password hash.
    
6. Jangan tampilkan token.
    
7. Jangan tampilkan AES key/JWT secret.
    
8. Jangan tampilkan stack trace backend.
    
9. Jangan menampilkan raw backend error detail.
    
10. Semua POST/PUT/PATCH/DELETE harus mengirim CSRF header.
    
11. Semua request pakai `credentials: "include"`.
    
12. Jika backend mengembalikan 403, tampilkan pesan akses ditolak.
    
13. Jika backend mengembalikan 401, redirect ke login.
    
14. Jangan bypass RBAC dari frontend.
    
15. Jangan membuat mock login lagi setelah backend auth aktif.
    

---

[ERROR, LOADING, EMPTY STATE]

Setiap halaman API-driven wajib memiliki:

1. Loading state:
    
    - Saat fetch data.
        
    - Saat submit form.
        
    - Saat delete action.
        
2. Empty state:
    
    - Jika data kosong.
        
    - Gunakan pesan profesional.
        
3. Error state:
    
    - Jika API gagal.
        
    - Jangan tampilkan stack trace.
        
    - Tampilkan pesan ringkas dan aman.
        
4. Success feedback:
    
    - Toast atau alert sukses setelah create/update/delete.
        
5. Confirmation dialog:
    
    - Wajib untuk delete/deactivate.
        

---

[ACCEPTANCE CRITERIA]

General:

- Frontend tetap Vue 3 + Vite.
    
- Backend tidak dibangun ulang dari nol.
    
- UI tidak dirombak total.
    
- Dashboard compact/no-scroll tetap terjaga.
    
- Sidebar role-based tetap berjalan.
    
- Theme Light/Dark/System tetap berjalan.
    
- Mobile drawer tetap berjalan.
    

API Integration:

- `src/services/apiClient.js` menggunakan backend Flask.
    
- Semua request memakai `credentials: "include"`.
    
- CSRF token digunakan untuk POST/PUT/PATCH/DELETE.
    
- JWT tidak disimpan di localStorage/sessionStorage.
    
- Login backend berjalan.
    
- Logout backend berjalan.
    
- `/api/auth/me` digunakan untuk session user dan role.
    
- Mock data utama diganti dengan data API nyata secara bertahap.
    

Assets:

- Assets page mengambil data dari API.
    
- Create/Edit Asset berjalan.
    
- Delete Asset hanya untuk Administrator.
    
- Operator tidak melihat tombol Delete.
    
- Network details tampil tanpa credential.
    
- Credential status hanya metadata, bukan secret.
    

Incidents:

- Incidents page mengambil data dari API.
    
- Create/Edit Incident berjalan.
    
- Delete Incident hanya untuk Administrator.
    
- Severity/status badge tetap berjalan.
    

Problems:

- Problems page mengambil data dari API.
    
- Create/Edit Problem berjalan.
    
- Delete Problem hanya untuk Administrator.
    
- Priority/status badge tetap berjalan.
    

Users/Roles:

- Users/Roles hanya untuk Administrator.
    
- User deactivate/soft delete berjalan.
    
- Password hash tidak tampil.
    
- Role bawaan tidak bisa dihapus.
    

Audit Logs:

- Audit Logs hanya untuk Administrator.
    
- Audit Logs read-only.
    
- Tidak ada create/edit/delete log.
    
- Tidak ada secret dalam tampilan audit log.
    

Enhancements:

- Warranty Watch tersedia tanpa merusak dashboard compact.
    
- Recent Activity memakai AuditLogs yang sudah redacted.
    
- Insiden Terbaru memakai data API Incidents.
    
- Export CSV tidak menyertakan secret/credential.
    
- Asset Change History memakai AuditLogs redacted.
    

Security:

- Tidak ada `v-html`.
    
- Tidak ada token di localStorage/sessionStorage.
    
- Tidak ada plaintext credential di UI.
    
- Tidak ada secret di UI.
    
- Error UI tidak membocorkan detail internal.
    
- 401 redirect ke login.
    
- 403 tampil sebagai akses ditolak.
    
- Role visibility sesuai backend session.
    

Final Instruction:  
Kerjakan Paket 3 secara bertahap:

1. Audit struktur frontend yang ada.
    
2. Jangan ubah Dashboard compact/no-scroll.
    
3. Perkuat `apiClient.js`.
    
4. Integrasikan auth backend.
    
5. Integrasikan Assets API.
    
6. Integrasikan Incidents API.
    
7. Integrasikan Problems API.
    
8. Integrasikan Users/Roles untuk Administrator.
    
9. Integrasikan AuditLogs untuk Administrator.
    
10. Tambahkan Warranty Watch.
    
11. Tambahkan Export CSV.
    
12. Tambahkan Asset Change History.
    
13. Jalankan manual test untuk Administrator dan Operator.
    
14. Pastikan semua acceptance criteria terpenuhi.