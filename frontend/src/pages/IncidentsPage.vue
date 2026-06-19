<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import apiClient from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Dialog from '@/components/ui/Dialog.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import TableSkeleton from '@/components/ui/TableSkeleton.vue'
import Pagination from '@/components/ui/Pagination.vue'
import IncidentFormDialog from '@/components/incidents/IncidentFormDialog.vue'
import { useUiStore } from '@/stores/ui'
import { formatDate, timeAgo } from '@/lib/utils'

const ui = useUiStore()
const auth = useAuthStore()
const { t } = useI18n()

const data = ref([])
const assets = ref([])
const users = ref([])
const loading = ref(true)
const error = ref(null)

const query = ref('')
const severityFilter = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = 8

const detailOpen = ref(false)
const detailItem = ref(null)
const confirmOpen = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)
const formOpen = ref(false)
const formIncident = ref(null)

const assetMap = computed(() => Object.fromEntries(assets.value.map((a) => [a.id, a])))
const userMap = computed(() => Object.fromEntries(users.value.map((u) => [u.id, u])))

async function load() {
  loading.value = true
  error.value = null
  try {
    const [incRes, assetRes, userRes] = await Promise.all([
      apiClient.listIncidents(),
      apiClient.listAssets(),
      apiClient.listUsers().catch(() => ({ data: [] })),
    ])
    data.value = incRes.data?.data || incRes.data || []
    assets.value = assetRes.data?.data || assetRes.data || []
    users.value = userRes.data?.data || userRes.data || []
  } catch (_) {
    error.value = t('incidents.loadFailed')
  } finally {
    loading.value = false
  }
}

onMounted(() => load())

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return data.value.filter((i) => {
    if (severityFilter.value && i.severity !== severityFilter.value) return false
    if (statusFilter.value && i.status !== statusFilter.value) return false
    if (!q) return true
    return (
      i.code.toLowerCase().includes(q) ||
      i.title.toLowerCase().includes(q) ||
      (assetMap.value[i.asset_id]?.asset_tag || '').toLowerCase().includes(q)
    )
  })
})

watch([query, severityFilter, statusFilter], () => { page.value = 1 })

const paged = computed(() => {
  const s = (page.value - 1) * pageSize
  return filtered.value.slice(s, s + pageSize)
})

function openDetail(item) { detailItem.value = item; detailOpen.value = true }
function openCreate() { formIncident.value = null; formOpen.value = true }
function openEdit(item) { formIncident.value = item; formOpen.value = true }
function askDelete(item) { pendingDelete.value = item; confirmOpen.value = true }

async function confirmDelete() {
  deleting.value = true
  try {
    await apiClient.deleteIncident(pendingDelete.value.id)
    data.value = data.value.filter((i) => i.id !== pendingDelete.value.id)
    ui.pushToast({ title: t('common.success'), description: `${pendingDelete.value.code} ${t('toast.deleted')}.`, variant: 'success' })
  } catch (err) {
    ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('pages.deleteFailed'), variant: 'destructive' })
  } finally {
    deleting.value = false
    confirmOpen.value = false
    pendingDelete.value = null
  }
}

function reset() { query.value = ''; severityFilter.value = ''; statusFilter.value = '' }

const severityOpts = ['Critical', 'High', 'Medium', 'Low'].map((v) => ({ label: v, value: v }))
const statusOpts = ['Open', 'In Progress', 'Resolved', 'Closed'].map((v) => ({ label: v, value: v }))
</script>

<template>
  <div class="space-y-5">
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Incident Management</p>
        <h2 class="text-2xl md:text-3xl font-bold tracking-tight mt-1">{{ t('pages.incidentsTitle') }}</h2>
        <p class="text-sm text-muted-foreground mt-1">Catat, tetapkan, dan pantau gangguan aset jaringan.</p>
      </div>
      <div class="flex items-center gap-2">
        <Button data-testid="incidents-add-btn" @click="openCreate">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
          Insiden Baru
        </Button>
      </div>
    </div>

    <Card class="p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="lg:col-span-2">
          <Label for="inc-search">Pencarian</Label>
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <Input id="inc-search" v-model="query" placeholder="Cari kode, judul, atau asset tag..." class="pl-9" data-testid="incidents-search-input" />
          </div>
        </div>
        <div>
          <Label>Severity</Label>
          <Select v-model="severityFilter" :options="severityOpts" placeholder="Semua severity" data-testid="incidents-filter-severity" />
        </div>
        <div>
          <Label>Status</Label>
          <Select v-model="statusFilter" :options="statusOpts" placeholder="Semua status" data-testid="incidents-filter-status" />
        </div>
      </div>
      <div v-if="query || severityFilter || statusFilter" class="mt-3 flex items-center gap-3 text-xs">
        <span class="text-muted-foreground">{{ filtered.length }} insiden sesuai filter</span>
        <button class="text-primary hover:underline" @click="reset" data-testid="incidents-reset-filters">Reset filter</button>
      </div>
    </Card>

    <Card class="overflow-hidden">
      <div v-if="loading" class="p-4"><TableSkeleton :rows="6" :columns="6" /></div>
      <ErrorState v-else-if="error" @retry="load()" />
      <EmptyState v-else-if="filtered.length === 0" title="Tidak ada insiden" description="Tidak ada insiden yang cocok dengan filter saat ini." icon="search" />
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm" data-testid="incidents-table">
          <thead class="bg-secondary/60 text-xs uppercase tracking-wider text-muted-foreground">
            <tr>
              <th class="text-left font-semibold px-4 py-3">Insiden</th>
              <th class="text-left font-semibold px-4 py-3">Aset Terkait</th>
              <th class="text-left font-semibold px-4 py-3">Severity</th>
              <th class="text-left font-semibold px-4 py-3">Status</th>
              <th class="text-left font-semibold px-4 py-3">Assignee</th>
              <th class="text-left font-semibold px-4 py-3">Dibuat</th>
              <th class="px-4 py-3 w-20"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-for="row in paged" :key="row.id" class="hover:bg-secondary/40 transition-colors" :data-testid="`incident-row-${row.code}`">
              <td class="px-4 py-3">
                <div class="font-medium">{{ row.title }}</div>
                <div class="text-xs text-muted-foreground font-mono">{{ row.code }}</div>
              </td>
              <td class="px-4 py-3">
                <span class="font-mono text-xs">{{ assetMap[row.asset_id]?.asset_tag || '—' }}</span>
                <div class="text-[11px] text-muted-foreground">{{ assetMap[row.asset_id]?.category_name }}</div>
              </td>
              <td class="px-4 py-3"><StatusBadge :value="row.severity" kind="severity" /></td>
              <td class="px-4 py-3"><StatusBadge :value="row.status" kind="incidentStatus" /></td>
              <td class="px-4 py-3 text-sm">{{ userMap[row.assignee_id]?.name || '—' }}</td>
              <td class="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{{ timeAgo(row.created_at) }}</td>
              <td class="px-4 py-3">
                <div class="flex justify-end gap-1">
                  <Button variant="ghost" size="icon" :data-testid="`incident-view-${row.code}`" @click="openDetail(row)" aria-label="Detail">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                  </Button>
                  <Button variant="ghost" size="icon" :data-testid="`incident-edit-${row.code}`" @click="openEdit(row)" aria-label="Edit">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                  </Button>
                  <Button v-if="auth.isAdmin" variant="ghost" size="icon" class="text-destructive hover:bg-destructive/10" :data-testid="`incident-delete-${row.code}`" @click="askDelete(row)" aria-label="Hapus">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!loading && !error && filtered.length" class="border-t border-border p-3">
        <Pagination :page="page" :page-size="pageSize" :total="filtered.length" @update:page="(p) => page = p" />
      </div>
    </Card>

    <Dialog v-model="detailOpen" :title="detailItem?.code" :description="detailItem?.title" size="lg">
      <div v-if="detailItem" class="space-y-4 text-sm" data-testid="incident-detail">
        <div class="flex flex-wrap gap-2">
          <StatusBadge :value="detailItem.severity" kind="severity" />
          <StatusBadge :value="detailItem.status" kind="incidentStatus" />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p class="text-muted-foreground text-xs uppercase tracking-wider">Aset terkait</p>
            <p class="font-mono">{{ assetMap[detailItem.asset_id]?.asset_tag || '—' }}</p>
            <p class="text-xs text-muted-foreground">{{ assetMap[detailItem.asset_id]?.location_name }}</p>
          </div>
          <div>
            <p class="text-muted-foreground text-xs uppercase tracking-wider">Assignee</p>
            <p>{{ userMap[detailItem.assignee_id]?.name || '—' }}</p>
          </div>
          <div>
            <p class="text-muted-foreground text-xs uppercase tracking-wider">Dibuat</p>
            <p>{{ formatDate(detailItem.created_at) }}</p>
          </div>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider mb-1">Deskripsi</p>
          <p class="leading-relaxed">{{ detailItem.description || '—' }}</p>
        </div>
      </div>
      <template #footer>
        <Button variant="ghost" @click="detailOpen = false" data-testid="incident-detail-close">Tutup</Button>
      </template>
    </Dialog>

    <IncidentFormDialog
      v-model="formOpen"
      :incident="formIncident"
      :assets="assets"
      :users="users"
      @saved="load"
    />

    <ConfirmDialog
      v-model="confirmOpen"
      title="Hapus insiden?"
      :description="`Insiden ${pendingDelete?.code} akan dihapus secara permanen.`"
      confirm-text="Hapus"
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>
