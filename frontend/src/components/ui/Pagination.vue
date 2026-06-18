<script setup>
import { computed } from 'vue'
import Button from './Button.vue'

const props = defineProps({
  page: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  total: { type: Number, required: true },
})
const emit = defineEmits(['update:page'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
const start = computed(() => props.total === 0 ? 0 : (props.page - 1) * props.pageSize + 1)
const end = computed(() => Math.min(props.total, props.page * props.pageSize))

function go(p) {
  const next = Math.min(Math.max(1, p), totalPages.value)
  if (next !== props.page) emit('update:page', next)
}
</script>

<template>
  <div class="flex items-center justify-between gap-3 text-sm flex-wrap" data-testid="pagination">
    <p class="text-muted-foreground">
      Menampilkan <span class="font-medium text-foreground">{{ start }}–{{ end }}</span> dari
      <span class="font-medium text-foreground">{{ total }}</span> data
    </p>
    <div class="flex items-center gap-1">
      <Button variant="outline" size="sm" :disabled="page === 1" data-testid="pagination-prev" @click="go(page - 1)">
        Sebelumnya
      </Button>
      <span class="px-3 text-muted-foreground">Hal. {{ page }} / {{ totalPages }}</span>
      <Button variant="outline" size="sm" :disabled="page >= totalPages" data-testid="pagination-next" @click="go(page + 1)">
        Berikutnya
      </Button>
    </div>
  </div>
</template>
