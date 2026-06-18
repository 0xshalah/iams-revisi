<script setup>
import { computed } from 'vue'
import Badge from './Badge.vue'

const props = defineProps({
  value: { type: String, required: true },
  kind: { type: String, default: 'asset' }, // asset | incidentStatus | severity | priority | problemStatus | user
})

const map = computed(() => {
  const v = String(props.value || '').toLowerCase()
  if (props.kind === 'asset') {
    return ({
      active: 'success', available: 'info', repair: 'warning', disposed: 'muted',
    })[v] || 'secondary'
  }
  if (props.kind === 'incidentStatus') {
    return ({
      open: 'destructive', 'in progress': 'warning', resolved: 'success', closed: 'muted',
    })[v] || 'secondary'
  }
  if (props.kind === 'severity' || props.kind === 'priority') {
    return ({
      critical: 'destructive', high: 'warning', medium: 'info', low: 'muted',
    })[v] || 'secondary'
  }
  if (props.kind === 'problemStatus') {
    return ({
      open: 'destructive', investigating: 'warning', 'known error': 'info', closed: 'muted',
    })[v] || 'secondary'
  }
  if (props.kind === 'user') {
    return ({ active: 'success', inactive: 'muted' })[v] || 'secondary'
  }
  return 'secondary'
})

const dotCls = computed(() => {
  const v = map.value
  return ({
    success: 'bg-success',
    warning: 'bg-warning',
    destructive: 'bg-destructive',
    info: 'bg-info',
    muted: 'bg-muted-foreground',
    secondary: 'bg-foreground/40',
    default: 'bg-primary',
  })[v]
})
</script>

<template>
  <Badge :variant="map">
    <span :class="['h-1.5 w-1.5 rounded-full', dotCls]" />
    <span class="capitalize">{{ value }}</span>
  </Badge>
</template>
