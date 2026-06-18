<script setup>
import { cn } from '@/lib/utils'

defineProps({
  title: { type: String, default: 'Tidak ada data' },
  description: { type: String, default: 'Coba ubah filter atau tambah data baru.' },
  icon: { type: String, default: 'inbox' }, // inbox | search | alert
})
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3 py-14 text-center" data-testid="empty-state">
    <div class="h-12 w-12 rounded-full bg-secondary text-muted-foreground flex items-center justify-center">
      <svg v-if="icon === 'inbox'" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 12h-6l-2 3h-4l-2-3H2" />
        <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
      </svg>
      <svg v-else-if="icon === 'search'" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" />
      </svg>
      <svg v-else class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 9v4M12 17h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
      </svg>
    </div>
    <div>
      <p class="text-sm font-medium">{{ title }}</p>
      <p class="text-xs text-muted-foreground mt-1 max-w-sm">{{ description }}</p>
    </div>
    <slot />
  </div>
</template>
