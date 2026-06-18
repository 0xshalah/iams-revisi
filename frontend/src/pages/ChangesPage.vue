<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
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
const { t } = useI18n()
const isAdmin = computed(() => auth.isAdmin)

const loading = ref(true)
const error = ref(null)
const data = ref([])
const search = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const riskFilter = ref('')
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
const incidents = ref([])
const problems = ref([])
const requests = ref([])
const users = ref([])

const statusOpts = ['Draft','Submitted','Under Review','Approved','Rejected','Scheduled','Implementing','Completed','Failed','Cancelled','Closed'].map(s => ({ label: s, value: s }))
const typeOpts = ['Standard','Normal','Emergency','Maintenance','Configuration','Replacement','Relocation','Other'].map(s => ({ label: s, value: s }))
const riskOpts = ['Low','Medium','High','Critical'].map(s => ({ label: s, value: s }))
const impactOpts = ['Low','Medium','High','Critical'].map(s => ({ label: s, value: s }))

const assetOpts = computed(() => assets.value.map(a => ({ label: a.asset_tag, value: String(a.id) })))
const incidentOpts = computed(() => incidents.value.map(i => ({ label: i.code, value: String(i.id) })))
const problemOpts = computed(() => problems.value.map(p => ({ label: p.code, value: String(p.id) })))
const requestOpts = computed(() => requests.value.map(r => ({ label: r.request_number, value: String(r.id) })))
const userOpts = computed(() => users.value.map(u => ({ label: u.name, value: String(u.id) })))

async function load() {
  loading.value = true; error.value = null
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    if (typeFilter.value) params.change_type = typeFilter.value
    if (riskFilter.value) params.risk_level = riskFilter.value
    if (search.value) params.search = search.value
    const [chgRes, assetRes, incRes, prbRes, reqRes, userRes] = await Promise.all([
      apiClient.listChanges(params),
      apiClient.listAssets().catch(() => ({ data: { data: [] } })),
      apiClient.listIncidents().catch(() => ({ data: { data: [] } })),
      apiClient.listProblems().catch(() => ({ data: { data: [] } })),
      apiClient.listRequests().catch(() => ({ data: { data: [] } })),
      isAdmin.value ? apiClient.listUsers().catch(() => ({ data: { data: [] } })) : Promise.resolve({ data: { data: [] } }),
    ])
    data.value = chgRes.data?.data || chgRes.data || []
    assets.value = assetRes.data?.data || assetRes.data || []
    incidents.value = incRes.data?.data || incRes.data || []
    problems.value = prbRes.data?.data || prbRes.data || []
    requests.value = reqRes.data?.data || reqRes.data || []
    users.value = userRes.data?.data || userRes.data || []
  } catch (_) { error.value = 'Gagal memuat data.' }
  finally { loading.value = false }
}

onMounted(() => load())
watch([search, statusFilter, typeFilter, riskFilter], () => { page.value = 1; load() })

const filtered = computed(() => data.value)
const paged = computed(() => {
  const start = (page.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

const form = ref({ title: '', description: '', change_type: '', risk_level: 'Low', impact: 'Low', status: 'Submitted', asset_id: '', incident_id: '', problem_id: '', request_id: '', assignee_id: '', approver_id: '', planned_start: '', planned_end: '', implementation_notes: '', rollback_plan: '', approval_notes: '' })

function openCreate() {
  formItem.value = null
  form.value = { title: '', description: '', change_type: '', risk_level: 'Low', impact: 'Low', status: 'Submitted', asset_id: '', incident_id: '', problem_id: '', request_id: '', assignee_id: '', approver_id: '', planned_start: '', planned_end: '', implementation_notes: '', rollback_plan: '', approval_notes: '' }
  formOpen.value = true
}

function openEdit(item) {
  formItem.value = item
  form.value = {
    title: item.title || '', description: item.description || '',
    change_type: item.change_type || '', risk_level: item.risk_level || 'Low', impact: item.impact || 'Low', status: item.status || 'Draft',
    asset_id: item.asset_id ? String(item.asset_id) : '',
    incident_id: item.incident_id ? String(item.incident_id) : '',
    problem_id: item.problem_id ? String(item.problem_id) : '',
    request_id: item.request_id ? String(item.request_id) : '',
    assignee_id: item.assignee_id ? String(item.assignee_id) : '',
    approver_id: item.approver_id ? String(item.approver_id) : '',
    planned_start: item.planned_start ? item.planned_start.substring(0,16) : '',
    planned_end: item.planned_end ? item.planned_end.substring(0,16) : '',
    implementation_notes: item.implementation_notes || '',
    rollback_plan: item.rollback_plan || '',
    approval_notes: item.approval_notes || '',
  }
  formOpen.value = true
}

async function submitForm() {
  formLoading.value = true
  try {
    const payload = {
      title: form.value.title.trim(),
      description: form.value.description.trim() || undefined,
      change_type: form.value.change_type,
      risk_level: form.value.risk_level,
      impact: form.value.impact,
      status: form.value.status,
      asset_id: form.value.asset_id || undefined,
      incident_id: form.value.incident_id || undefined,
      problem_id: form.value.problem_id || undefined,
      request_id: form.value.request_id || undefined,
      assignee_id: form.value.assignee_id || undefined,
      approver_id: form.value.approver_id || undefined,
      planned_start: form.value.planned_start || undefined,
      planned_end: form.value.planned_end || undefined,
      implementation_notes: form.value.implementation_notes.trim() || undefined,
      rollback_plan: form.value.rollback_plan.trim() || undefined,
      approval_notes: form.value.approval_notes.trim() || undefined,
    }
    if (isEdit.value) {
      await apiClient.updateChange(formItem.value.id, payload)
      ui.pushToast({ title: 'Berhasil', description: 'Perubahan diperbarui.', variant: 'success' })
    } else {
      await apiClient.createChange(payload)
      ui.pushToast({ title: 'Berhasil', description: 'Perubahan dibuat.', variant: 'success' })
    }
    formOpen.value = false; load()
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Terjadi kesalahan.', variant: 'destructive' })
  } finally { formLoading.value = false }
}

async function doApprove(item) {
  try {
    await apiClient.approveChange(item.id, { approval_notes: 'Approved' })
    ui.pushToast({ title: 'Berhasil', description: 'Perubahan disetujui.', variant: 'success' })
    load()
  } catch (err) { ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Gagal.', variant: 'destructive' }) }
}

async function doReject(item) {
  try {
    await apiClient.rejectChange(item.id, { approval_notes: 'Rejected' })
    ui.pushToast({ title: 'Berhasil', description: 'Perubahan ditolak.', variant: 'success' })
    load()
  } catch (err) { ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Gagal.', variant: 'destructive' }) }
}

function confirmDelete(item) { pendingDelete.value = item; confirmOpen.value = true }

async function executeDelete() {
  if (!pendingDelete.value) return; deleting.value = true
  try {
    await apiClient.deleteChange(pendingDelete.value.id)
    ui.pushToast({ title: 'Berhasil', description: 'Perubahan dihapus.', variant: 'success' })
    confirmOpen.value = false; pendingDelete.value = null; load()
  } catch (err) { ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Gagal.', variant: 'destructive' }) }
  finally { deleting.value = false }
}

const riskVariant = (r) => ({ Low: 'info', Medium: 'warning', High: 'orange', Critical: 'destructive' }[r] || 'secondary')
const typeLabel = (t) => ({ Standard: 'Standard', Normal: 'Normal', Emergency: 'Darurat', Maintenance: 'Pemeliharaan', Configuration: 'Konfigurasi', Replacement: 'Penggantian', Relocation: 'Pemindahan', Other: 'Lainnya' }[t] || t)
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h1 class="text-lg font-bold tracking-tight">{{ t('navigation.changes') }}</h1>
        <p class="text-xs text-muted-foreground mt-0.5">Kelola perubahan IT: rencana, persetujuan, dan eksekusi.</p>
      </div>
      <Button size="sm" @click="openCreate">+ {{ t('changes.addChange') }}</Button>
    </div>

    <Card class="p-4">
      <div class="flex flex-wrap items-center gap-2 mb-3">
        <div class="relative w-full max-w-[200px]">
          <Input v-model="search" placeholder="Cari..." class="h-8 text-[13px] pl-7 pr-3" />
          <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </div>
        <Select v-model="statusFilter" :options="[{label:'All Status',value:''},...statusOpts]" class="h-8 text-[13px] w-[150px]" />
        <Select v-model="typeFilter" :options="[{label:'All Types',value:''},...typeOpts]" class="h-8 text-[13px] w-[150px]" />
        <Select v-model="riskFilter" :options="[{label:'All Risk',value:''},...riskOpts]" class="h-8 text-[13px] w-[130px]" />
      </div>

      <TableSkeleton v-if="loading" :cols="7" :rows="4" />
      <ErrorState v-else-if="error" :message="error" @retry="load" />
      <EmptyState v-else-if="!filtered.length" title="Belum ada change" description="Belum ada perubahan yang dibuat." @action="openCreate" />

      <template v-else>
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b text-left">
                <th class="py-2 px-2 font-medium text-muted-foreground">{{ t('changes.number') }}</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">{{ t('changes.title_') }}</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">{{ t('changes.changeType') }}</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">{{ t('changes.riskLevel') }}</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">{{ t('changes.impact') }}</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">{{ t('changes.status') }}</th>
                <th class="py-2 px-2 font-medium text-muted-foreground">{{ t('changes.requester') }}</th>
                <th class="py-2 px-2 font-medium text-muted-foreground w-40">{{ t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paged" :key="item.id" class="border-b hover:bg-muted/50 transition-colors">
                <td class="py-1.5 px-2 font-mono text-[11px]">{{ item.change_number }}</td>
                <td class="py-1.5 px-2 max-w-[180px] truncate" :title="item.title">{{ item.title }}</td>
                <td class="py-1.5 px-2"><span class="inline-block px-1.5 py-0.5 rounded text-[10px] bg-muted">{{ typeLabel(item.change_type) }}</span></td>
                <td class="py-1.5 px-2"><StatusBadge :variant="riskVariant(item.risk_level)">{{ item.risk_level }}</StatusBadge></td>
                <td class="py-1.5 px-2"><StatusBadge :variant="item.impact === 'Low' ? 'info' : item.impact === 'Medium' ? 'warning' : 'destructive'">{{ item.impact }}</StatusBadge></td>
                <td class="py-1.5 px-2"><StatusBadge :status="item.status">{{ item.status }}</StatusBadge></td>
                <td class="py-1.5 px-2">{{ item.requester_name || '-' }}</td>
                <td class="py-1.5 px-2">
                  <div class="flex items-center gap-1 flex-wrap">
                    <Button variant="ghost" size="xs" @click="openEdit(item)">Edit</Button>
                    <template v-if="isAdmin">
                      <Button v-if="item.status === 'Under Review' || item.status === 'Submitted'" variant="ghost" size="xs" class="text-green-600" @click="doApprove(item)">Approve</Button>
                      <Button v-if="item.status === 'Under Review' || item.status === 'Submitted'" variant="ghost" size="xs" class="text-red-600" @click="doReject(item)">Reject</Button>
                      <Button variant="ghost" size="xs" class="text-destructive" @click="confirmDelete(item)">Hapus</Button>
                    </template>
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
    <Dialog :model-value="formOpen" :title="isEdit ? t('changes.editChange') : t('changes.addChange')" :description="isEdit ? 'Perbarui data perubahan.' : 'Isi data perubahan baru.'" size="lg" compact @update:model-value="formOpen = $event">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[13px]">
        <div class="sm:col-span-2"><Label class="mb-0.5 text-xs">Title *</Label><Input v-model="form.title" placeholder="Judul perubahan" class="h-8 text-[13px] px-2.5" /></div>
        <div class="sm:col-span-2"><Label class="mb-0.5 text-xs">Description</Label><Input v-model="form.description" placeholder="Deskripsi" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Change Type *</Label><Select v-model="form.change_type" :options="typeOpts" placeholder="Pilih tipe" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Status</Label><Select v-model="form.status" :options="statusOpts" placeholder="Pilih status" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Risk Level *</Label><Select v-model="form.risk_level" :options="riskOpts" placeholder="Pilih risiko" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Impact *</Label><Select v-model="form.impact" :options="impactOpts" placeholder="Pilih dampak" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Asset</Label><Select v-model="form.asset_id" :options="assetOpts" placeholder="Pilih aset" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Incident</Label><Select v-model="form.incident_id" :options="incidentOpts" placeholder="Pilih insiden" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Problem</Label><Select v-model="form.problem_id" :options="problemOpts" placeholder="Pilih problem" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Request</Label><Select v-model="form.request_id" :options="requestOpts" placeholder="Pilih request" class="h-8 text-[13px] px-2.5" /></div>
        <div v-if="isAdmin"><Label class="mb-0.5 text-xs">Assignee</Label><Select v-model="form.assignee_id" :options="userOpts" placeholder="Pilih user" class="h-8 text-[13px] px-2.5" /></div>
        <div v-if="isAdmin"><Label class="mb-0.5 text-xs">Approver</Label><Select v-model="form.approver_id" :options="userOpts" placeholder="Pilih approver" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Planned Start</Label><Input v-model="form.planned_start" type="datetime-local" class="h-8 text-[13px] px-2.5" /></div>
        <div><Label class="mb-0.5 text-xs">Planned End</Label><Input v-model="form.planned_end" type="datetime-local" class="h-8 text-[13px] px-2.5" /></div>
        <div class="sm:col-span-2"><Label class="mb-0.5 text-xs">Implementation Notes</Label><Input v-model="form.implementation_notes" placeholder="Catatan implementasi" class="h-8 text-[13px] px-2.5" /></div>
        <div class="sm:col-span-2"><Label class="mb-0.5 text-xs">Rollback Plan</Label><Input v-model="form.rollback_plan" placeholder="Rencana rollback" class="h-8 text-[13px] px-2.5" /></div>
        <div class="sm:col-span-2"><Label class="mb-0.5 text-xs">Approval Notes</Label><Input v-model="form.approval_notes" placeholder="Catatan persetujuan" class="h-8 text-[13px] px-2.5" /></div>
      </div>
      <template #footer>
        <Button variant="ghost" size="sm" @click="formOpen = false">Batal</Button>
        <Button size="sm" :loading="formLoading" :disabled="!form.title.trim() || !form.change_type" @click="submitForm">{{ isEdit ? 'Perbarui' : 'Simpan' }}</Button>
      </template>
    </Dialog>

    <ConfirmDialog :open="confirmOpen" title="Hapus Change" :description="`Yakin ingin menghapus ${pendingDelete?.change_number || 'change ini'}?`" :loading="deleting" @confirm="executeDelete" @cancel="confirmOpen = false; pendingDelete = null" />
  </div>
</template>
