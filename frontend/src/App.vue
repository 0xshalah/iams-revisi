<script setup>
import { RouterView } from 'vue-router'
import ToastHost from '@/components/ui/ToastHost.vue'
</script>

<template>
  <RouterView v-slot="{ Component, route }">
    <transition name="fade" mode="out-in">
      <component :is="Component" :key="route.fullPath" />
    </transition>
  </RouterView>
  <ToastHost />
</template>

<style>
.fade-enter-active {
  transition: all 0.25s cubic-bezier(0.25, 0.1, 0.25, 1);
}
.fade-leave-active {
  transition: all 0.15s ease-in;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(6px) scale(0.995);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.995);
}
</style>
