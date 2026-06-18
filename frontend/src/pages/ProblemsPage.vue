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
import ProblemFormDialog from '@/components/problems/ProblemFormDialog.vue'
import { useUiStore } from '@/stores/ui'
import { formatDate, timeAgo } from '@/lib/utils'

const ui = useUiStore()
const auth = useAuthStore()

const data = ref([])
const users = ref([])
const loading = ref(true)
const error = ref(null)
const query = ref('')
const priorityFilter = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = 8

const detailOpen = ref(false)
const detailItem = ref(null)
const confirmOpen = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)
const formOpen = ref(false)
const formProblem = ref(null)

const userMap = computed(() => Object.fromEntries(users.value.map((u) => [u.id, u])))

async function load() {
  loading.value = true
  error.value = null
  try {
    const [prbRes, userRes] = await Promise.all([
      apiClient.listProblems(),
      apiClient.listUsers().catch(() => ({ data: [] })),
    ])
    data.value = prbRes.data?.data || prbRes.data || []
    users.value = userRes.data?.data || userRes.data || []
  } catch (_) {
    error.value = 'Gagal memuat problem.'
  } finally {
    loading.value = false
  }
}

onMounted(() => load())

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return data.value.filter((p) => {
    if (priorityFilter.value && p.priority !== priorityFilter.value) return false
    if (statusFilter.value && p.status !== statusFilter.value) return false
    if (!q) return true
    return p.code.toLowerCase().includes(q) || p.title.toLowerCase().includes(q) || (p.root_cause || '').toLowerCase().includes(q)
  })
})

watch([query, priorityFilter, statusFilter], () => { page.value = 1 })

const paged = computed(() => {
  const s = (page.value - 1) * pageSize
  return filtered.value.slice(s, s + pageSize)
})

function openDetail(item) { detailItem.value = item; detailOpen.value = true }
function openCreate() { formProblem.value = null; formOpen.value = true }
function openEdit(item) { formProblem.value = item; formOpen.value = true }
function askDelete(item) { pendingDelete.value = item; confirmOpen.value = true }

async function confirmDelete() {
  deleting.value = true
  try {
    await apiClient.deleteProblem(pendingDelete.value.id)
    data.value = data.value.filter((i) => i.id !== pendingDelete.value.id)
    ui.pushToast({ title: 'Problem dihapus', description: `${pendingDelete.value.code} dihapus.`, variant: 'success' })
  } catch (err) {
    ui.pushToast({ title: 'Gagal menghapus', description: err.data?.error || 'Tidak dapat menghapus problem.', variant: 'destructive' })
  } finally {
    deleting.value = false
    confirmOpen.value = false
    pendingDelete.value = null
  }
}

function reset() { query.value = ''; priorityFilter.value = ''; statusFilter.value = '' }

const priorityOpts = ['Critical', 'High', 'Medium', 'Low'].map((v) => ({ label: v, value: v }))
const statusOpts = ['Open', 'Investigating', 'Known Error', 'Closed'].map((v) => ({ label: v, value: v }))
</script>

<template>
  <div class="space-y-5">
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Problem Management</p>
        <h2 class="text-2xl md:text-3xl font-bold tracking-tight mt-1">Akar Masalah</h2>
        <p class="text-sm text-muted-foreground mt-1">Dokumentasikan root cause dari insiden berulang.</p>
      </div>
      <div class="flex items-center gap-2">
        <Button data-testid="problems-add-btn" @click="openCreate">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
          Problem Baru
        </Button>
      </div>
    </div>

    <Card class="p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="lg:col-span-2">
          <Label for="prb-search">Pencarian</Label>
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <Input id="prb-search" v-model="query" placeholder="Cari kode, judul, atau root cause..." class="pl-9" data-testid="problems-search-input" />
          </div>
        </div>
        <div>
          <Label>Priority</Label>
          <Select v-model="priorityFilter" :options="priorityOpts" placeholder="Semua priority" data-testid="problems-filter-priority" />
        </div>
        <div>
          <Label>Status</Label>
          <Select v-model="statusFilter" :options="statusOpts" placeholder="Semua status" data-testid="problems-filter-status" />
        </div>
      </div>
      <div v-if="query || priorityFilter || statusFilter" class="mt-3 flex items-center gap-3 text-xs">
        <span class="text-muted-foreground">{{ filtered.length }} problem sesuai filter</span>
        <button class="text-primary hover:underline" @click="reset" data-testid="problems-reset-filters">Reset filter</button>
      </div>
    </Card>

    <Card class="overflow-hidden">
      <div v-if="loading" class="p-4"><TableSkeleton :rows="5" :columns="6" /></div>
      <ErrorState v-else-if="error" @retry="load()" />
      <EmptyState v-else-if="filtered.length === 0" title="Tidak ada problem" description="Tidak ada problem yang sesuai filter." icon="search" />
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm" data-testid="problems-table">
          <thead class="bg-secondary/60 text-xs uppercase tracking-wider text-muted-foreground">
            <tr>
              <th class="text-left font-semibold px-4 py-3">Problem</th>
              <th class="text-left font-semibold px-4 py-3">Priority</th>
              <th class="text-left font-semibold px-4 py-3">Status</th>
              <th class="text-left font-semibold px-4 py-3">Owner</th>
              <th class="text-left font-semibold px-4 py-3">Dibuat</th>
              <th class="px-4 py-3 w-20"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-for="row in paged" :key="row.id" class="hover:bg-secondary/40 transition-colors" :data-testid="`problem-row-${row.code}`">
              <td class="px-4 py-3">
                <div class="font-medium">{{ row.title }}</div>
                <div class="text-xs text-muted-foreground font-mono">{{ row.code }}</div>
              </td>
              <td class="px-4 py-3"><StatusBadge :value="row.priority" kind="priority" /></td>
              <td class="px-4 py-3"><StatusBadge :value="row.status" kind="problemStatus" /></td>
              <td class="px-4 py-3 text-sm">{{ userMap[row.owner_id]?.name || '—' }}</td>
              <td class="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{{ timeAgo(row.created_at) }}</td>
              <td class="px-4 py-3">
                <div class="flex justify-end gap-1">
                  <Button variant="ghost" size="icon" :data-testid="`problem-view-${row.code}`" @click="openDetail(row)" aria-label="Detail">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                  </Button>
                  <Button variant="ghost" size="icon" :data-testid="`problem-edit-${row.code}`" @click="openEdit(row)" aria-label="Edit">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                  </Button>
                  <Button v-if="auth.isAdmin" variant="ghost" size="icon" class="text-destructive hover:bg-destructive/10" :data-testid="`problem-delete-${row.code}`" @click="askDelete(row)" aria-label="Hapus">
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
      <div v-if="detailItem" class="space-y-4 text-sm" data-testid="problem-detail">
        <div class="flex flex-wrap gap-2">
          <StatusBadge :value="detailItem.priority" kind="priority" />
          <StatusBadge :value="detailItem.status" kind="problemStatus" />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p class="text-muted-foreground text-xs uppercase tracking-wider">Owner</p>
            <p>{{ userMap[detailItem.owner_id]?.name || '—' }}</p>
          </div>
          <div>
            <p class="text-muted-foreground text-xs uppercase tracking-wider">Dibuat</p>
            <p>{{ formatDate(detailItem.created_at) }}</p>
          </div>
        </div>
        <div>
          <p class="text-muted-foreground text-xs uppercase tracking-wider mb-1">Root cause</p>
          <p class="leading-relaxed">{{ detailItem.root_cause || '—' }}</p>
        </div>
      </div>
      <template #footer>
        <Button variant="ghost" @click="detailOpen = false" data-testid="problem-detail-close">Tutup</Button>
      </template>
    </Dialog>

    <ProblemFormDialog
      v-model="formOpen"
      :problem="formProblem"
      :users="users"
      @saved="load"
    />

    <ConfirmDialog
      v-model="confirmOpen"
      title="Hapus problem?"
      :description="`Problem ${pendingDelete?.code} akan dihapus secara permanen.`"
      confirm-text="Hapus"
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>
