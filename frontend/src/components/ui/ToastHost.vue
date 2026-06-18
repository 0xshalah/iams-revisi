<script setup>
import { useUiStore } from '@/stores/ui'
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const ui = useUiStore()
const toasts = computed(() => ui.toasts)

const toneCls = {
  default: 'border-border bg-card text-foreground',
  success: 'border-primary/30 bg-primary/10 text-primary',
  destructive: 'border-destructive/30 bg-destructive/10 text-destructive',
  warning: 'border-warning/40 bg-warning/15 text-warning',
  info: 'border-info/30 bg-info/10 text-info',
}
</script>

<template>
  <Teleport to="body">
    <div
      class="pointer-events-none fixed bottom-4 right-4 left-4 sm:left-auto sm:right-4 z-[200] flex flex-col items-end gap-1.5"
      data-testid="toast-host"
    >
      <transition-group name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          :class="cn(
            'pointer-events-auto flex items-start gap-2 rounded-lg border px-3 py-2 shadow-md backdrop-blur-sm max-w-xs sm:max-w-sm',
            toneCls[t.variant] || toneCls.default
          )"
          :data-testid="`toast-${t.variant || 'default'}`"
        >
          <svg v-if="t.variant==='success'" class="h-4 w-4 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
          <svg v-else-if="t.variant==='destructive'" class="h-4 w-4 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg>
          <svg v-else-if="t.variant==='warning'" class="h-4 w-4 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><path d="M12 9v4M12 17h.01"/></svg>
          <svg v-else-if="t.variant==='info'" class="h-4 w-4 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
          <div class="min-w-0 flex-1">
            <p class="text-xs font-semibold leading-tight">{{ t.title }}</p>
            <p v-if="t.description" class="text-[11px] leading-tight opacity-80 mt-0.5">{{ t.description }}</p>
          </div>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active { transition: all 250ms ease-out; }
.toast-leave-active { transition: all 180ms ease-in; }
.toast-enter-from { opacity: 0; transform: translateY(12px) scale(0.96); }
.toast-leave-to { opacity: 0; transform: translateX(30px) scale(0.96); }
</style>
