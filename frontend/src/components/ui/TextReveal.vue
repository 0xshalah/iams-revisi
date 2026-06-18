<script setup>
defineProps({ text: { type: String, required: true } })
</script>
<template>
  <span class="inline-block animate-text-reveal bg-gradient-to-r from-primary via-violet-500 to-primary bg-clip-text text-transparent bg-[length:200%_auto]">{{ text }}</span>
</template>
<style scoped>
@keyframes text-reveal {
  0% { background-position: 200% center; opacity: 0; }
  40% { opacity: 1; }
  100% { background-position: 0% center; opacity: 1; }
}
.animate-text-reveal { animation: text-reveal 1.2s ease-out forwards; }
</style>
