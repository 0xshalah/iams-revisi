<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import apiClient from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
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

const ui = useUiStore()
const auth = useAuthStore()

const loading = ref(true)
const error = ref(null)
const data = ref([])
const search = ref('')
const statusFilter = ref('')
const priorityFilter = ref('')
const typeFilter = ref('')
const page = ref(1)
const pageSize = 8

const formOpen = ref(false)
const formItem = ref(null)
const formLoading = ref(false)
const isEdit = computed(() => !!formItem.value)

const confirmOpen = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)

const assets = ref([])
const departments = ref([])
const users = ref([])
const isAdmin = computed(() => auth.isAdmin)

const statusOpts = ['Open','In Progress','Waiting Approval','Approved','Rejected','Fulfilled','Closed','Cancelled'].map(s => ({ label: s, value: s }))
const priorityOpts = ['Low','Medium','High','Critical'].map(s => ({ label: s, value: s }))
const typeOpts = ['Asset Request','Repair Request','Replacement Request','Relocation Request','Access Request','Network Request','Other'].map(s => ({ label: s, value: s }))

const assetOpts = computed(() => assets.value.map(a => ({ label: a.asset_tag, value: String(a.id) })))
const deptOpts = computed(() => departments.value.map(d => ({ label: d.name, value: String(d.id) })))
const userOpts = computed(() => users.value.map(u => ({ label: u.name, value: String(u.id) })))

async function load() {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    if (priorityFilter.value) params.priority = priorityFilter.value
    if (typeFilter.value) params.request_type = typeFilter.value
    if (search.value) params.search = search.value
    const [reqRes, assetRes, deptRes, userRes] = await Promise.all([
      apiClient.listRequests(params),
      apiClient.listAssets().catch(() => ({ data: { data: [] } })),
      apiClient.listDepartments().catch(() => ({ data: { data: [] } })),
      isAdmin.value ? apiClient.listUsers().catch(() => ({ data: { data: [] } })) : Promise.resolve({ data: { data: [] } }),
    ])
    data.value = reqRes.data?.data || reqRes.data || []
    assets.value = assetRes.data?.data || assetRes.data || []
    departments.value = deptRes.data?.data || deptRes.data || []
    users.value = userRes.data?.data || userRes.data || []
  } catch (_) {
    error.value = 'Gagal memuat data permintaan.'
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
watch([search, statusFilter, priorityFilter, typeFilter], () => { page.value = 1; load() })

const filtered = computed(() => data.value)

const paged = computed(() => {
  const start = (page.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

const form = ref({
  title: '', description: '', request_type: '', priority: 'Medium',
  status: 'Open', asset_id: '', department_id: '', assigned_to_id: '',
  due_date: '', resolution_notes: '',
})

function openCreate() {
  formItem.value = null
  form.value = { title: '', description: '', request_type: '', priority: 'Medium', status: 'Open', asset_id: '', department_id: '', assigned_to_id: '', due_date: '', resolution_notes: '' }
  formOpen.value = true
}

function openEdit(item) {
  formItem.value = item
  form.value = {
    title: item.title || '',
    description: item.description || '',
    request_type: item.request_type || '',
    priority: item.priority || 'Medium',
    status: item.status || 'Open',
    asset_id: item.asset_id ? String(item.asset_id) : '',
    department_id: item.department_id ? String(item.department_id) : '',
    assigned_to_id: item.assigned_to_id ? String(item.assigned_to_id) : '',
    due_date: item.due_date || '',
    resolution_notes: item.resolution_notes || '',
  }
  formOpen.value = true
}

async function submitForm() {
  formLoading.value = true
  try {
    const payload = {
      title: form.value.title.trim(),
      description: form.value.description.trim() || undefined,
      request_type: form.value.request_type,
      priority: form.value.priority,
      status: form.value.status,
      asset_id: form.value.asset_id || undefined,
      department_id: form.value.department_id || undefined,
      assigned_to_id: form.value.assigned_to_id || undefined,
      due_date: form.value.due_date || undefined,
      resolution_notes: form.value.resolution_notes.trim() || undefined,
    }
    if (isEdit.value) {
      await apiClient.updateRequest(formItem.value.id, payload)
      ui.pushToast({ title: 'Berhasil', description: 'Permintaan diperbarui.', variant: 'success' })
    } else {
      await apiClient.createRequest(payload)
      ui.pushToast({ title: 'Berhasil', description: 'Permintaan dibuat.', variant: 'success' })
    }
    formOpen.value = false
    load()
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Terjadi kesalahan.', variant: 'destructive' })
  } finally {
    formLoading.value = false
  }
}

function confirmDelete(item) {
  pendingDelete.value = item
  confirmOpen.value = true
}

async function executeDelete() {
  if (!pendingDelete.value) return
  deleting.value = true
  try {
    await apiClient.deleteRequest(pendingDelete.value.id)
    ui.pushToast({ title: 'Berhasil', description: 'Permintaan dihapus.', variant: 'success' })
    confirmOpen.value = false; pendingDelete.value = null
    load()
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Gagal menghapus.', variant: 'destructive' })
  } finally { deleting.value = false }
}

const priorityVariant = (p) => ({ Low: 'info', Medium: 'warning', High: 'orange', Critical: 'destructive' }[p] || 'secondary')
const typeLabel = (t) => ({ 'Asset Request': 'Aset', 'Repair Request': 'Perbaikan', 'Replacement Request': 'Penggantian', 'Relocation Request': 'Pemindahan', 'Access Request': 'Akses', 'Network Request': 'Jaringan', Other: 'Lainnya' }[t] || t)
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h1 class="text-lg font-bold tracking-tight">Requests</h1>
        <p class="text-xs text-muted-foreground mt-0.5">Kelola permintaan operasional IT.</p>
      </div>
      <Button size="sm" @click="openCreate">+ Buat Request</Button>
    </div>

    <Card class="p-4">
      <div class="flex flex-wrap items-center gap-2 mb-3">
        <div class="relative w-full max-w-[200px]">
          <Input v-model="search" placeholder="Cari..." class="h-8 text-[13px] pl-7 pr-3" />
          <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </div>
        <Select v-model="statusFilter" :options="[{label:'All Status',value:''},...statusOpts]" class="h-8 text-[13px] w-[150px]" />
        <Select v-model="priorityFilter" :options="[{label:'All Priority',value:''},...priorityOpts]" class="h-8 text-[13px] w-[140px]" />
        <Select v-model="typeFilter" :options="[{label:'All Types',value:''},...typeOpts]" class="h-8 text-[13px] w-[160px]" />
      </div>

      <TableSkeleton v-if="loading" :cols="6" :rows="4" />
      <ErrorState v-else-if="error" :message="error" @retry="load" />
      <EmptyState v-else-if="!filtered.length" title="Belum ada request" description="Belum ada permintaan yang dibuat." @action="openCreate" />

      <template v-else>
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b text-left">
                <th class="py-2 px-2 font-medium text-muted-foreground">Number</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">Title</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">Type</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">Priority</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">Status</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">Requester</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">Due</th>
                <th class="py-2 px-2 font-medium text-muted-foreground w-24">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paged" :key="item.id" class="border-b hover:bg-muted/50 transition-colors">
                <td class="py-1.5 px-2 font-mono text-[11px]">{{ item.request_number }}</td>
                <td class="py-1.5 px-2 max-w-[200px] truncate" :title="item.title">{{ item.title }}</td>
                <td class="py-1.5 px-2"><span class="inline-block px-1.5 py-0.5 rounded text-[10px] bg-muted">{{ typeLabel(item.request_type) }}</span></td>
                <td class="py-1.5 px-2"><StatusBadge :variant="priorityVariant(item.priority)">{{ item.priority }}</StatusBadge></td>
                <td class="py-1.5 px-2"><StatusBadge :status="item.status">{{ item.status }}</StatusBadge></td>
                <td class="py-1.5 px-2">{{ item.requester_name || '-' }}</td>
                <td class="py-1.5 px-2">{{ item.due_date || '-' }}</td>
                <td class="py-1.5 px-2">
                  <div class="flex items-center gap-1">
                    <Button variant="ghost" size="xs" @click="openEdit(item)">Edit</Button>
                    <Button v-if="isAdmin" variant="ghost" size="xs" class="text-destructive" @click="confirmDelete(item)">Hapus</Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pagination v-if="filtered.length > pageSize" :model-value="page" :total="filtered.length" :per-page="pageSize" class="mt-3" @update:model-value="page = $event" />
      </template>
    </Card>

    <!-- Create/Edit Dialog -->
    <Dialog :model-value="formOpen" :title="isEdit ? 'Edit Request' : 'Buat Request'" :description="isEdit ? 'Perbarui data permintaan.' : 'Isi data permintaan baru.'" size="lg" compact @update:model-value="formOpen = $event">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[13px]">
        <div class="sm:col-span-2"><Label class="mb-0.5 text-xs">Title *</Label><Input v-model="form.title" placeholder="Judul permintaan" class="h-8 text-[13px] px-2.5" /></div>
        <div class="sm:col-span-2"><Label class="mb-0.5 text-xs">Description</Label><Input v-model="form.description" placeholder="Deskripsi" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Request Type *</Label><Select v-model="form.request_type" :options="typeOpts" placeholder="Pilih tipe" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Priority *</Label><Select v-model="form.priority" :options="priorityOpts" placeholder="Pilih prioritas" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Status</Label><Select v-model="form.status" :options="statusOpts" placeholder="Pilih status" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Asset</Label><Select v-model="form.asset_id" :options="assetOpts" placeholder="Pilih aset" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Department</Label><Select v-model="form.department_id" :options="deptOpts" placeholder="Pilih departemen" class="h-8 text-[13px] px-2.5" /></div>
        <div v-if="isAdmin"><Label class="mb-0.5 text-xs">Assigned To</Label><Select v-model="form.assigned_to_id" :options="userOpts" placeholder="Pilih user" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Due Date</Label><Input v-model="form.due_date" type="date" class="h-8 text-[13px] px-2.5" /></div>
        <div class="sm:col-span-2"><Label class="mb-0.5 text-xs">Resolution Notes</Label><Input v-model="form.resolution_notes" placeholder="Catatan resolusi" class="h-8 text-[13px] px-2.5" /></div>
      </div>
      <template #footer>
        <Button variant="ghost" size="sm" @click="formOpen = false">Batal</Button>
        <Button size="sm" :loading="formLoading" :disabled="!form.title.trim() || !form.request_type || !form.priority" @click="submitForm">{{ isEdit ? 'Perbarui' : 'Simpan' }}</Button>
      </template>
    </Dialog>

    <ConfirmDialog :open="confirmOpen" title="Hapus Request" :description="`Yakin ingin menghapus ${pendingDelete?.request_number || 'request ini'}?`" :loading="deleting" @confirm="executeDelete" @cancel="confirmOpen = false; pendingDelete = null" />
  </div>
</template>
