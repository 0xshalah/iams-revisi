<script setup>
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: { type: String, default: 'default' },
  // default | secondary | outline | success | warning | destructive | info | muted
})
const base = 'inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium tracking-wide'
const variants = {
  default: 'bg-primary/10 text-primary border-primary/20',
  secondary: 'bg-secondary text-secondary-foreground border-border',
  outline: 'border-border text-foreground bg-transparent',
  success: 'bg-success/10 text-success border-success/20',
  warning: 'bg-warning/15 text-warning border-warning/30',
  destructive: 'bg-destructive/10 text-destructive border-destructive/20',
  info: 'bg-info/10 text-info border-info/20',
  muted: 'bg-muted text-muted-foreground border-border',
}
const cls = computed(() => cn(base, variants[props.variant]))
</script>
<template><span :class="cls"><slot /></span></template>
