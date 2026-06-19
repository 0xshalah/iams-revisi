<script setup>
import { computed } from 'vue'

const props = defineProps({ value: { type: String, required: true }, size: { type: Number, default: 120 } })

const bars = computed(() => {
  const v = props.value
  const out = []
  // Simple Code-128-like barcode simulation
  for (let i = 0; i < v.length; i++) {
    const code = v.charCodeAt(i)
    for (let bit = 6; bit >= 0; bit--) {
      out.push({ black: (code >> bit) & 1, key: `${i}-${bit}` })
    }
  }
  return out
})
</script>
<template>
  <svg :width="size" :height="size * 0.6" viewBox="0 0 200 120" class="inline-block">
    <rect v-for="(b, i) in bars.slice(0, 105)" :key="b.key"
      :x="10 + i * 1.6" y="10" width="1.3" height="80"
      :fill="b.black ? 'currentColor' : 'transparent'" />
    <text :x="100" y="108" text-anchor="middle" class="text-[8px] font-mono fill-current">{{ value }}</text>
  </svg>
</template>
