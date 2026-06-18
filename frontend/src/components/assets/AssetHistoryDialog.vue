<script setup>
import { ref, computed, watch } from 'vue'
import apiClient from '@/services/apiClient'
import Dialog from '@/components/ui/Dialog.vue'
import Badge from '@/components/ui/Badge.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import TableSkeleton from '@/components/ui/TableSkeleton.vue'
import { formatDate } from '@/lib/utils'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  assetId: { type: [Number, String], default: null },
})

const data = ref([])
const loading = ref(false)

async function load() {
  if (!props.assetId) return
  loading.value = true
  try {
    const res = await apiClient.listAuditLogs()
    data.value = (res.data || []).filter(
      (l) => String(l.resource_type).toLowerCase() === 'asset' && String(l.resource_id) === String(props.assetId),
    )
  } catch (_) {
    data.value = []
  } finally {
    loading.value = false
  }
}

watch(() => [props.modelValue, props.assetId], () => {
  if (props.modelValue) load()
})

const actionVariant = (a) => ({ CREATE: 'success', UPDATE: 'info', DELETE: 'destructive', LOGIN: 'secondary', ACCESS: 'muted' }[a] || 'secondary')
</script>

<template>
  <Dialog
    :model-value="modelValue"
    title="Riwayat Perubahan Aset"
    :description="`Audit log untuk aset ID ${assetId}`"
    size="lg"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="loading" class="p-2"><TableSkeleton :rows="4" :columns="4" /></div>
    <EmptyState v-else-if="data.length === 0" title="Tidak ada riwayat" description="Belum ada aktivitas tercatat untuk aset ini." icon="history" />
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-secondary/60 text-xs uppercase tracking-wider text-muted-foreground">
          <tr>
            <th class="text-left font-semibold px-3 py-2">Waktu</th>
            <th class="text-left font-semibold px-3 py-2">Actor</th>
            <th class="text-left font-semibold px-3 py-2">Action</th>
            <th class="text-left font-semibold px-3 py-2">Detail</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          <tr v-for="l in data" :key="l.id" class="hover:bg-secondary/40">
            <td class="px-3 py-2 text-xs text-muted-foreground whitespace-nowrap">{{ formatDate(l.timestamp) }}</td>
            <td class="px-3 py-2 text-xs font-mono">{{ l.actor }}</td>
            <td class="px-3 py-2"><Badge :variant="actionVariant(l.action)">{{ l.action }}</Badge></td>
            <td class="px-3 py-2 text-foreground/80 text-xs">{{ l.detail || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <template #footer>
      <button class="text-sm text-primary hover:underline" @click="load">Refresh</button>
    </template>
  </Dialog>
</template>
