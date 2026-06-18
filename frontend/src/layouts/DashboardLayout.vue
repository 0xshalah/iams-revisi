<script setup>
import { RouterView } from 'vue-router'
import Sidebar from '@/components/layout/Sidebar.vue'
import MobileSidebar from '@/components/layout/MobileSidebar.vue'
import Header from '@/components/layout/Header.vue'
</script>

<template>
  <div class="min-h-screen bg-background text-foreground flex">
    <Sidebar />
    <MobileSidebar />

    <div class="flex-1 flex flex-col min-w-0">
      <Header />

      <main class="flex-1 p-3 sm:p-4 lg:p-5 max-w-[1600px] mx-auto w-full">
        <RouterView v-slot="{ Component, route: r }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="r.fullPath" />
          </transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>
