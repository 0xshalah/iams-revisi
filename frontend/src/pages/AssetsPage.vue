<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import apiClient from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
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
import AssetFormDialog from '@/components/assets/AssetFormDialog.vue'
import AssetHistoryDialog from '@/components/assets/AssetHistoryDialog.vue'
import { useUiStore } from '@/stores/ui'
import { formatDateShort } from '@/lib/utils'

const ui = useUiStore()
const auth = useAuthStore()

const loading = ref(true)
const error = ref(null)
const data = ref([])
const query = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const locationFilter = ref('')
const page = ref(1)
const pageSize = 8

const editOpen = ref(false)
const detailItem = ref(null)
const confirmOpen = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)
const formOpen = ref(false)
const formAsset = ref(null)
const historyOpen = ref(false)
const historyAssetId = ref(null)

const locations = ref([])
const models = ref([])
const users = ref([])

async function load() {
  loading.value = true
  error.value = null
  try {
    const [assetsRes, locRes, modelRes, userRes] = await Promise.all([
      apiClient.listAssets(),
      apiClient.listLocations(),
      apiClient.listModels(),
      apiClient.listUsers().catch(() => ({ data: [] })),
    ])
    data.value = assetsRes.data?.data || assetsRes.data || []
    locations.value = locRes.data || []
    models.value = modelRes.data
    users.value = userRes.data
  } catch (_) {
    error.value = 'Gagal memuat data aset.'
  } finally {
    loading.value = false
  }
}

onMounted(() => load())

const categories = computed(() => {
  const map = {}
  for (const m of models.value) {
    if (m.category_name && !map[m.category_name]) {
      map[m.category_name] = { id: m.category_id, name: m.category_name }
    }
  }
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return data.value.filter((a) => {
    if (categoryFilter.value && a.category_name !== categoryFilter.value) return false
    if (statusFilter.value && a.status !== statusFilter.value) return false
    if (locationFilter.value && String(a.location_id) !== String(locationFilter.value)) return false
    if (!q) return true
    return (
      (a.asset_tag || '').toLowerCase().includes(q) ||
      (a.serial_number || '').toLowerCase().includes(q) ||
      (a.model_name || '').toLowerCase().includes(q) ||
      (a.brand_name || '').toLowerCase().includes(q) ||
      (a.ip_address || '').toLowerCase().includes(q) ||
      (a.po_number || '').toLowerCase().includes(q) ||
      (a.location_name || '').toLowerCase().includes(q)
    )
  })
})

watch([query, categoryFilter, statusFilter, locationFilter], () => { page.value = 1 })

const paged = computed(() => {
  const start = (page.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

function openDetail(item) {
  detailItem.value = item
  editOpen.value = true
}

function openHistory(item) {
  historyAssetId.value = item.id
  historyOpen.value = true
}

function openCreate() {
  formAsset.value = null
  formOpen.value = true
}

function openEdit(item) {
  formAsset.value = item
  formOpen.value = true
}

function askDelete(item) {
  pendingDelete.value = item
  confirmOpen.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await apiClient.deleteAsset(pendingDelete.value.id)
    data.value = data.value.filter((a) => a.id !== pendingDelete.value.id)
    ui.pushToast({ title: 'Aset dihapus', description: `${pendingDelete.value.asset_tag} berhasil dihapus.`, variant: 'success' })
  } catch (err) {
    ui.pushToast({ title: 'Gagal menghapus', description: err.data?.error || 'Tidak dapat menghapus aset.', variant: 'destructive' })
  } finally {
    deleting.value = false
    confirmOpen.value = false
    pendingDelete.value = null
  }
}

function resetFilters() {
  query.value = ''
  categoryFilter.value = ''
  statusFilter.value = ''
  locationFilter.value = ''
}

function maskMac(mac) {
  if (!mac) return '-'
  return mac.slice(0, 8) + ':**:**:**'
}

const categoryOpts = computed(() => categories.value.map((c) => ({ label: c.name, value: c.name })))
const statusOpts = ['Active', 'Available', 'Repair', 'Disposed'].map((s) => ({ label: s, value: s }))
const locationOpts = computed(() => locations.value.map((l) => ({ label: l.name, value: String(l.id) })))
</script>

<template>
  <div class="space-y-5">
    <!-- Header & actions -->
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Inventory</p>
        <h2 class="text-2xl md:text-3xl font-bold tracking-tight mt-1">Manajemen Aset</h2>
        <p class="text-sm text-muted-foreground mt-1">Router, Switch, Firewall, Access Point, dan Printer.</p>
      </div>
      <div class="flex items-center gap-2">
        <Button data-testid="assets-add-btn" @click="openCreate">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
          Tambah Aset
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <Card class="p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div class="lg:col-span-2">
          <Label for="search">Pencarian</Label>
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <Input id="search" v-model="query" placeholder="Cari tag, serial, IP, PO, model..." class="pl-9" data-testid="assets-search-input" />
          </div>
        </div>
        <div>
          <Label>Kategori</Label>
          <Select v-model="categoryFilter" :options="categoryOpts" placeholder="Semua kategori" data-testid="assets-filter-category" />
        </div>
        <div>
          <Label>Status</Label>
          <Select v-model="statusFilter" :options="statusOpts" placeholder="Semua status" data-testid="assets-filter-status" />
        </div>
        <div>
          <Label>Lokasi</Label>
          <Select v-model="locationFilter" :options="locationOpts" placeholder="Semua lokasi" data-testid="assets-filter-location" />
        </div>
      </div>
      <div v-if="query || categoryFilter || statusFilter || locationFilter" class="mt-3 flex items-center gap-3 text-xs">
        <span class="text-muted-foreground">{{ filtered.length }} hasil sesuai filter</span>
        <button class="text-primary hover:underline" data-testid="assets-reset-filters" @click="resetFilters">Reset filter</button>
      </div>
    </Card>

    <!-- Table -->
    <Card class="overflow-hidden">
      <div v-if="loading" class="p-4"><TableSkeleton :rows="6" :columns="7" /></div>
      <ErrorState v-else-if="error" @retry="load()" />
      <EmptyState v-else-if="filtered.length === 0" title="Aset tidak ditemukan" description="Coba ubah filter atau kata kunci pencarian." icon="search" />
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm" data-testid="assets-table">
          <thead class="bg-secondary/60 text-xs uppercase tracking-wider text-muted-foreground">
            <tr>
              <th class="text-left font-semibold px-4 py-3">Aset</th>
              <th class="text-left font-semibold px-4 py-3">Kategori</th>
              <th class="text-left font-semibold px-4 py-3">Lokasi</th>
              <th class="text-left font-semibold px-4 py-3">IP / MAC</th>
              <th class="text-left font-semibold px-4 py-3">Pengguna</th>
              <th class="text-left font-semibold px-4 py-3">Status</th>
              <th class="text-left font-semibold px-4 py-3">Diperbarui</th>
              <th class="px-4 py-3 w-20"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-for="row in paged" :key="row.id" class="hover:bg-secondary/40 transition-colors" :data-testid="`asset-row-${row.asset_tag}`">
              <td class="px-4 py-3">
                <div class="font-medium">{{ row.asset_tag }}</div>
                <div class="text-xs text-muted-foreground font-mono">{{ row.serial_number || '—' }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="font-medium">{{ row.category_name }}</div>
                <div class="text-xs text-muted-foreground">{{ row.brand_name }} · {{ row.model_name }}</div>
              </td>
              <td class="px-4 py-3 text-foreground/90">{{ row.location_name }}</td>
              <td class="px-4 py-3">
                <div class="font-mono text-xs">{{ row.ip_address || '—' }}</div>
                <div class="text-xs text-muted-foreground font-mono">{{ maskMac(row.mac_address) }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm">{{ row.user_name }}</div>
                <div class="text-xs text-muted-foreground">{{ row.department_name }}</div>
              </td>
              <td class="px-4 py-3"><StatusBadge :value="row.status" kind="asset" /></td>
              <td class="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{{ formatDateShort(row.updated_at) }}</td>
              <td class="px-4 py-3">
                <div class="flex justify-end gap-1">
                  <Button variant="ghost" size="icon" :data-testid="`asset-history-${row.asset_tag}`" aria-label="History" @click="openHistory(row)">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 3-6.74"/><path d="M3 4v5h5M12 7v5l3 2"/></svg>
                  </Button>
                  <Button variant="ghost" size="icon" :data-testid="`asset-edit-${row.asset_tag}`" aria-label="Edit" @click="openEdit(row)">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                  </Button>
                  <Button v-if="auth.isAdmin" variant="ghost" size="icon" class="text-destructive hover:bg-destructive/10" :data-testid="`asset-delete-${row.asset_tag}`" aria-label="Hapus" @click="askDelete(row)">
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

    <!-- Detail dialog (read only) -->
    <Dialog v-model="editOpen" :title="detailItem?.asset_tag" :description="`${detailItem?.brand_name} ${detailItem?.model_name}`" size="lg">
      <div v-if="detailItem" class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm" data-testid="asset-detail">
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">Serial Number</p>
          <p class="font-mono">{{ detailItem.serial_number || '—' }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">PO Number</p>
          <p class="font-mono">{{ detailItem.po_number || '—' }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">Status</p>
          <StatusBadge :value="detailItem.status" kind="asset" />
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">Lokasi</p>
          <p>{{ detailItem.location_name }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">IP Address</p>
          <p class="font-mono">{{ detailItem.ip_address || '—' }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">MAC Address</p>
          <p class="font-mono">{{ maskMac(detailItem.mac_address) }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">Hostname</p>
          <p class="font-mono">{{ detailItem.hostname || '—' }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">VLAN</p>
          <p class="font-mono">{{ detailItem.vlan || '—' }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">Pengguna</p>
          <p>{{ detailItem.user_name }} <span class="text-muted-foreground">· {{ detailItem.department_name }}</span></p>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider">Tanggal Pembelian</p>
          <p>{{ formatDateShort(detailItem.purchase_date) }}</p>
        </div>
        <div class="sm:col-span-2">
          <p class="text-muted-foreground text-xs uppercase tracking-wider">Garansi</p>
          <p>{{ detailItem.warranty_months }} bulan sejak pembelian</p>
        </div>
        <div class="sm:col-span-2">
          <p class="text-muted-foreground text-xs uppercase tracking-wider">Credential</p>
          <p>{{ detailItem.has_credential ? 'Tersimpan (terenkripsi)' : 'Belum ada' }}</p>
        </div>
      </div>
      <template #footer>
        <Button variant="ghost" data-testid="asset-detail-close" @click="editOpen = false">Tutup</Button>
        <Button variant="outline" data-testid="asset-detail-history" @click="openHistory(detailItem)">Riwayat</Button>
      </template>
    </Dialog>

    <AssetHistoryDialog
      v-model="historyOpen"
      :asset-id="historyAssetId"
    />

    <AssetFormDialog
      v-model="formOpen"
      :asset="formAsset"
      :locations="locations"
      :models="models"
      :users="users"
      @saved="load"
    />

    <ConfirmDialog
      v-model="confirmOpen"
      title="Hapus aset?"
      :description="`Aset ${pendingDelete?.asset_tag} akan dihapus secara permanen. Tindakan ini tidak dapat dibatalkan.`"
      confirm-text="Hapus aset"
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>
