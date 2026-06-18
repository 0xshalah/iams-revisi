<script setup>
import { ref, computed, onMounted } from 'vue'
import apiClient from '@/services/apiClient'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import TableSkeleton from '@/components/ui/TableSkeleton.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { useUiStore } from '@/stores/ui'
import { formatDateShort } from '@/lib/utils'

const ui = useUiStore()
const months = ref(3)
const loading = ref(true)
const error = ref(null)
const data = ref([])

const warrantyRows = computed(() => {
  const now = new Date()
  return data.value.map((row) => {
    const expiry = row.warranty_expiry ? new Date(row.warranty_expiry) : null
    const remainingDays = expiry ? Math.max(0, Math.ceil((expiry - now) / (1000 * 60 * 60 * 24))) : null
    return { ...row, remaining_days: remainingDays }
  }).sort((a, b) => (a.remaining_days || Infinity) - (b.remaining_days || Infinity))
})

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await apiClient.assetsWarrantyExpiring(months.value)
    data.value = res.data
  } catch (err) {
    error.value = 'Gagal memuat data garansi.'
  } finally {
    loading.value = false
  }
}

onMounted(() => load())

const exportLoading = ref(false)
async function exportCsv() {
  exportLoading.value = true
  try {
    const res = await apiClient.fullAssetReport()
    const rows = res.data || []
    const safeRows = rows.map((a) => ({
      asset_tag: a.asset_tag,
      serial_number: a.serial_number || '',
      po_number: a.po_number || '',
      category: a.category_name || '',
      brand: a.brand_name || '',
      model: a.model_name || '',
      location: a.location_name || '',
      department: a.department_name || '',
      user: a.user_name || '',
      ip_address: a.ip_address || '',
      mac_address: a.mac_address || '',
      status: a.status || '',
      purchase_date: a.purchase_date || '',
      warranty_months: a.warranty_months || '',
    }))
    const headers = Object.keys(safeRows[0] || {})
    const csv = [
      headers.join(','),
      ...safeRows.map((r) => headers.map((h) => `"${String(r[h] || '').replace(/"/g, '""')}"`).join(',')),
    ].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `iams-assets-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    ui.pushToast({ title: 'Export berhasil', description: `${safeRows.length} aset diekspor.`, variant: 'success' })
  } catch (err) {
    ui.pushToast({ title: 'Export gagal', description: err.data?.error || 'Tidak dapat mengekspor laporan.', variant: 'destructive' })
  } finally {
    exportLoading.value = false
  }
}
</script>

<template>
  <div class="space-y-5">
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Reports</p>
        <h2 class="text-2xl md:text-3xl font-bold tracking-tight mt-1">Laporan & Garansi</h2>
        <p class="text-sm text-muted-foreground mt-1">Pantau aset dengan garansi akan habis dan ekspor laporan aset.</p>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" :loading="exportLoading" data-testid="assets-export-csv-btn" @click="exportCsv">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10 12 15 17 10"/><path d="M12 15V3"/></svg>
          Export CSV Aset
        </Button>
      </div>
    </div>

    <Card class="p-4">
      <div class="flex flex-col sm:flex-row sm:items-end gap-4">
        <div>
          <Label for="warranty-months">Garansi habis dalam (bulan)</Label>
          <Input id="warranty-months" v-model="months" type="number" min="1" max="60" class="w-40" />
        </div>
        <Button data-testid="warranty-refresh-btn" @click="load">Tampilkan</Button>
      </div>
    </Card>

    <Card class="overflow-hidden">
      <div v-if="loading" class="p-4"><TableSkeleton :rows="5" :columns="7" /></div>
      <ErrorState v-else-if="error" @retry="load()" />
      <EmptyState v-else-if="warrantyRows.length === 0" title="Tidak ada aset" :description="`Tidak ada aset dengan garansi habis dalam ${months} bulan.`" icon="search" />
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm" data-testid="warranty-table">
          <thead class="bg-secondary/60 text-xs uppercase tracking-wider text-muted-foreground">
            <tr>
              <th class="text-left font-semibold px-4 py-3">Aset</th>
              <th class="text-left font-semibold px-4 py-3">Model</th>
              <th class="text-left font-semibold px-4 py-3">Kategori</th>
              <th class="text-left font-semibold px-4 py-3">Lokasi</th>
              <th class="text-left font-semibold px-4 py-3">Tanggal Beli</th>
              <th class="text-left font-semibold px-4 py-3">Garansi (bulan)</th>
              <th class="text-left font-semibold px-4 py-3">Habis Garansi</th>
              <th class="text-left font-semibold px-4 py-3">Sisa Hari</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-for="row in warrantyRows" :key="row.id" class="hover:bg-secondary/40" :data-testid="`warranty-row-${row.asset_tag}`">
              <td class="px-4 py-3 font-medium">{{ row.asset_tag }}</td>
              <td class="px-4 py-3">{{ row.brand_name }} {{ row.model_name }}</td>
              <td class="px-4 py-3">{{ row.category_name }}</td>
              <td class="px-4 py-3">{{ row.location_name }}</td>
              <td class="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{{ formatDateShort(row.purchase_date) }}</td>
              <td class="px-4 py-3">{{ row.warranty_months }}</td>
              <td class="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{{ formatDateShort(row.warranty_expiry) }}</td>
              <td class="px-4 py-3">
                <StatusBadge :value="row.remaining_days <= 30 ? 'Critical' : row.remaining_days <= 90 ? 'High' : 'Medium'" kind="severity" />
                <span class="text-xs text-muted-foreground ml-1">{{ row.remaining_days }} hari</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>
