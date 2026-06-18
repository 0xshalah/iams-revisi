<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useThemeStore } from '@/stores/theme'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const ui = useUiStore()
const theme = useThemeStore()

const email = ref('')
const password = ref('')
const showPwd = ref(false)
const remember = ref(true)

onMounted(() => {
  email.value = auth.getRememberedEmail() || ''
})

async function onSubmit() {
  const res = await auth.login({ email: email.value, password: password.value, remember: remember.value })
  if (res.ok) {
    ui.pushToast({ title: t('auth.loginSuccess'), description: `${t('auth.loggedInAs')} ${auth.role}`, variant: 'success' })
    const next = route.query.next || { name: 'dashboard' }
    router.push(next)
  } else {
    ui.pushToast({ title: t('common.failed'), description: res.error, variant: 'destructive' })
  }
}

function applyDemo(role) {
  if (role === 'admin') {
    email.value = 'admin@iams.local'
    password.value = 'admin123'
  } else {
    email.value = 'operator@iams.local'
    password.value = 'operator123'
  }
}

function toggleTheme() {
  theme.setMode(theme.resolved === 'dark' ? 'light' : 'dark')
}

const year = computed(() => new Date().getFullYear())
</script>

<template>
  <div class="min-h-screen flex bg-background">
    <!-- Left brand panel -->
    <aside class="hidden lg:flex relative w-1/2 xl:w-[55%] bg-slate-950 text-white overflow-hidden">
      <div class="absolute inset-0 grid-bg opacity-40"></div>
      <div class="absolute -top-32 -right-32 h-96 w-96 rounded-full bg-indigo-500/20 blur-3xl"></div>
      <div class="absolute -bottom-40 -left-20 h-96 w-96 rounded-full bg-violet-500/10 blur-3xl"></div>

      <div class="relative z-10 flex flex-col p-12 w-full">
        <div class="flex items-center gap-3">
          <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-indigo-400 to-violet-500 grid place-items-center font-bold">
              <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="white" stroke-width="2.5"><path d="M3 9h18M3 15h18M7 9v6M17 9v6"/></svg>
            </div>
            <div>
              <p class="font-bold tracking-tight">IAMS</p>
              <p class="text-[11px] uppercase tracking-widest text-indigo-300/80">Infrastructure Asset Management</p>
            </div>
          </router-link>
        </div>

        <div class="mt-auto max-w-md">
          <p class="text-[11px] uppercase tracking-[0.25em] text-indigo-300/80 mb-3">Internal IT Operations</p>
          <h2 class="text-4xl xl:text-5xl font-bold leading-[1.05] tracking-tight">
            Kelola aset jaringan,<br>
            <span class="text-indigo-300">tindak gangguan,</span><br>
            telusuri akar masalah.
          </h2>
          <p class="mt-5 text-sm text-slate-300/90 leading-relaxed">
            Dashboard internal untuk tim IT, terpusat, terdokumentasi, dan auditable.
          </p>

          <div class="mt-10 grid grid-cols-3 gap-3 max-w-sm">
            <div class="rounded-lg bg-white/5 border border-white/10 p-3">
              <p class="text-2xl font-bold text-indigo-300">24</p>
              <p class="text-[10px] uppercase tracking-wider text-slate-400 mt-1">Aset Aktif</p>
            </div>
            <div class="rounded-lg bg-white/5 border border-white/10 p-3">
              <p class="text-2xl font-bold text-amber-300">7</p>
              <p class="text-[10px] uppercase tracking-wider text-slate-400 mt-1">Insiden</p>
            </div>
            <div class="rounded-lg bg-white/5 border border-white/10 p-3">
              <p class="text-2xl font-bold text-rose-300">3</p>
              <p class="text-[10px] uppercase tracking-wider text-slate-400 mt-1">Problem</p>
            </div>
          </div>
        </div>

        <p class="mt-12 text-[11px] text-slate-500">© {{ year }} IAMS · Prototype build</p>
      </div>
    </aside>

    <!-- Right form panel -->
    <section class="flex-1 flex items-center justify-center p-6 sm:p-10 relative">
      <button
        class="absolute top-5 right-5 h-9 w-9 inline-flex items-center justify-center rounded-md hover:bg-secondary text-muted-foreground"
        data-testid="login-theme-toggle"
        aria-label="Theme"
        @click="toggleTheme"
      >
        <svg v-if="theme.resolved==='dark'" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
      </button>

      <div class="w-full max-w-sm" data-testid="login-card">
        <div class="lg:hidden flex items-center gap-2 mb-8">
          <div class="h-9 w-9 rounded-lg bg-primary text-primary-foreground grid place-items-center font-bold">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 9h18M3 15h18M7 9v6M17 9v6"/></svg>
          </div>
          <p class="font-bold tracking-tight">IAMS</p>
        </div>

        <h1 class="text-2xl font-bold tracking-tight">{{ t('auth.login') }}</h1>
        <p class="text-sm text-muted-foreground mt-1.5">{{ t('auth.loginSubtitle') }}</p>

        <form class="mt-7 space-y-4" @submit.prevent="onSubmit">
          <div>
            <Label for="email">{{ t('auth.email') }}</Label>
            <Input id="email" v-model="email" type="email" placeholder="nama@perusahaan.id" autocomplete="email" data-testid="login-email-input" />
          </div>
          <div>
            <div class="flex items-center justify-between">
              <Label for="password">{{ t('auth.password') }}</Label>
              <button type="button" class="text-xs text-primary hover:underline" data-testid="forgot-password-link">Lupa password?</button>
            </div>
            <div class="relative">
              <Input id="password" v-model="password" :type="showPwd ? 'text' : 'password'" placeholder="••••••••" autocomplete="current-password" data-testid="login-password-input" />
              <button
                type="button"
                class="absolute inset-y-0 right-0 px-3 grid place-items-center text-muted-foreground"
                @click="showPwd = !showPwd"
                data-testid="toggle-password-visibility"
                aria-label="Toggle password visibility"
              >
                <svg v-if="showPwd" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61M2 2l20 20"/></svg>
                <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
          </div>

          <label class="flex items-center gap-2 text-sm">
            <input type="checkbox" v-model="remember" class="h-4 w-4 rounded border-border" data-testid="remember-checkbox" />
            <span class="text-muted-foreground">Ingat email saya</span>
          </label>

          <Button type="submit" :loading="auth.loading" class="w-full" size="lg" data-testid="login-submit-btn">
            {{ t('auth.loginButton') }}
          </Button>

          <p v-if="auth.error" class="text-xs text-destructive text-center" data-testid="login-error">{{ auth.error }}</p>
        </form>

        <div class="mt-7 rounded-lg border border-dashed border-border p-3 bg-secondary/40">
          <p class="text-[10px] uppercase tracking-widest text-muted-foreground font-semibold mb-2">Akun Demo</p>
          <div class="flex gap-2">
            <button class="flex-1 text-left rounded-md bg-card hover:border-primary border border-border px-3 py-2 transition-colors" data-testid="demo-admin-btn" @click="applyDemo('admin')">
              <p class="text-xs font-semibold">Administrator</p>
              <p class="text-[10px] text-muted-foreground mt-0.5">admin@iams.local</p>
            </button>
            <button class="flex-1 text-left rounded-md bg-card hover:border-primary border border-border px-3 py-2 transition-colors" data-testid="demo-operator-btn" @click="applyDemo('operator')">
              <p class="text-xs font-semibold">Operator</p>
              <p class="text-[10px] text-muted-foreground mt-0.5">operator@iams.local</p>
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
