<script setup>
defineProps({ items: { type: Array, required: true }, speed: { type: String, default: '20s' } })
</script>
<template>
  <div class="overflow-hidden">
    <div class="flex gap-8 animate-marquee whitespace-nowrap" :style="{ animationDuration: speed }">
      <span v-for="item in items" :key="item" class="text-sm font-semibold text-muted-foreground/60">{{ item }}</span>
      <span v-for="item in items" :key="item + '_2'" class="text-sm font-semibold text-muted-foreground/60">{{ item }}</span>
    </div>
  </div>
</template>
<style scoped>
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.animate-marquee { animation: marquee linear infinite; }
</style>
