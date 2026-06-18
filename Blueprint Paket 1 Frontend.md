### PAKET 1: Eksekusi Frontend — Emergent.sh

[PRODUCT REQUIREMENTS DOCUMENT (PRD) - FRONTEND CONTEXT]

Product Name: Infrastructure Asset Management System (IAMS)

Objective:  
Membangun dashboard internal untuk tim operasional IT dalam mengelola aset jaringan, melacak insiden, mencatat problem, dan memantau status operasional secara terpusat.

Target Users (Personas - MVP):

1. Administrator:  
    Memiliki akses penuh ke semua modul, termasuk Dashboard, Assets, Incidents, Problems, Users/Roles, dan Audit Logs.
    
2. Operator:  
    Mengelola data aset, insiden, dan problem, tetapi tidak bisa mengelola user/role maupun melihat audit log.
    

User Stories & Core Flows:

- Sebagai pengguna, saya ingin melihat ringkasan total aset dan status jaringan di Dashboard agar bisa mengambil keputusan cepat.
    
- Sebagai Operator, saya ingin melihat tabel daftar Router/Switch/Firewall/AP/Printer yang bisa difilter dan dipaginasi untuk memudahkan pencarian.
    
- Sebagai Operator, saya ingin mencatat dan memantau Incident agar gangguan operasional dapat ditindaklanjuti.
    
- Sebagai Operator, saya ingin mencatat dan memantau Problem agar akar masalah dari insiden berulang dapat terdokumentasi.
    
- Sebagai Administrator, saya ingin melihat Users/Roles agar dapat memahami simulasi kontrol akses dalam sistem.
    
- Sebagai Administrator, saya ingin melihat Audit Logs agar dapat memantau riwayat aktivitas sistem.
    
- Sebagai pengguna, saya ingin beralih antara Light/Dark/System mode agar nyaman digunakan di berbagai kondisi pencahayaan.
    
- Sebagai pengguna, jika saya belum login, saya harus diarahkan ke halaman login.
    

---

[IMPLEMENTATION PROMPT]

!!! PERINGATAN KETAT:  
Seluruh instruksi teknis di bawah ini WAJIB diimplementasikan dengan mengacu pada entitas data, persona, dan user story yang tertulis pada [PRODUCT REQUIREMENTS DOCUMENT (PRD) - FRONTEND CONTEXT] di atas.  
!!!

[ROLE]  
Kamu adalah Senior Frontend Engineer yang ahli dalam ekosistem Vue 3, Vite, Tailwind CSS, dan shadcn-vue. Kamu sangat berfokus pada Developer Experience (DX), arsitektur Single File Component (SFC) yang bersih, dan UI/UX tingkat enterprise.

[TASK]  
Buatkan prototype antarmuka untuk aplikasi Infrastructure Asset Management System (IAMS) berdasarkan PRD di atas.

Abaikan pembuatan backend nyata, database, Docker, authentication server, atau API production. Fokus 100% pada pembuatan UI/UX, routing statis, role-based UI simulation, dan integrasi komponen shadcn-vue dengan mock data untuk simulasi.

[CONSTRAINTS & TECH STACK]

- Framework: Vue 3 dengan Composition API + Vite.
    
- Styling: Tailwind CSS.
    
- Komponen: Wajib menggunakan shadcn-vue.
    
- Theme: Implementasikan dukungan Light, Dark, dan System theme.
    
- Responsivitas: Wajib mobile, tablet, dan desktop friendly.
    
- State Management: Gunakan Pinia untuk simulasi session user, role aktif, theme, dan state UI.
    
- Data: Gunakan mock data terstruktur. Jangan membuat backend nyata.
    

[PROJECT STRUCTURE]  
Gunakan struktur folder yang rapi:

- src/pages
    
- src/components
    
- src/layouts
    
- src/router
    
- src/stores
    
- src/data
    
- src/lib
    
- src/services
    

Ketentuan struktur:

- `src/pages` berisi halaman utama seperti Dashboard, Login, Assets, Incidents, Problems, UsersRoles, dan AuditLogs.
    
- `src/components` berisi komponen reusable seperti table, card, badge, dialog, sidebar, header, dan form.
    
- `src/layouts` berisi layout utama dashboard.
    
- `src/router` berisi konfigurasi routing statis dan simulasi route guard.
    
- `src/stores` berisi Pinia store untuk session, role, theme, dan UI state.
    
- `src/data` berisi mock data.
    
- `src/services` berisi mock API adapter dan struktur `apiClient.ts` atau setara.
    
- Jangan menumpuk seluruh UI dalam satu file besar.
    
- Setiap halaman utama harus menjadi komponen terpisah.
    

[IMPORTANT SECURITY & STACK ENFORCEMENT]

1. DILARANG KERAS mengganti stack ke React, Next.js, Angular, Vuetify, Quasar, atau library UI lain.
    
2. Jika ada komponen shadcn-vue yang belum tersedia, buat komponen custom berbasis Tailwind CSS dengan gaya visual yang konsisten.
    
3. Keamanan frontend hanya bersifat simulasi UX. Semua routing guard, session user, dan role di frontend HANYA untuk simulasi tampilan. Enforcement keamanan final akan dilakukan di backend.
    
4. Pastikan default escaping pada template Vue tetap digunakan.
    
5. DILARANG menggunakan `v-html` untuk menampilkan data dari user atau mock data.
    
6. Semua teks harus dirender melalui template interpolation normal (`{{ }}`).
    
7. Jangan menyimpan token di localStorage atau sessionStorage.
    
8. Jangan hardcode business logic terlalu dalam di komponen UI.
    
9. Pisahkan mock data, state Pinia, dan API adapter agar nanti mudah diganti ke backend Flask.
    

[API ADAPTER REQUIREMENT]  
Buat struktur `src/services/apiClient.ts` atau setara.

Pada prototype awal, service boleh memakai mock adapter. Namun struktur service harus siap diganti ke API Flask nyata di tahap berikutnya.

Ketentuan:

- Siapkan pola request yang nantinya mendukung `credentials: "include"`.
    
- Jangan menyimpan token di localStorage.
    
- Jangan menyimpan token di sessionStorage.
    
- Jangan membuat backend nyata.
    
- Jangan membuat endpoint production.
    
- Semua response sementara berasal dari mock data.
    

[UI STATE REQUIREMENTS]  
Setiap halaman data wajib memiliki:

- Loading state
    
- Empty state
    
- Error state
    
- Confirmation dialog untuk aksi delete
    
- Badge/status visual untuk membedakan status data
    
- Search/filter sederhana
    
- Pagination atau simulasi pagination
    

[ROLE-BASED UI SIMULATION]  
Simulasikan minimal dua role:

1. Administrator:  
    Dapat melihat menu:
    
    - Dashboard
        
    - Assets
        
    - Incidents
        
    - Problems
        
    - Users/Roles
        
    - Audit Logs
        
2. Operator:  
    Dapat melihat menu:
    
    - Dashboard
        
    - Assets
        
    - Incidents
        
    - Problems
        

Operator tidak boleh melihat menu:

- Users/Roles
    
- Audit Logs
    

Catatan:  
Role di frontend hanya untuk simulasi tampilan, bukan enforcement keamanan final.

[NAVIGATION VISIBILITY]  
Sidebar navigation harus menyesuaikan role aktif:

- Administrator melihat menu Dashboard, Assets, Incidents, Problems, Users/Roles, dan Audit Logs.
    
- Operator melihat menu Dashboard, Assets, Incidents, dan Problems saja.
    

Tambahkan mekanisme sederhana untuk mengganti role aktif dalam mode prototype, misalnya melalui profile dropdown atau mock session switcher, agar perbedaan sidebar dapat diuji secara visual.

[FITUR UI YANG HARUS DIBANGUN]

1. Layout Utama
    
    - Sidebar navigasi interaktif.
        
    - Header berisi toggle theme, profile dropdown, notifikasi, dan role aktif.
        
    - Layout responsive untuk desktop, tablet, dan mobile.
        
2. Halaman Login
    
    - Form login modern.
        
    - Simulasi error state.
        
    - Simulasi redirect ke Dashboard setelah login.
        
    - Tidak perlu backend auth nyata.
        
3. Dashboard
    
    - Card ringkasan Total Aset, Incident Terbuka, Problem Aktif, dan Status Jaringan.
        
    - Chart statis atau visual ringkas untuk distribusi aset/status.
        
    - Recent activity list berbasis mock data.
        
    - Tampilan profesional untuk dashboard internal IT.
        
4. Halaman Manajemen Aset
    
    - Tabel data aset jaringan.
        
    - Jenis aset minimal: Router, Switch, Firewall, AP, Printer.
        
    - Field contoh: nama aset, tipe, lokasi, IP address, status, owner/operator, updated_at.
        
    - Fitur search/filter, pagination, status badge, dan Action Edit/Delete.
        
    - Gunakan Table dan Dialog/Modal dari shadcn-vue atau komponen custom Tailwind yang konsisten.
        
    - Delete wajib memakai confirmation dialog.
        
    - Jangan tampilkan plaintext credential.
        
5. Halaman Manajemen Insiden
    
    - Tabel data incident.
        
    - Field contoh: title, related asset, severity, status, assignee, created_at.
        
    - Fitur search/filter, pagination, severity badge, status badge, dan Action Edit/Delete.
        
    - Delete wajib memakai confirmation dialog.
        
    - Tampilkan loading, empty, dan error state.
        
6. Halaman Manajemen Problems
    
    - Tabel data problem.
        
    - Field contoh: title, related incidents, root cause summary, priority, status, owner, created_at.
        
    - Fitur search/filter, pagination, priority badge, status badge, dan Action Edit/Delete.
        
    - Delete wajib memakai confirmation dialog.
        
    - Tampilkan loading, empty, dan error state.
        
7. Halaman Users/Roles
    
    - Tabel statis untuk simulasi manajemen pengguna dan role.
        
    - Halaman ini hanya terlihat untuk role Administrator.
        
    - Field contoh: name, email, role, status, last_login.
        
    - Tambahkan badge role dan status.
        
    - Tidak perlu CRUD penuh, cukup tabel statis dan mock action.
        
8. Halaman Audit Logs
    
    - Tabel statis riwayat aktivitas sistem.
        
    - Halaman ini hanya terlihat untuk role Administrator.
        
    - Field contoh: actor, action, resource_type, resource_id, status, timestamp.
        
    - Jangan tampilkan secret, credential, token, atau data sensitif dalam log.
        
    - Gunakan data mock yang sudah tersamarkan.
        

[VISUAL STYLE]  
Gunakan gaya dashboard enterprise yang bersih, modern, dan profesional.

Preferensi visual:

- Minimalis.
    
- Banyak whitespace.
    
- Card jelas.
    
- Table mudah dibaca.
    
- Badge status konsisten.
    
- Tidak menggunakan warna neon berlebihan.
    
- Cocok untuk aplikasi internal IT.
    
- Light/Dark/System theme harus terlihat rapi.
    

[ACCEPTANCE CRITERIA]

- Aplikasi dapat dijalankan tanpa error.
    
- Struktur folder mengikuti instruksi secara presisi.
    
- Tidak ada stack yang diganti dari Vue 3 + Vite.
    
- Tidak ada React, Next.js, Angular, Vuetify, atau Quasar.
    
- Tidak ada penggunaan `v-html`.
    
- Tidak ada token yang disimpan di localStorage atau sessionStorage.
    
- Pemisahan mock data dan komponen UI berjalan baik melalui `src/data` dan `src/services`.
    
- Setiap halaman data memiliki loading, empty, dan error state.
    
- Sidebar berubah sesuai role aktif.
    
- Operator tidak melihat Users/Roles dan Audit Logs.
    
- Administrator melihat semua menu.
    
- Halaman Assets, Incidents, dan Problems dibuat terpisah.
    
- Halaman Users/Roles dibuat dan hanya terlihat untuk Administrator.
    
- Halaman Audit Logs dibuat dan hanya terlihat untuk Administrator.
    
- Delete action memakai confirmation dialog.
    
- Tidak ada plaintext credential yang ditampilkan di UI.