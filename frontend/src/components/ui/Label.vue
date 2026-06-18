<script setup>
const props = defineProps({
  for: { type: String, default: undefined },
  class: { type: String, default: '' },
})
</script>
<template>
  <label :for="props.for" :class="['block text-sm font-medium text-foreground/80 mb-1.5', props.class]">
    <slot />
  </label>
</template>
