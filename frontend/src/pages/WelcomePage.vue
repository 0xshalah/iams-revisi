<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLocaleStore } from '@/stores/locale'
import { computed } from 'vue'
import Button from '@/components/ui/Button.vue'
import TextReveal from '@/components/ui/TextReveal.vue'
import Marquee from '@/components/ui/Marquee.vue'
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
    badge: _('Infrastructure Asset Management System', 'Infrastructure Asset Management System'),
    title1: _('Kelola Aset IT', 'Manage IT Assets'),
    title2: _('Terpusat & Aman', 'Centralized & Secure'),
    desc: _('Dashboard internal untuk tim IT: pantau aset jaringan, tindak insiden, telusuri akar masalah, dan audit setiap perubahan.', 'Internal dashboard for IT teams: monitor network assets, handle incidents, trace root causes, and audit every change.'),
    cta1: _('Mulai Sekarang', 'Get Started'),
    cta2: _('Lihat Fitur', 'Features'),
  },
  stats: [
    { value: '17', label: _('Fitur PRD', 'PRD Features'), color: 'text-primary' },
    { value: '19', label: _('Automated Tests', 'Automated Tests'), color: 'text-success' },
    { value: 'ID/EN', label: _('Bahasa', 'Languages'), color: 'text-info' },
  ],
  features: {
    title: _('Fitur', 'Features'),
    heading: _('Semua yang Dibutuhkan Tim IT', 'Everything IT Teams Need'),
    sub: _('Dari manajemen aset hingga audit log: terlindungi, terdokumentasi, siap diaudit.', 'From asset management to audit logs: secure, documented, audit-ready.'),
    items: [
      { icon: 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z M3.3 7l8.7 5 8.7-5 M12 22V12', title: _('Manajemen Aset', 'Asset Management'), desc: _('CRUD aset lengkap, serial number unique, network detail, credential AES-256-GCM.', 'Full asset CRUD, unique serial numbers, network details, AES-256-GCM credentials.') },
      { icon: 'M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z M12 9v4 M12 17h.01', title: _('Insiden & Problem', 'Incidents & Problems'), desc: _('ITSM workflow: tracking insiden, root cause analysis, severity & priority.', 'ITSM workflow: incident tracking, root cause analysis, severity & priority.') },
      { icon: 'M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2 M8 2h8v4H8z M9 14h.01 M9 17h.01', title: _('Request & Change', 'Request & Change'), desc: _('7 tipe request + Change management approve/reject workflow.', '7 request types + Change management with approve/reject workflow.') },
      { icon: 'M9 12l2 2 4-4 M7.835 4.697a3.42 3.42 0 0 0 1.946-.806 3.42 3.42 0 0 1 4.438 0 3.42 3.42 0 0 0 1.946.806 3.42 3.42 0 0 1 3.138 3.138 3.42 3.42 0 0 0 .806 1.946 3.42 3.42 0 0 1 0 4.438 3.42 3.42 0 0 0-.806 1.946 3.42 3.42 0 0 1-3.138 3.138 3.42 3.42 0 0 0-1.946.806 3.42 3.42 0 0 1-4.438 0 3.42 3.42 0 0 0-1.946-.806 3.42 3.42 0 0 1-3.138-3.138 3.42 3.42 0 0 0-.806-1.946 3.42 3.42 0 0 1 0-4.438 3.42 3.42 0 0 0 .806-1.946 3.42 3.42 0 0 1 3.138-3.138z', title: _('Security Hardened', 'Security Hardened'), desc: _('JWT HttpOnly, CSRF, CORS, bcrypt, AES-256-GCM, rate limit, audit log.', 'JWT HttpOnly, CSRF, CORS, bcrypt, AES-256-GCM, rate limiting, audit log.') },
      { icon: 'M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122', title: _('i18n & Theme', 'i18n & Theme'), desc: _('Bahasa ID/EN realtime, dark/light mode, View Transitions API 120fps.', 'ID/EN realtime switch, dark/light mode, View Transitions API 120fps.') },
      { icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z', title: _('Role-Based Access', 'Role-Based Access'), desc: _('Admin full control, Operator limited. Server-side enforcement, bukan client-side.', 'Admin full control, Operator limited. Server-side enforcement, not client-side.') },
    ]
  },
  techStack: _('Dibangun dengan Teknologi Modern', 'Built with Modern Tech'),
  cta: {
    title: _('Siap Kelola Aset dengan Lebih Baik?', 'Ready to Manage Assets Better?'),
    sub: _('Login sebagai Administrator atau Operator dan mulai mengelola infrastruktur IT Anda.', 'Login as Administrator or Operator and start managing your IT infrastructure.'),
    btn: _('Masuk ke Dashboard', 'Go to Dashboard'),
  },
  faq: {
    title: _('FAQ', 'FAQ'),
    heading: _('Pertanyaan Umum', 'Frequently Asked Questions'),
    items: [
      { q: _('Apa itu IAMS?', 'What is IAMS?'), a: _('Infrastructure Asset Management System, platform internal untuk tim IT mengelola aset jaringan, insiden, problem, request, dan perubahan secara terpusat.', 'Infrastructure Asset Management System, an internal platform for IT teams to manage network assets, incidents, problems, requests, and changes centrally.') },
      { q: _('Apakah credential aset aman?', 'Are asset credentials secure?'), a: _('Ya. Credential dienkripsi dengan AES-256-GCM, kunci enkripsi tidak pernah disimpan di database, dan tidak pernah ditampilkan kembali di UI.', 'Yes. Credentials are encrypted with AES-256-GCM, the encryption key is never stored in the database, and credentials are never displayed again in the UI.') },
      { q: _('Apakah bisa multi-user?', 'Is multi-user supported?'), a: _('Ya. Ada role Administrator (full access) dan Operator (limited access). RBAC di-enforce di server-side.', 'Yes. Administrator (full access) and Operator (limited access) roles. RBAC enforced server-side.') },
      { q: _('Database apa yang dipakai?', 'What database is used?'), a: _('MariaDB/MySQL dengan schema dari database.sql pembimbing. Support migration via Alembic.', "MariaDB/MySQL with schema from supervisor database.sql. Migration support via Alembic.") },
    ]
  }
}))
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
          <button class="text-xs text-muted-foreground hover:text-foreground font-medium px-2 py-1 rounded-md transition-colors" @click="locale.setLocale(locale.current==='id'?'en':'id')">
            {{ locale.current === 'id' ? 'EN' : 'ID' }}
          </button>
          <Button v-if="auth.isAuthenticated" size="sm" @click="goDashboard">{{ t.nav.dashboard }}</Button>
          <Button v-else size="sm" @click="goLogin">{{ t.nav.login }}</Button>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 grid-bg opacity-30"></div>
      <div class="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-primary/5 blur-3xl"></div>
      <div class="absolute -bottom-60 -left-40 h-[500px] w-[500px] rounded-full bg-violet-500/5 blur-3xl"></div>
      <div class="max-w-4xl mx-auto px-4 sm:px-6 pt-20 pb-16 sm:pt-28 sm:pb-20 text-center relative z-10">
        <!-- Hero Illustration -->
        <div class="hidden lg:block absolute -right-16 top-1/2 -translate-y-1/2 w-[400px] h-[320px] opacity-20 dark:opacity-15 pointer-events-none">
          <svg viewBox="0 0 400 320" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="20" y="60" width="80" height="120" rx="6" stroke="currentColor" stroke-width="1.5" class="text-primary"/>
            <rect x="28" y="74" width="64" height="8" rx="3" fill="currentColor" class="text-primary/40"/>
            <rect x="28" y="88" width="50" height="8" rx="3" fill="currentColor" class="text-primary/30"/>
            <rect x="28" y="102" width="58" height="8" rx="3" fill="currentColor" class="text-primary/25"/>
            <circle cx="60" cy="160" r="4" fill="currentColor" class="text-success"/>
            <circle cx="60" cy="180" r="4" fill="currentColor" class="text-success"/>
            <rect x="120" y="100" width="80" height="100" rx="6" stroke="currentColor" stroke-width="1.5" class="text-primary"/>
            <rect x="128" y="114" width="64" height="8" rx="3" fill="currentColor" class="text-primary/40"/>
            <rect x="128" y="128" width="44" height="8" rx="3" fill="currentColor" class="text-primary/25"/>
            <rect x="128" y="142" width="56" height="8" rx="3" fill="currentColor" class="text-primary/30"/>
            <circle cx="160" cy="180" r="4" fill="currentColor" class="text-success"/>
            <rect x="220" y="30" width="70" height="90" rx="6" stroke="currentColor" stroke-width="1.5" class="text-primary"/>
            <rect x="228" y="44" width="54" height="8" rx="3" fill="currentColor" class="text-primary/35"/>
            <rect x="228" y="58" width="42" height="8" rx="3" fill="currentColor" class="text-primary/25"/>
            <circle cx="255" cy="100" r="4" fill="currentColor" class="text-success"/>
            <circle cx="255" cy="120" r="4" fill="currentColor" class="text-warning"/>
            <rect x="300" y="140" width="70" height="70" rx="6" stroke="currentColor" stroke-width="1.5" class="text-primary"/>
            <rect x="308" y="154" width="54" height="8" rx="3" fill="currentColor" class="text-primary/30"/>
            <rect x="308" y="168" width="40" height="8" rx="3" fill="currentColor" class="text-primary/25"/>
            <circle cx="335" cy="190" r="4" fill="currentColor" class="text-warning"/>
            <path d="M100 160 L120 150 M180 150 L200 120 M160 180 L160 300 M255 120 L290 140 L300 140 M335 190 L340 220" stroke="currentColor" stroke-width="1" class="text-muted-foreground/40" stroke-dasharray="4 4"/>
            <circle cx="40" cy="260" r="5" fill="currentColor" class="text-info/40"/>
            <circle cx="200" cy="290" r="4" fill="currentColor" class="text-info/30"/>
            <circle cx="340" cy="250" r="5" fill="currentColor" class="text-info/40"/>
            <rect x="120" y="280" width="80" height="30" rx="5" stroke="currentColor" stroke-width="1" class="text-muted-foreground/30"/>
            <rect x="128" y="288" width="64" height="6" rx="2" fill="currentColor" class="text-muted-foreground/20"/>
            <line x1="160" y1="280" x2="160" y2="260" stroke="currentColor" stroke-width="1.5" class="text-muted-foreground/40"/>
            <line x1="120" y1="280" x2="100" y2="260" stroke="currentColor" stroke-width="1.5" class="text-muted-foreground/30"/>
            <line x1="200" y1="280" x2="220" y2="255" stroke="currentColor" stroke-width="1.5" class="text-muted-foreground/30"/>
          </svg>
        </div>

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

        <!-- Stats -->
        <div class="mt-16 grid grid-cols-3 gap-6 max-w-lg mx-auto">
          <div v-for="s in t.stats" :key="s.label" class="text-center">
            <p :class="['text-3xl sm:text-4xl font-extrabold tracking-tight', s.color]">{{ s.value }}</p>
            <p class="text-xs text-muted-foreground mt-1">{{ s.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Stack Scrolling -->
    <div class="border-y border-border/50 py-8 overflow-hidden">
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
          class="group rounded-xl border border-border bg-card p-6 hover:border-primary/30 hover:shadow-md transition-colors duration-200"
        >
          <div class="h-10 w-10 rounded-lg bg-primary/10 text-primary grid place-items-center mb-4 group-hover:bg-primary group-hover:text-primary-foreground transition-colors duration-200">
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2"><path :d="f.icon"/></svg>
          </div>
          <h3 class="font-semibold text-sm">{{ f.title }}</h3>
          <p class="text-xs text-muted-foreground mt-2 leading-relaxed">{{ f.desc }}</p>
        </motion.div>
      </div>
    </section>

    <!-- FAQ -->
    <section id="faq" class="max-w-3xl mx-auto px-4 sm:px-6 py-20 sm:py-28">
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
      <div class="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-muted-foreground">
        <p>© {{ new Date().getFullYear() }} IAMS &middot; Infrastructure Asset Management System</p>
        <div class="flex items-center gap-4">
          <span>MariaDB + Flask + Vue 3</span>
          <span class="hidden sm:inline">·</span>
          <span class="hidden sm:inline">Docker Compose</span>
        </div>
      </div>
    </footer>
  </div>
</template>
