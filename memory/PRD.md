# IAMS — Infrastructure Asset Management System

## Original Problem Statement
Paket 1 (Eksekusi Frontend) untuk membangun **prototype antarmuka IAMS**:
dashboard internal tim IT untuk mengelola aset jaringan (Router/Switch/Firewall/AP/Printer),
mencatat incident, mendokumentasikan problem, mengontrol akses (Users/Roles),
dan memantau Audit Logs — semuanya dengan **mock data** (tanpa backend nyata,
tanpa database, tanpa auth nyata).

Stack wajib: **Vue 3 (Composition API) + Vite + Tailwind CSS + shadcn-style components + Pinia**.

## Architecture
- **Framework**: Vue 3 + Vite (dijalankan dengan `yarn start` → vite host 0.0.0.0:3000)
- **State**: Pinia stores (`auth`, `theme`, `ui`)
- **Router**: vue-router (history mode) dengan **route guards** untuk auth & role-based access
- **UI**: komponen custom shadcn-style berbasis Tailwind (Button, Card, Badge, Input, Select,
  Label, Dialog, ConfirmDialog, ToastHost, StatusBadge, Pagination, EmptyState, ErrorState, TableSkeleton)
- **API adapter**: `src/services/apiClient.js` — sudah dibentuk siap diganti ke Flask nyata.
  Pola ready untuk `credentials: 'include'` (cookie session) tanpa menyentuh localStorage/sessionStorage.
- **Backup**: codebase React boilerplate sebelumnya dipindah ke `/app/frontend-react-backup`.
  Symlink `/app/frontend-vue → /app/frontend`.

### Folder structure
```
/app/frontend/
├── index.html, vite.config.js, tailwind.config.js, postcss.config.js, package.json
├── public/favicon.svg
└── src/
    ├── main.js, App.vue, style.css
    ├── lib/utils.js
    ├── router/index.js
    ├── stores/{auth,theme,ui}.js
    ├── data/{mockAssets,mockIncidents,mockAuth,mockAudit,mockActivity}.js
    ├── services/apiClient.js
    ├── components/ui/{Button,Card,Badge,Input,Select,Label,Dialog,ConfirmDialog,
    │                   ToastHost,StatusBadge,Pagination,EmptyState,ErrorState,TableSkeleton}.vue
    ├── layouts/DashboardLayout.vue
    └── pages/{LoginPage,DashboardPage,AssetsPage,IncidentsPage,ProblemsPage,
                UsersRolesPage,AuditLogsPage,NotFoundPage}.vue
```

## User Personas
1. **Administrator** — akses penuh (Dashboard, Assets, Incidents, Problems, Users/Roles, Audit Logs)
2. **Operator** — Dashboard, Assets, Incidents, Problems saja

## Core Requirements (static, ditetapkan PRD)
- Login simulasi (tanpa backend)
- Role-based sidebar visibility + route guards
- Theme Light/Dark/System (persist via `iams-theme`)
- Setiap halaman data: loading / empty / error state + search/filter + pagination + status badges
- Delete = ConfirmDialog
- Tidak ada token/credential di localStorage/sessionStorage
- Tidak ada `v-html` untuk data dinamis (semua via `{{ }}`)
- Mock data mengikuti schema SQL pembimbing (departments, locations, categories, brands, models,
  users, assets, network_details) dengan fokus pada Router/Switch/Firewall/AP/Printer
- MAC address ditampilkan partially-masked

## What's been implemented — 2026-01-16
- [x] Proyek Vue 3 + Vite + Tailwind di `/app/frontend` (port 3000)
- [x] Pinia stores: auth (in-memory), theme (3-mode), ui (sidebar + toast)
- [x] vue-router dengan guards (`requiresAuth`, role check)
- [x] LoginPage dengan dua-panel layout, demo accounts quick-fill, theme toggle
- [x] DashboardLayout: sidebar (desktop collapse + mobile drawer), header (theme/notifications/profile)
- [x] DashboardPage: 4 KPI cards, distribution chart (Tailwind bar chart), status breakdown,
      recent incidents list, recent activity
- [x] AssetsPage: tabel 24 aset, search & filter (kategori/status/lokasi), pagination (size 8),
      detail dialog read-only, delete confirmation, simulasi error state
- [x] IncidentsPage: 12 insiden, severity & status badges, search/filter, detail dialog, delete confirm
- [x] ProblemsPage: 6 problem, priority/status badges, related incident chips, detail & delete
- [x] UsersRolesPage (Admin only): tabel statis + role/status badges
- [x] AuditLogsPage (Admin only): tabel log dengan masking data sensitif, filter action/status
- [x] NotFoundPage (404)
- [x] Role switching via profile dropdown (UX simulasi)
- [x] Toast notifications (success/error/info/warning)
- [x] Data-testid lengkap di semua elemen interaktif & informasi penting
- [x] Mobile sidebar auto-close setelah nav (fix dari iterasi testing)

## Testing
- **Iteration 1** (`/app/test_reports/iteration_1.json`): 19/20 lulus.
  - 1 minor UX bug (mobile sidebar tidak auto-close) → **sudah diperbaiki**.
  - Verifikasi security: tidak ada token/password di localStorage atau sessionStorage.

## Backlog / Next Action Items
### P0 — Paket 2 (Backend Flask)
- Implementasi Flask backend dengan endpoint:
  `GET /api/assets`, `POST /api/assets`, `PUT /api/assets/:id`, `DELETE /api/assets/:id`,
  `GET /api/incidents`, `GET /api/problems`, `GET /api/users`, `GET /api/audit-logs`,
  `POST /api/auth/login` (cookie session HttpOnly), `POST /api/auth/logout`.
- Ganti `apiClient.js` dari mock ke fetch dengan `credentials: 'include'`.

### P1 — Penyempurnaan Frontend
- Form Create/Edit untuk Assets, Incidents, Problems (saat ini hanya read-only dialog)
- Bulk action (multi-select + bulk delete)
- Export CSV/XLSX laporan aset
- Histori perubahan per aset (timeline)
- Filter lanjutan (date range, garansi habis, dsb.)
- Refactor `DashboardLayout.vue` jadi `Sidebar.vue` + `Header.vue` + `MobileSidebar.vue`

### P2 — Quality of Life
- Save filter preset per user
- Tampilkan IP map / topology jaringan ringan (canvas/SVG)
- Konfirmasi keluar saat ada perubahan form belum tersimpan
- i18n (id/en) untuk teks UI

## Notes
- Source React boilerplate lama disimpan di `/app/frontend-react-backup` (jika perlu referensi).
- Supervisor mengelola frontend di `/app/frontend` via `yarn start` (sekarang menjalankan Vite).
- Tidak ada perubahan ke `backend/` — Paket 1 tidak menyentuh backend nyata.
