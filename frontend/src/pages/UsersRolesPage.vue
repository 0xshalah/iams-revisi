<script setup>
import { ref, computed, onMounted } from 'vue'
import apiClient from '@/services/apiClient'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import TableSkeleton from '@/components/ui/TableSkeleton.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import UserFormDialog from '@/components/users/UserFormDialog.vue'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/lib/utils'

const ui = useUiStore()

const data = ref([])
const roles = ref([])
const departments = ref([])
const loading = ref(true)
const error = ref(null)
const query = ref('')

const formOpen = ref(false)
const formUser = ref(null)
const confirmOpen = ref(false)
const pendingDeactivate = ref(null)
const deactivating = ref(false)
const confirmDeleteOpen = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  error.value = null
  try {
    const [userRes, roleRes, deptRes] = await Promise.all([
      apiClient.listUsers(),
      apiClient.listRoles(),
      apiClient.listDepartments(),
    ])
    data.value = userRes.data?.data || userRes.data || []
    roles.value = roleRes.data
    departments.value = deptRes.data
  } catch (_) {
    error.value = 'Gagal memuat data pengguna.'
  } finally {
    loading.value = false
  }
}
onMounted(() => load())

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return data.value
  return data.value.filter((u) =>
    u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q) || (u.role_name || '').toLowerCase().includes(q),
  )
})

function openCreate() { formUser.value = null; formOpen.value = true }
function openEdit(user) { formUser.value = user; formOpen.value = true }
function askDeactivate(user) { pendingDeactivate.value = user; confirmOpen.value = true }

async function confirmDeactivate() {
  deactivating.value = true
  try {
    await apiClient.updateUser(pendingDeactivate.value.id, { is_active: false })
    data.value = data.value.map((u) => u.id === pendingDeactivate.value.id ? { ...u, is_active: false, status: 'inactive' } : u)
    ui.pushToast({ title: 'Berhasil', description: `${pendingDeactivate.value.name} telah dinonaktifkan.`, variant: 'success' })
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Tidak dapat menonaktifkan pengguna.', variant: 'destructive' })
  } finally {
    deactivating.value = false
    confirmOpen.value = false
    pendingDeactivate.value = null
  }
}

function askDelete(user) { pendingDelete.value = user; confirmDeleteOpen.value = true }

async function confirmDelete() {
  deleting.value = true
  try {
    await apiClient.deleteUser(pendingDelete.value.id)
    data.value = data.value.filter((u) => u.id !== pendingDelete.value.id)
    ui.pushToast({ title: 'Berhasil', description: `${pendingDelete.value.name} telah dihapus.`, variant: 'success' })
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Tidak dapat menghapus pengguna.', variant: 'destructive' })
  } finally {
    deleting.value = false
    confirmDeleteOpen.value = false
    pendingDelete.value = null
  }
}

</script>

<template>
  <div class="space-y-5">
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Access Control</p>
        <h2 class="text-2xl md:text-3xl font-bold tracking-tight mt-1">{{ t('navigation.usersRoles') }}</h2>
        <p class="text-sm text-muted-foreground mt-1">Manajemen pengguna dan role (Administrator only).</p>
      </div>
      <div class="flex items-center gap-2">
        <Badge variant="info">Admin only</Badge>
        <Button data-testid="users-add-btn" @click="openCreate">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
          Tambah User
        </Button>
      </div>
    </div>

    <Card class="p-4">
      <Label for="users-search">Pencarian</Label>
      <div class="relative max-w-md">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <Input id="users-search" v-model="query" placeholder="Cari nama, email, atau role..." class="pl-9" data-testid="users-search-input" />
      </div>
    </Card>

    <Card class="overflow-hidden">
      <div v-if="loading" class="p-4"><TableSkeleton :rows="3" :columns="5" /></div>
      <ErrorState v-else-if="error" @retry="load()" />
      <EmptyState v-else-if="filtered.length === 0" title="Tidak ada user" />
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm" data-testid="users-table">
          <thead class="bg-secondary/60 text-xs uppercase tracking-wider text-muted-foreground">
            <tr>
              <th class="text-left font-semibold px-4 py-3">Nama</th>
              <th class="text-left font-semibold px-4 py-3">Email</th>
              <th class="text-left font-semibold px-4 py-3">Role</th>
              <th class="text-left font-semibold px-4 py-3">Status</th>
              <th class="text-left font-semibold px-4 py-3">Last login</th>
              <th class="px-4 py-3 w-40"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-for="u in filtered" :key="u.id" class="hover:bg-secondary/40" :data-testid="`user-row-${u.id}`">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="h-9 w-9 rounded-full bg-primary/10 text-primary grid place-items-center text-xs font-bold">{{ u.avatar }}</div>
                  <div>
                    <p class="font-medium">{{ u.name }}</p>
                    <p class="text-xs text-muted-foreground">{{ u.department_name }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-foreground/90">{{ u.email }}</td>
              <td class="px-4 py-3">
                <Badge :variant="u.role_name === 'Administrator' ? 'default' : 'secondary'">{{ u.role_name }}</Badge>
              </td>
              <td class="px-4 py-3"><StatusBadge :value="u.status" kind="user" /></td>
              <td class="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{{ formatDate(u.last_login) }}</td>
              <td class="px-4 py-3 text-right">
                <div class="flex justify-end gap-2">
                  <button class="text-xs text-primary hover:underline" :data-testid="`user-edit-${u.id}`" @click="openEdit(u)">Edit</button>
                  <button v-if="u.is_active !== false" class="text-xs text-destructive hover:underline" :data-testid="`user-deactivate-${u.id}`" @click="askDeactivate(u)">Nonaktifkan</button>
                  <button v-if="u.role_name !== 'Administrator'" class="text-xs text-destructive hover:underline" :data-testid="`user-delete-${u.id}`" @click="askDelete(u)">Hapus</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <UserFormDialog
      v-model="formOpen"
      :user="formUser"
      :roles="roles"
      :departments="departments"
      @saved="load"
    />

    <ConfirmDialog
      v-model="confirmOpen"
      title="Nonaktifkan pengguna?"
      :description="`Akun ${pendingDeactivate?.name} akan dinonaktifkan. Pengguna tidak bisa login setelah ini.`"
      confirm-text="Nonaktifkan"
      :loading="deactivating"
      variant="destructive"
      @confirm="confirmDeactivate"
    />

    <ConfirmDialog
      v-model="confirmDeleteOpen"
      title="Hapus pengguna?"
      :description="`Akun ${pendingDelete?.name} akan dihapus permanen. Tindakan ini tidak dapat dibatalkan.`"
      confirm-text="Hapus"
      :loading="deleting"
      variant="destructive"
      @confirm="confirmDelete"
    />
  </div>
</template>
