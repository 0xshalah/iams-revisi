<script setup>
defineProps({
  rows: { type: Number, default: 5 },
  columns: { type: Number, default: 6 },
})
</script>

<template>
  <div class="space-y-2 py-3" data-testid="table-skeleton">
    <div v-for="r in rows" :key="r" class="flex gap-3 px-4">
      <div
        v-for="c in columns"
        :key="c"
        class="h-4 flex-1 rounded bg-muted animate-pulse"
        :style="{ animationDelay: `${(r + c) * 40}ms` }"
      />
    </div>
  </div>
</template>
