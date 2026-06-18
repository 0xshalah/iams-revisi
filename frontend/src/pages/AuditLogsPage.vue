<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import apiClient from '@/services/apiClient'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import TableSkeleton from '@/components/ui/TableSkeleton.vue'
import Pagination from '@/components/ui/Pagination.vue'
import Button from '@/components/ui/Button.vue'
import { formatDate } from '@/lib/utils'

const data = ref([])
const loading = ref(true)
const error = ref(null)
const query = ref('')
const actionFilter = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = 10

async function load(simulateError = false) {
  loading.value = true
  error.value = null
  try {
    if (simulateError) throw new Error('simulated')
    const res = await apiClient.listAuditLogs()
    data.value = res.data?.data || res.data || []
  } catch (_) {
    error.value = 'Gagal memuat audit logs.'
  } finally {
    loading.value = false
  }
}
onMounted(() => load())

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return data.value.filter((l) => {
    if (actionFilter.value && l.action !== actionFilter.value) return false
    if (statusFilter.value && l.status !== statusFilter.value) return false
    if (!q) return true
    return l.actor.toLowerCase().includes(q) || l.resource_id.toLowerCase().includes(q) || l.resource_type.toLowerCase().includes(q)
  })
})

watch([query, actionFilter, statusFilter], () => { page.value = 1 })

const paged = computed(() => {
  const s = (page.value - 1) * pageSize
  return filtered.value.slice(s, s + pageSize)
})

const actionVariant = (a) => ({ CREATE: 'success', UPDATE: 'info', DELETE: 'destructive', LOGIN: 'secondary', JOB: 'muted', EXPORT: 'default' }[a] || 'secondary')

const actionOpts = ['CREATE','UPDATE','DELETE','LOGIN','JOB','EXPORT'].map((v) => ({ label: v, value: v }))
const statusOpts = [{ label: 'success', value: 'success' }, { label: 'failure', value: 'failure' }]

function reset() { query.value=''; actionFilter.value=''; statusFilter.value='' }
</script>

<template>
  <div class="space-y-5">
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Compliance</p>
        <h2 class="text-2xl md:text-3xl font-bold tracking-tight mt-1">Audit Logs</h2>
        <p class="text-sm text-muted-foreground mt-1">Riwayat aktivitas sistem (Administrator only). Data sensitif telah dimasking.</p>
      </div>
      <Badge variant="info">Admin only</Badge>
    </div>

    <Card class="p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="lg:col-span-2">
          <Label for="al-search">Pencarian</Label>
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <Input id="al-search" v-model="query" placeholder="Cari aktor, resource type, atau ID..." class="pl-9" data-testid="audit-search-input" />
          </div>
        </div>
        <div>
          <Label>Action</Label>
          <Select v-model="actionFilter" :options="actionOpts" placeholder="Semua action" data-testid="audit-filter-action" />
        </div>
        <div>
          <Label>Status</Label>
          <Select v-model="statusFilter" :options="statusOpts" placeholder="Semua status" data-testid="audit-filter-status" />
        </div>
      </div>
      <div v-if="query || actionFilter || statusFilter" class="mt-3 flex items-center gap-3 text-xs">
        <span class="text-muted-foreground">{{ filtered.length }} log sesuai filter</span>
        <button class="text-primary hover:underline" @click="reset" data-testid="audit-reset-filters">Reset filter</button>
      </div>
    </Card>

    <Card class="overflow-hidden">
      <div v-if="loading" class="p-4"><TableSkeleton :rows="6" :columns="6" /></div>
      <ErrorState v-else-if="error" @retry="load()" />
      <EmptyState v-else-if="filtered.length === 0" title="Tidak ada log" icon="search" />
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm" data-testid="audit-table">
          <thead class="bg-secondary/60 text-xs uppercase tracking-wider text-muted-foreground">
            <tr>
              <th class="text-left font-semibold px-4 py-3">Waktu</th>
              <th class="text-left font-semibold px-4 py-3">Actor</th>
              <th class="text-left font-semibold px-4 py-3">Action</th>
              <th class="text-left font-semibold px-4 py-3">Resource</th>
              <th class="text-left font-semibold px-4 py-3">Status</th>
              <th class="text-left font-semibold px-4 py-3">Detail</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-for="l in paged" :key="l.id" class="hover:bg-secondary/40" :data-testid="`audit-row-${l.id}`">
              <td class="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{{ formatDate(l.timestamp) }}</td>
              <td class="px-4 py-3 font-mono text-xs">{{ l.actor }}</td>
              <td class="px-4 py-3"><Badge :variant="actionVariant(l.action)">{{ l.action }}</Badge></td>
              <td class="px-4 py-3">
                <div class="text-xs uppercase text-muted-foreground">{{ l.resource_type }}</div>
                <div class="font-mono text-xs">{{ l.resource_id }}</div>
              </td>
              <td class="px-4 py-3">
                <Badge :variant="l.status === 'success' ? 'success' : 'destructive'">{{ l.status }}</Badge>
              </td>
              <td class="px-4 py-3 text-foreground/80">{{ l.detail }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!loading && !error && filtered.length" class="border-t border-border p-3">
        <Pagination :page="page" :page-size="pageSize" :total="filtered.length" @update:page="(p) => page = p" />
      </div>
    </Card>
  </div>
</template>
