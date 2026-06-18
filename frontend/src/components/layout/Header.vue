<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useThemeStore } from '@/stores/theme'
import { useLocaleStore } from '@/stores/locale'
import { useI18n } from 'vue-i18n'
import { labelForRoute } from '@/lib/menuConfig'
import Button from '@/components/ui/Button.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()
const theme = useThemeStore()
const locale = useLocaleStore()
const { t } = useI18n()

const profileOpen = ref(false)
const langOpen = ref(false)
const notifOpen = ref(false)
const notifications = ref([])
const hasUnread = ref(false)

function closeAllMenus(e) {
  if (!e.target.closest('[data-menu-root]')) {
    profileOpen.value = false
    langOpen.value = false
    notifOpen.value = false
  }
}

onMounted(() => { window.addEventListener('click', closeAllMenus); fetchNotifications() })
onBeforeUnmount(() => window.removeEventListener('click', closeAllMenus))

const currentLabel = computed(() => labelForRoute(route.name))
const initials = computed(() => auth.user?.avatar || (auth.user?.name || '').split(' ').map((s) => s[0]).slice(0, 2).join(''))

async function fetchNotifications() {
  try {
    const [incRes, auditRes] = await Promise.all([
      apiClient.listIncidents({ per_page: 3 }).catch(() => ({ data: { data: [] } })),
      apiClient.listAuditLogs({ per_page: 3 }).catch(() => ({ data: { data: [] } })),
    ])
    const incs = (incRes.data?.data || incRes.data || []).slice(0, 3).map(i => ({
      text: `${i.code} · ${i.severity}`,
      sub: i.title,
    }))
    const logs = (auditRes.data?.data || auditRes.data || []).slice(0, 2).map(l => ({
      text: `${l.action} ${l.resource_type}`,
      sub: l.status === 'success' ? 'Berhasil' : 'Gagal',
    }))
    notifications.value = [...incs, ...logs].slice(0, 5)
    hasUnread.value = notifications.value.length > 0
  } catch (_) { /* ignore */ }
}

function logout() {
  router.push({ name: 'login' })
  auth.logout()
}

function toggleLang() {
  langOpen.value = !langOpen.value
  themeOpen.value = false
  profileOpen.value = false
  notifOpen.value = false
}

function toggleNotif() {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value) { hasUnread.value = false }
  langOpen.value = false
  profileOpen.value = false
}

function toggleProfile() {
  profileOpen.value = !profileOpen.value
  langOpen.value = false
  notifOpen.value = false
}
</script>

<template>
  <header class="h-14 border-b border-border bg-card/80 backdrop-blur sticky top-0 z-30">
    <div class="h-full flex items-center justify-between px-3 sm:px-4 gap-3">
      <div class="flex items-center gap-2 min-w-0">
        <Button variant="ghost" size="icon" class="md:hidden" @click="ui.openMobileSidebar()" data-testid="mobile-menu-btn" aria-label="Open menu">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
        </Button>
        <div class="min-w-0">
          <h1 class="text-base sm:text-lg font-semibold tracking-tight truncate" data-testid="page-title">{{ currentLabel }}</h1>
          <p class="text-xs text-muted-foreground hidden sm:block">Infrastructure Asset Management</p>
        </div>
      </div>

      <div class="flex items-center gap-1 sm:gap-2">
        <!-- Theme — direct toggle, no dropdown -->
        <Button variant="ghost" size="icon" data-testid="theme-toggle-btn" aria-label="Theme" @click.stop="theme.setMode(theme.resolved==='dark'?'light':'dark', $event.clientX, $event.clientY)">
          <span class="relative h-5 w-5 block" style="overflow:hidden">
            <Transition name="theme-icon" mode="out-in">
              <svg v-if="theme.resolved==='dark'" key="moon" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
              <svg v-else key="sun" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
            </Transition>
          </span>
        </Button>

        <!-- Language -->
        <div class="relative" data-menu-root>
          <Button variant="ghost" size="icon" aria-label="Language" @click.stop="toggleLang">
            <span class="text-[11px] font-bold uppercase">{{ locale.current }}</span>
          </Button>
          <transition name="fade">
            <div v-if="langOpen" class="absolute right-0 mt-2 w-44 card-surface shadow-xl p-1 animate-slide-down">
              <button
                v-for="code in locale.available" :key="code"
                :class="['w-full text-left px-3 py-2 rounded-md text-sm flex items-center justify-between hover:bg-secondary', locale.current===code && 'bg-secondary']"
                @click="locale.setLocale(code); langOpen=false"
              >
                <span>{{ { id: 'Bahasa Indonesia', en: 'English' }[code] }}</span>
                <svg v-if="locale.current===code" class="h-4 w-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m5 12 5 5L20 7"/></svg>
              </button>
            </div>
          </transition>
        </div>

        <!-- Notifications -->
        <div class="relative" data-menu-root>
          <Button variant="ghost" size="icon" data-testid="notifications-btn" aria-label="Notifications" @click.stop="toggleNotif">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            <span v-if="notifications.length && hasUnread" class="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive"></span>
          </Button>
          <transition name="fade">
            <div v-if="notifOpen" class="absolute right-0 mt-2 w-80 card-surface shadow-xl p-2 animate-slide-down" data-testid="notifications-menu">
              <div class="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Notifikasi terbaru</div>
              <div class="divide-y divide-border">
                <div v-if="!notifications.length" class="p-3 text-xs text-muted-foreground">Belum ada notifikasi.</div>
                <div v-for="(n, i) in notifications" :key="i" class="p-3 hover:bg-secondary rounded-md">
                  <p class="text-sm font-medium">{{ n.text }}</p>
                  <p class="text-xs text-muted-foreground mt-0.5">{{ n.sub }}</p>
                </div>
              </div>
            </div>
          </transition>
        </div>

        <!-- Profile -->
        <div class="relative" data-menu-root>
          <button
            class="flex items-center gap-2 pl-1.5 pr-2 h-9 rounded-md hover:bg-secondary transition-colors"
            @click.stop="toggleProfile"
            data-testid="profile-menu-btn"
          >
            <div class="h-7 w-7 rounded-full bg-primary text-primary-foreground grid place-items-center text-xs font-bold">{{ initials }}</div>
            <div class="hidden md:block text-left leading-tight">
              <p class="text-xs font-semibold">{{ auth.user?.name }}</p>
              <p class="text-[10px] text-muted-foreground">{{ auth.role }}</p>
            </div>
            <svg class="h-4 w-4 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
          </button>
          <transition name="fade">
            <div v-if="profileOpen" class="absolute right-0 mt-2 w-64 card-surface shadow-xl p-1.5 animate-slide-down" data-testid="profile-menu">
              <div class="px-3 py-2.5 border-b border-border">
                <p class="text-sm font-semibold">{{ auth.user?.name }}</p>
                <p class="text-xs text-muted-foreground">{{ auth.user?.email }}</p>
              </div>
              <button
                class="w-full text-left px-3 py-2 rounded-md text-sm flex items-center gap-2 hover:bg-destructive/10 text-destructive"
                data-testid="logout-btn"
                @click="logout"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>
                {{ t('auth.logout') }}
              </button>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.theme-icon-enter-active,
.theme-icon-leave-active {
  transition: all 0.35s ease;
}
.theme-icon-enter-from {
  opacity: 0;
  transform: scale(0.4) rotate(180deg);
}
.theme-icon-leave-to {
  opacity: 0;
  transform: scale(0.4) rotate(-180deg);
}
</style>
