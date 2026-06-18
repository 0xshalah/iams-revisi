<script setup>
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] }, // [{label,value}]
  placeholder: { type: String, default: 'Pilih...' },
  disabled: { type: Boolean, default: false },
  class: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])
const onChange = (e) => emit('update:modelValue', e.target.value)

const cls = computed(() =>
  cn(
    'h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm pr-9 appearance-none',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background',
    'disabled:cursor-not-allowed disabled:opacity-50',
    props.class,
  ),
)
</script>
<template>
  <div class="relative">
    <select :value="modelValue" :disabled="disabled" :class="cls" @change="onChange">
      <option value="" disabled>{{ placeholder }}</option>
      <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
    </select>
    <svg class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m6 9 6 6 6-6" />
    </svg>
  </div>
</template>
