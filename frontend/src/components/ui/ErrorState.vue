<script setup>
import Button from './Button.vue'

defineProps({
  title: { type: String, default: 'Gagal memuat data' },
  description: { type: String, default: 'Terjadi kesalahan saat mengambil data dari server.' },
})
const emit = defineEmits(['retry'])
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3 py-14 text-center" data-testid="error-state">
    <div class="h-12 w-12 rounded-full bg-destructive/10 text-destructive flex items-center justify-center">
      <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" /><path d="M12 8v4M12 16h.01" />
      </svg>
    </div>
    <div>
      <p class="text-sm font-medium">{{ title }}</p>
      <p class="text-xs text-muted-foreground mt-1 max-w-sm">{{ description }}</p>
    </div>
    <Button variant="outline" size="sm" data-testid="error-state-retry-btn" @click="emit('retry')">Coba lagi</Button>
  </div>
</template>
