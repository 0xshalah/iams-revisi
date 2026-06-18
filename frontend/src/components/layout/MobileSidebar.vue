<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { menuForRole } from '@/lib/menuConfig'

const route = useRoute()
const auth = useAuthStore()
const ui = useUiStore()

const menu = computed(() => menuForRole(auth.role))

// Safety net: auto-close drawer on any route change (back/forward, programmatic, etc.)
watch(() => route.fullPath, () => {
  ui.closeMobileSidebar()
})
</script>

<template>
  <transition name="fade">
    <div v-if="ui.mobileSidebarOpen" class="md:hidden fixed inset-0 z-40">
      <div class="absolute inset-0 bg-black/50" @click="ui.closeMobileSidebar()" />
      <aside class="absolute left-0 top-0 bottom-0 w-72 bg-card border-r border-border p-3 animate-slide-down">
        <div class="h-12 flex items-center gap-2 px-1 mb-2">
          <div class="h-8 w-8 rounded-lg bg-primary text-primary-foreground grid place-items-center font-bold">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 9h18M3 15h18M7 9v6M17 9v6"/></svg>
          </div>
          <p class="text-sm font-bold tracking-tight">IAMS</p>
        </div>
        <nav class="space-y-1">
          <router-link
            v-for="item in menu"
            :key="item.name"
            :to="{ name: item.name }"
            custom
            v-slot="{ navigate, isActive }"
          >
            <button
              :data-testid="`mobile-nav-${item.name}`"
              :class="[
                'w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium',
                isActive ? 'bg-primary/10 text-primary' : 'text-foreground/80 hover:bg-secondary',
              ]"
              @click="navigate(); ui.closeMobileSidebar()"
            >
              {{ item.label }}
            </button>
          </router-link>
        </nav>
      </aside>
    </div>
  </transition>
</template>
