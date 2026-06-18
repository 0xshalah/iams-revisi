<script setup>
import { useRouter } from 'vue-router'
import Button from '@/components/ui/Button.vue'

const router = useRouter()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-6 bg-background">
    <div class="text-center max-w-md">
      <p class="text-[10px] uppercase tracking-[0.3em] text-primary font-semibold">Error 404</p>
      <h1 class="text-5xl font-bold tracking-tight mt-3">Halaman tidak ditemukan</h1>
      <p class="text-sm text-muted-foreground mt-3">Halaman yang Anda cari tidak ada atau telah dipindahkan.</p>
      <Button class="mt-6" data-testid="back-to-dashboard-btn" @click="router.push({ name: 'dashboard' })">Kembali ke Dashboard</Button>
    </div>
  </div>
</template>
