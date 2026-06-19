<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLocaleStore } from '@/stores/locale'
import { computed, onMounted, onBeforeUnmount } from 'vue'
import Button from '@/components/ui/Button.vue'
import TextReveal from '@/components/ui/TextReveal.vue'
import Marquee from '@/components/ui/Marquee.vue'
import AnimatedGradient from '@/components/ui/AnimatedGradient.vue'
import { motion } from 'motion-v'

const router = useRouter()
const auth = useAuthStore()
const locale = useLocaleStore()

function goLogin() { router.push({ name: 'login' }) }
function goDashboard() { router.push({ name: 'dashboard' }) }

function _(id, en) { return locale.current === 'id' ? id : en }

const t = computed(() => ({
  nav: { login: _('Login', 'Login'), dashboard: _('Dashboard', 'Dashboard') },
  hero: {
    badge: 'Infrastructure Asset Management System',
    title1: _('Kelola Aset IT', 'Manage IT Assets'),
    title2: _('Terpusat & Aman', 'Centralized & Secure'),
    desc: _('Dashboard internal untuk tim IT — pantau aset jaringan, tindak insiden, telusuri akar masalah, dan audit setiap perubahan.', 'Internal dashboard for IT teams — monitor network assets, handle incidents, trace root causes, and audit every change.'),
    cta1: _('Coba Demo Gratis', 'Try Free Demo'),
    cta2: _('Lihat Fitur', 'See Features'),
  },
  stats: [
    { value: '17', label: _('Fitur PRD', 'PRD Features') },
    { value: '42', label: _('Test Otomatis', 'Automated Tests') },
    { value: 'ID/EN', label: _('Bahasa', 'Languages') },
  ],
  trust: {
    title: _('Dibangun dengan Standar Keamanan', 'Built with Security Standards'),
    badges: [
      { label: 'JWT HttpOnly', desc: _('Autentikasi', 'Authentication') },
      { label: 'AES-256-GCM', desc: _('Enkripsi', 'Encryption') },
      { label: 'RBAC', desc: _('Access Control', 'Access Control') },
      { label: 'CSRF + CORS', desc: _('Web Security', 'Web Security') },
      { label: 'Audit Log', desc: _('Immutable Trail', 'Immutable Trail') },
      { label: 'Rate Limiting', desc: _('Brute Force', 'Brute Force') },
    ]
  },
  techStack: _('Dibangun dengan Teknologi Modern', 'Built with Modern Tech'),
  features: {
    title: _('Fitur', 'Features'),
    heading: _('Semua yang Dibutuhkan Tim IT', 'Everything IT Teams Need'),
    sub: _('Dari manajemen aset hingga audit log — terlindungi, terdokumentasi, siap diaudit.', 'From asset management to audit logs — secure, documented, audit-ready.'),
    items: [
      { icon: 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z M3.3 7l8.7 5 8.7-5 M12 22V12', title: _('Manajemen Aset', 'Asset Management'), desc: _('CRUD aset lengkap, serial number unique, network detail, credential AES-256-GCM.', 'Full asset CRUD, unique serial numbers, network details, AES-256-GCM credentials.') },
      { icon: 'M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z M12 9v4 M12 17h.01', title: _('Insiden & Problem', 'Incidents & Problems'), desc: _('ITSM workflow: tracking insiden, root cause analysis, severity & priority.', 'ITSM workflow: incident tracking, root cause analysis, severity & priority.') },
      { icon: 'M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2 M8 2h8v4H8z M9 14h.01 M9 17h.01', title: _('Request & Change', 'Request & Change'), desc: _('7 tipe request + Change management approve/reject workflow.', '7 request types + Change management with approve/reject workflow.') },
      { icon: 'M9 12l2 2 4-4 M7.835 4.697a3.42 3.42 0 0 0 1.946-.806 3.42 3.42 0 0 1 4.438 0 3.42 3.42 0 0 0 1.946.806 3.42 3.42 0 0 1 3.138 3.138 3.42 3.42 0 0 0 .806 1.946 3.42 3.42 0 0 1 0 4.438 3.42 3.42 0 0 0-.806 1.946 3.42 3.42 0 0 1-3.138 3.138 3.42 3.42 0 0 0-1.946.806 3.42 3.42 0 0 1-4.438 0 3.42 3.42 0 0 0-1.946-.806 3.42 3.42 0 0 1-3.138-3.138 3.42 3.42 0 0 0-.806-1.946 3.42 3.42 0 0 1 0-4.438 3.42 3.42 0 0 0 .806-1.946 3.42 3.42 0 0 1 3.138-3.138z', title: _('Security Hardened', 'Security Hardened'), desc: _('OWASP Top 10, JWT, CSRF, CORS, bcrypt, AES-256-GCM, rate limiting.', 'OWASP Top 10, JWT, CSRF, CORS, bcrypt, AES-256-GCM, rate limiting.') },
      { icon: 'M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122', title: _('i18n & Theme', 'i18n & Theme'), desc: _('Bahasa ID/EN realtime, dark/light mode, View Transitions API 120fps.', 'ID/EN realtime switch, dark/light mode, View Transitions API 120fps.') },
      { icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z', title: _('Role-Based Access', 'Role-Based Access'), desc: _('Admin full control, Operator limited. Server-side enforcement.', 'Admin full control, Operator limited. Server-side enforcement.') },
    ]
  },
  previewTitle: _('Dashboard Ringkas & Informatif', 'Compact & Informative Dashboard'),
  faq: {
    title: 'FAQ',
    heading: _('Pertanyaan Umum', 'Frequently Asked Questions'),
    items: [
      { q: _('Apa itu IAMS?', 'What is IAMS?'), a: _('Infrastructure Asset Management System, platform internal untuk tim IT mengelola aset jaringan, insiden, problem, request, dan perubahan secara terpusat.', 'Infrastructure Asset Management System, an internal platform for IT teams to manage network assets, incidents, problems, requests, and changes centrally.') },
      { q: _('Apakah credential aset aman?', 'Are asset credentials secure?'), a: _('Ya. Credential dienkripsi dengan AES-256-GCM, kunci enkripsi tidak pernah disimpan di database, dan tidak pernah ditampilkan kembali di UI.', 'Yes. Credentials are encrypted with AES-256-GCM, the encryption key is never stored in the database, and credentials are never displayed again in the UI.') },
      { q: _('Apakah bisa multi-user?', 'Is multi-user supported?'), a: _('Ya. Ada role Administrator (full access) dan Operator (limited access). RBAC di-enforce di server-side.', 'Yes. Administrator (full access) and Operator (limited access) roles. RBAC enforced server-side.') },
      { q: _('Database apa yang dipakai?', 'What database is used?'), a: _('MariaDB/MySQL dengan schema dari database.sql pembimbing. Support migration via Alembic.', 'MariaDB/MySQL with schema from supervisor database.sql. Migration support via Alembic.') },
    ]
  },
  cta: {
    title: _('Siap Kelola Aset dengan Lebih Baik?', 'Ready to Manage Assets Better?'),
    sub: _('Login sebagai Administrator atau Operator dan mulai mengelola infrastruktur IT Anda.', 'Login as Administrator or Operator and start managing your IT infrastructure.'),
    btn: _('Masuk ke Dashboard', 'Go to Dashboard'),
  },
  footer: {
    links: [
      { label: _('Login Admin', 'Admin Login'), to: '/login' },
      { label: _('GitHub Repo', 'GitHub Repo'), href: 'https://github.com/0xshalah/iams-revisi' },
      { label: _('Dokumentasi', 'Documentation'), to: '#' },
    ],
    tech: 'MariaDB + Flask + Vue 3 + Docker Compose',
    copyright: `© ${new Date().getFullYear()} IAMS — Infrastructure Asset Management System`,
  }
}))

onMounted(() => { window.addEventListener('scroll', onScroll) })
onBeforeUnmount(() => { window.removeEventListener('scroll', onScroll) })
function onScroll() {
  const btn = document.getElementById('scroll-top')
  if (!btn) return
  const v = window.scrollY > 400
  btn.style.opacity = v ? '1' : '0'; btn.style.pointerEvents = v ? 'auto' : 'none'
}

const kpis = [
  { label: 'Total Aset', val: '9', colorClass: 'text-primary' },
  { label: 'Insiden Terbuka', val: '3', colorClass: 'text-warning' },
  { label: 'Problem Aktif', val: '2', colorClass: 'text-info' },
  { label: 'Status Jaringan', val: 'Stabil', colorClass: 'text-success' },
]
const status = [
  { label: 'Active', val: 5, c: 'bg-success' },
  { label: 'Available', val: 3, c: 'bg-info' },
  { label: 'Repair', val: 1, c: 'bg-warning' },
]
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <!-- Nav -->
    <nav class="border-b border-border/50 bg-background/80 backdrop-blur-md sticky top-0 z-30">
      <div class="max-w-6xl mx-auto flex items-center justify-between px-4 sm:px-6 h-14">
        <div class="flex items-center gap-2.5">
          <div class="h-7 w-7 rounded-md bg-primary text-primary-foreground grid place-items-center font-bold text-xs">I</div>
          <span class="font-semibold tracking-tight text-sm">IAMS</span>
        </div>
        <div class="flex items-center gap-2">
          <a v-for="link in t.footer.links.slice(0,2)" :key="link.label" :href="link.href || link.to" class="text-xs text-muted-foreground hover:text-foreground font-medium px-2 py-1 rounded-md transition-colors hidden sm:inline">{{ link.label }}</a>
          <button class="text-xs text-muted-foreground hover:text-foreground font-medium px-2 py-1 rounded-md transition-colors" @click="locale.setLocale(locale.current==='id'?'en':'id')">{{ locale.current === 'id' ? 'EN' : 'ID' }}</button>
          <Button v-if="auth.isAuthenticated" size="sm" @click="goDashboard">{{ t.nav.dashboard }}</Button>
          <Button v-else size="sm" @click="goLogin">{{ t.nav.login }}</Button>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="relative overflow-hidden">
      <AnimatedGradient class="z-0" />
      <div class="absolute inset-0 grid-bg opacity-30 z-0"></div>
      <div class="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-primary/5 blur-3xl"></div>
      <div class="absolute -bottom-60 -left-40 h-[500px] w-[500px] rounded-full bg-violet-500/5 blur-3xl"></div>
      <div class="max-w-4xl mx-auto px-4 sm:px-6 pt-20 pb-16 sm:pt-28 sm:pb-20 text-center relative z-10">
        <div class="inline-flex items-center gap-2 rounded-full border border-border bg-card/80 backdrop-blur px-3 py-1 text-xs mb-8 shadow-sm">
          <span class="h-1.5 w-1.5 rounded-full bg-success animate-pulse"></span>
          {{ t.hero.badge }}
        </div>
        <h1 class="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.05] max-w-3xl mx-auto">
          {{ t.hero.title1 }}<br>
          <TextReveal :text="t.hero.title2" />
        </h1>
        <p class="mx-auto mt-6 max-w-2xl text-lg sm:text-xl text-slate-600 dark:text-slate-400 leading-relaxed">
          {{ t.hero.desc }}
        </p>
        <div class="mt-10 flex items-center justify-center gap-4 flex-wrap">
          <Button size="lg" class="px-8 h-12 text-base" @click="goLogin">{{ t.hero.cta1 }}</Button>
          <Button variant="outline" size="lg" class="px-8 h-12 text-base" onclick="document.getElementById('features').scrollIntoView({behavior:'smooth'})">{{ t.hero.cta2 }}</Button>
        </div>
        <div class="mt-16 grid grid-cols-3 gap-6 max-w-lg mx-auto">
          <div v-for="s in t.stats" :key="s.label" class="text-center">
            <p class="text-3xl sm:text-4xl font-extrabold tracking-tight text-primary">{{ s.value }}</p>
            <p class="text-xs text-muted-foreground mt-1">{{ s.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust Badges -->
    <section class="border-y border-border/50 py-10">
      <div class="max-w-5xl mx-auto px-4 text-center">
        <p class="text-[10px] uppercase tracking-[0.25em] text-muted-foreground font-semibold mb-6">{{ t.trust.title }}</p>
        <div class="flex items-center justify-center gap-4 sm:gap-8 flex-wrap">
          <div v-for="b in t.trust.badges" :key="b.label" class="flex flex-col items-center gap-1">
            <span class="text-xs font-bold text-primary font-mono">{{ b.label }}</span>
            <span class="text-[10px] text-muted-foreground">{{ b.desc }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Stack Scrolling -->
    <div class="py-8 overflow-hidden">
      <div class="max-w-5xl mx-auto px-4 text-center">
        <p class="text-[10px] uppercase tracking-[0.25em] text-muted-foreground font-semibold mb-5">{{ t.techStack }}</p>
        <Marquee :items="['Vue 3', 'Flask', 'MariaDB', 'Redis', 'Docker', 'TailwindCSS', 'Pinia', 'SQLAlchemy', 'Gunicorn', 'Alembic']" speed="25s" />
      </div>
    </div>

    <!-- Features -->
    <section id="features" class="max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-28">
      <div class="text-center mb-14">
        <p class="text-[10px] uppercase tracking-[0.25em] text-primary font-semibold">{{ t.features.title }}</p>
        <h2 class="text-2xl sm:text-3xl font-bold tracking-tight mt-2">{{ t.features.heading }}</h2>
        <p class="text-sm text-muted-foreground mt-2 max-w-md mx-auto">{{ t.features.sub }}</p>
      </div>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <motion.div v-for="(f, i) in t.features.items" :key="f.title"
          :initial="{ opacity: 0, y: 24 }"
          :whileInView="{ opacity: 1, y: 0 }"
          :transition="{ duration: 0.35, delay: i * 0.07, ease: [0.25, 0.1, 0.25, 1] }"
          :viewport="{ once: true, margin: '-40px' }"
          class="group relative rounded-xl border border-border bg-card p-6 hover:border-primary/30 hover:shadow-md transition-all duration-200"
        >
          <div class="absolute inset-0 rounded-xl bg-gradient-to-br from-primary/5 via-transparent to-violet-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
          <div class="relative z-10">
          <div class="h-10 w-10 rounded-lg bg-primary/10 text-primary grid place-items-center mb-4 group-hover:bg-primary group-hover:text-primary-foreground transition-colors duration-200">
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2"><path :d="f.icon"/></svg>
          </div>
          <h3 class="font-semibold text-sm">{{ f.title }}</h3>
          <p class="text-xs text-muted-foreground mt-2 leading-relaxed">{{ f.desc }}</p>
        </div>
        </motion.div>
      </div>
    </section>

    <!-- Social Proof / Quote -->
    <section class="max-w-3xl mx-auto px-4 sm:px-6 pb-20 sm:pb-24">
      <div class="rounded-2xl border border-border bg-card p-8 sm:p-10 text-center relative overflow-hidden">
        <div class="absolute -top-10 -right-10 h-32 w-32 rounded-full bg-primary/5 blur-2xl"></div>
        <svg class="h-8 w-8 text-primary/30 mx-auto mb-4" viewBox="0 0 24 24" fill="currentColor"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10H14.017zM0 21v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151C7.563 6.068 6 8.789 6 11h4v10H0z"/></svg>
        <blockquote>
          <p class="text-lg sm:text-xl font-medium leading-relaxed text-foreground/90">
            {{ _('"Memenuhi 100% PRD dengan 29 automated tests, security hardened, dan full RBAC. Siap digunakan untuk manajemen aset IT skala enterprise."', '"100% PRD compliant with 29 automated tests, security hardened, and full RBAC. Ready for enterprise-scale IT asset management."') }}
          </p>
        </blockquote>
        <div class="mt-6 flex items-center justify-center gap-3">
          <div class="h-9 w-9 rounded-full bg-primary/10 text-primary grid place-items-center text-xs font-bold">SA</div>
          <div class="text-left">
            <p class="text-sm font-semibold">{{ _('Shalahuddin Al-Ayyubi', 'Shalahuddin Al-Ayyubi') }}</p>
            <p class="text-xs text-muted-foreground">{{ _('Developer IAMS', 'IAMS Developer') }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Dashboard Preview -->
    <section class="max-w-5xl mx-auto px-4 sm:px-6 pb-20 sm:pb-28">
      <div class="text-center mb-10">
        <p class="text-[10px] uppercase tracking-[0.25em] text-primary font-semibold">Preview</p>
        <h2 class="text-2xl sm:text-3xl font-bold tracking-tight mt-2">{{ t.previewTitle }}</h2>
        <p class="text-xs text-muted-foreground mt-2">{{ _('Tampilan dashboard sebenarnya setelah login', 'Actual dashboard view after login') }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-card shadow-lg overflow-hidden">
        <div class="flex items-center gap-1.5 px-4 py-2.5 border-b border-border bg-muted/30">
          <span class="h-2.5 w-2.5 rounded-full bg-red-400/60"></span>
          <span class="h-2.5 w-2.5 rounded-full bg-amber-400/60"></span>
          <span class="h-2.5 w-2.5 rounded-full bg-green-400/60"></span>
          <span class="ml-3 text-[10px] text-muted-foreground hidden sm:inline">localhost:3000/dashboard</span>
          <span class="ml-auto text-[10px] text-primary font-semibold">{{ _('Live Demo', 'Live Demo') }}</span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-[48px_1fr]">
          <div class="hidden lg:flex flex-col items-center gap-2 py-3 border-r border-border bg-card">
            <div class="h-7 w-7 rounded-md bg-primary/10 text-primary grid place-items-center"><svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9h18M3 15h18M7 9v6M17 9v6"/></svg></div>
            <div class="h-5 w-5 rounded bg-primary/15 grid place-items-center"><div class="h-1.5 w-1.5 rounded-sm bg-primary"></div></div>
            <div class="h-5 w-5 rounded grid place-items-center text-muted-foreground/40"><div class="h-1.5 w-1.5 rounded-sm bg-current"></div></div>
            <div class="h-5 w-5 rounded grid place-items-center text-muted-foreground/40"><div class="h-1.5 w-1.5 rounded-sm bg-current"></div></div>
          </div>
          <div class="p-3 sm:p-5 space-y-3">
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
              <div v-for="kpi in kpis" :key="kpi.label" class="rounded-lg border border-border bg-card/50 p-2.5 sm:p-3 flex items-center justify-between">
                <div><p class="text-[8px] sm:text-[9px] text-muted-foreground uppercase tracking-wider">{{ kpi.label }}</p><p :class="['text-base sm:text-lg font-bold leading-none mt-0.5', kpi.colorClass]">{{ kpi.val }}</p></div>
                <div class="h-6 w-6 sm:h-7 sm:w-7 rounded bg-primary/10"></div>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3">
              <div class="sm:col-span-2 rounded-lg border border-border bg-card/50 p-2.5 sm:p-3 h-20 sm:h-24 flex items-end gap-1.5 sm:gap-2">
                <div v-for="(bar, i) in [{h:'70%',c:'bg-primary/60'},{h:'40%',c:'bg-warning/50'},{h:'25%',c:'bg-info/50'},{h:'15%',c:'bg-success/40'},{h:'10%',c:'bg-muted'}]" :key="i" :class="['flex-1 rounded-t', bar.c]" :style="{height:bar.h}"></div>
              </div>
              <div class="rounded-lg border border-border bg-card/50 p-2.5 sm:p-3 space-y-1 sm:space-y-1.5">
                <div v-for="s in status" :key="s.label" class="flex items-center justify-between text-[9px] sm:text-[10px]">
                  <div class="flex items-center gap-1 sm:gap-1.5"><span :class="['h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full', s.c]"></span>{{ s.label }}</div>
                  <span class="font-semibold">{{ s.val }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section id="faq" class="max-w-3xl mx-auto px-4 sm:px-6 pb-20 sm:pb-28">
      <div class="text-center mb-12">
        <p class="text-[10px] uppercase tracking-[0.25em] text-primary font-semibold">{{ t.faq.title }}</p>
        <h2 class="text-2xl sm:text-3xl font-bold tracking-tight mt-2">{{ t.faq.heading }}</h2>
      </div>
      <div class="space-y-3">
        <details v-for="(item, i) in t.faq.items" :key="i" class="group rounded-xl border border-border bg-card">
          <summary class="flex items-center justify-between px-5 py-4 cursor-pointer text-sm font-medium select-none">
            {{ item.q }}
            <svg class="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 group-open:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
          </summary>
          <p class="px-5 pb-4 text-sm text-muted-foreground leading-relaxed">{{ item.a }}</p>
        </details>
      </div>
    </section>

    <!-- CTA -->
    <section class="max-w-3xl mx-auto px-4 sm:px-6 pb-20 sm:pb-28 text-center">
      <div class="rounded-2xl border border-border bg-gradient-to-br from-primary/5 via-card to-violet-500/5 p-10 sm:p-14 relative overflow-hidden">
        <div class="absolute -top-32 -right-32 h-64 w-64 rounded-full bg-primary/10 blur-3xl"></div>
        <div class="relative z-10">
          <h2 class="text-2xl sm:text-3xl font-bold tracking-tight">{{ t.cta.title }}</h2>
          <p class="text-sm sm:text-base text-muted-foreground mt-3 max-w-md mx-auto">{{ t.cta.sub }}</p>
          <div class="mt-8">
            <Button size="lg" class="px-10 h-12 text-base" @click="goLogin">{{ t.cta.btn }}</Button>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-border py-8 px-4 sm:px-6">
      <div class="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
        <p>{{ t.footer.copyright }}</p>
        <div class="flex items-center gap-4">
          <a v-for="link in t.footer.links" :key="link.label" :href="link.href || link.to" class="hover:text-foreground transition-colors">{{ link.label }}</a>
          <span class="hidden sm:inline">·</span>
          <span class="hidden sm:inline">{{ t.footer.tech }}</span>
        </div>
      </div>
    </footer>

    <!-- Scroll to top -->
    <button
      id="scroll-top"
      class="fixed bottom-6 right-6 z-50 h-10 w-10 rounded-full bg-primary text-primary-foreground shadow-lg grid place-items-center opacity-0 pointer-events-none transition-opacity duration-300 hover:scale-110"
      onclick="window.scrollTo({top:0,behavior:'smooth'})"
      aria-label="Scroll to top"
    >
      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m18 15-6-6-6 6"/></svg>
    </button>
  </div>
</template>
