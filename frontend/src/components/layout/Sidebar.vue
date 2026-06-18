<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { menuForRole } from '@/lib/menuConfig'
import NavIcon from './NavIcon.vue'

const { t } = useI18n()
const auth = useAuthStore()
const ui = useUiStore()

const menu = computed(() => menuForRole(auth.role).map(m => ({ ...m, label: m.i18nKey ? t(m.i18nKey) : m.label })))
</script>

<template>
  <aside
    :class="[
      'hidden md:flex flex-col border-r border-border bg-card transition-all duration-300 z-20',
      ui.sidebarOpen ? 'w-64' : 'w-[72px]',
    ]"
    data-testid="sidebar"
  >
    <div class="h-14 flex items-center gap-2 px-3 border-b border-border">
      <div class="h-8 w-8 rounded-lg bg-primary text-primary-foreground grid place-items-center font-bold">
        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M3 9h18M3 15h18M7 9v6M17 9v6"/>
        </svg>
      </div>
      <div v-if="ui.sidebarOpen" class="leading-tight">
        <p class="text-sm font-bold tracking-tight">IAMS</p>
        <p class="text-[10px] uppercase tracking-widest text-muted-foreground">Asset Mgmt</p>
      </div>
    </div>

    <nav class="flex-1 p-2 space-y-0.5">
      <router-link
        v-for="item in menu"
        :key="item.name"
        :to="{ name: item.name }"
        custom
        v-slot="{ navigate, isActive }"
      >
        <button
          :data-testid="`nav-${item.name}`"
          :class="[
            'group w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
            isActive
              ? 'bg-primary/10 text-primary'
              : 'text-foreground/70 hover:bg-secondary hover:text-foreground',
          ]"
          @click="navigate"
        >
          <NavIcon :name="item.icon" />
          <span v-if="ui.sidebarOpen">{{ item.label }}</span>
        </button>
      </router-link>
    </nav>

    <div class="p-2 border-t border-border">
      <button
        class="w-full text-left flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-foreground/70 hover:bg-secondary hover:text-foreground"
        @click="ui.toggleSidebar()"
        data-testid="sidebar-toggle"
      >
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path :d="ui.sidebarOpen ? 'M15 18l-6-6 6-6' : 'M9 18l6-6-6-6'" />
        </svg>
        <span v-if="ui.sidebarOpen">Collapse</span>
      </button>
    </div>
  </aside>
</template>
