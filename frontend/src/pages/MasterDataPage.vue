<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '@/services/apiClient'
import { useUiStore } from '@/stores/ui'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import Dialog from '@/components/ui/Dialog.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import TableSkeleton from '@/components/ui/TableSkeleton.vue'
import Pagination from '@/components/ui/Pagination.vue'

const ui = useUiStore()
const { t } = useI18n()

const TABS = computed(() => [
  { key: 'departments', label: t('masterData.departments') },
  { key: 'locations', label: t('masterData.locations') },
  { key: 'categories', label: t('masterData.categories') },
  { key: 'brands', label: t('masterData.brands') },
  { key: 'models', label: t('masterData.models') },
])

const activeTab = ref('departments')
const loading = ref(true)
const error = ref(null)
const data = ref([])
const query = ref('')
const page = ref(1)
const pageSize = 10

// form state
const formOpen = ref(false)
const formItem = ref(null)
const formLoading = ref(false)
const isEdit = computed(() => !!formItem.value)

const confirmOpen = ref(false)
const pendingDelete = ref(null)
const deleting = ref(false)

// dropdowns for models tab
const brands = ref([])
const categories = ref([])

const apiForTab = (tab) => ({
  departments: apiClient,
  locations: apiClient,
  categories: apiClient,
  brands: apiClient,
  models: apiClient,
}[tab])

const listMethod = {
  departments: 'listDepartments',
  locations: 'listLocations',
  categories: 'listCategories',
  brands: 'listBrands',
  models: 'listModels',
}

const createMethod = {
  departments: 'createDepartment',
  locations: 'createLocation',
  categories: 'createCategory',
  brands: 'createBrand',
  models: 'createModel',
}

const updateMethod = {
  departments: 'updateDepartment',
  locations: 'updateLocation',
  categories: 'updateCategory',
  brands: 'updateBrand',
  models: 'updateModel',
}

const deleteMethod = {
  departments: 'deleteDepartment',
  locations: 'deleteLocation',
  categories: 'deleteCategory',
  brands: 'deleteBrand',
  models: 'deleteModel',
}

const tabLabel = {
  departments: { singular: 'Department', article: 'Department' },
  locations: { singular: 'Location', article: 'Location' },
  categories: { singular: 'Category', article: 'Category' },
  brands: { singular: 'Brand', article: 'Brand' },
  models: { singular: 'Model', article: 'Model' },
}

const columnsForTab = computed(() => {
  const base = [{ key: 'name', label: t('masterData.name') }]
  if (activeTab.value === 'locations') base.push({ key: 'description', label: t('assets.notes') })
  if (activeTab.value === 'models') {
    base.push({ key: 'brand_name', label: t('masterData.brand') })
    base.push({ key: 'category_name', label: t('masterData.category') })
    base.push({ key: 'specifications', label: t('masterData.specifications') })
  }
  if (activeTab.value === 'departments') base.push({ key: 'description', label: t('assets.notes') })
  return base
})

async function load() {
  loading.value = true
  error.value = null
  try {
    if (activeTab.value === 'models') {
      const [b, c] = await Promise.all([
        apiClient.listBrands(),
        apiClient.listCategories(),
      ])
      brands.value = b.data?.data || b.data || []
      categories.value = c.data?.data || c.data || []
    }
    const api = apiForTab(activeTab.value)
    const res = await api[listMethod[activeTab.value]]()
    data.value = res.data?.data || res.data || []
  } catch (_) {
    error.value = 'Gagal memuat data.'
  } finally {
    loading.value = false
  }
}

watch(activeTab, () => {
  page.value = 1
  query.value = ''
  load()
})

onMounted(() => load())

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return data.value
  return data.value.filter((item) =>
    (item.name || '').toLowerCase().includes(q) ||
    (item.description || '').toLowerCase().includes(q) ||
    (item.brand_name || '').toLowerCase().includes(q) ||
    (item.category_name || '').toLowerCase().includes(q)
  )
})

const paged = computed(() => {
  const start = (page.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

watch(query, () => { page.value = 1 })

// Form helpers
const form = ref({ name: '', description: '', brand_id: '', category_id: '', specifications: '' })

function openCreate() {
  formItem.value = null
  form.value = { name: '', description: '', brand_id: '', category_id: '', specifications: '' }
  formOpen.value = true
}

function openEdit(item) {
  formItem.value = item
  form.value = {
    name: item.name || '',
    description: item.description || '',
    brand_id: item.brand_id ? String(item.brand_id) : '',
    category_id: item.category_id ? String(item.category_id) : '',
    specifications: item.specifications || '',
  }
  formOpen.value = true
}

async function submitForm() {
  formLoading.value = true
  try {
    const api = apiForTab(activeTab.value)
    const payload = { name: form.value.name.trim() }
    if (activeTab.value === 'locations' || activeTab.value === 'departments')
      payload.description = form.value.description.trim() || undefined
    if (activeTab.value === 'models') {
      payload.brand_id = form.value.brand_id || undefined
      payload.category_id = form.value.category_id || undefined
      payload.specifications = form.value.specifications.trim() || undefined
    }

    if (isEdit.value) {
      await api[updateMethod[activeTab.value]](formItem.value.id, payload)
      ui.pushToast({ title: 'Berhasil', description: `${tabLabel[activeTab.value].singular} diperbarui.`, variant: 'success' })
    } else {
      await api[createMethod[activeTab.value]](payload)
      ui.pushToast({ title: 'Berhasil', description: `${tabLabel[activeTab.value].singular} ditambahkan.`, variant: 'success' })
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
    const api = apiForTab(activeTab.value)
    await api[deleteMethod[activeTab.value]](pendingDelete.value.id)
    ui.pushToast({ title: 'Berhasil', description: `${tabLabel[activeTab.value].singular} dihapus.`, variant: 'success' })
    confirmOpen.value = false
    pendingDelete.value = null
    load()
  } catch (err) {
    const msg = err.data?.error || 'Gagal menghapus.'
    ui.pushToast({ title: 'Gagal', description: msg, variant: 'destructive' })
  } finally {
    deleting.value = false
  }
}

const brandOpts = computed(() => brands.value.map(b => ({ label: b.name, value: String(b.id) })))
const categoryOpts = computed(() => categories.value.map(c => ({ label: c.name, value: String(c.id) })))
</script>

<template>
  <div class="space-y-4">
    <div>
      <h1 class="text-lg font-bold tracking-tight">{{ t('masterData.title') }}</h1>
      <p class="text-xs text-muted-foreground mt-0.5">Kelola data master: departemen, lokasi, kategori, merek, dan model.</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-0.5 bg-muted rounded-lg p-0.5 w-fit">
      <button
        v-for="tab in TABS"
        :key="tab.key"
        :class="[
          'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
          activeTab === tab.key ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground',
        ]"
        @click="activeTab = tab.key"
      >{{ tab.label }}</button>
    </div>

    <Card class="p-4">
      <!-- Toolbar -->
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
        <div class="relative w-full max-w-xs">
          <Input v-model="query" placeholder="Cari..." class="h-8 text-[13px] pl-7 pr-3" />
          <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </div>
        <Button size="sm" @click="openCreate">+ {{ tabLabel[activeTab].singular }}</Button>
      </div>

      <!-- Loading -->
      <TableSkeleton v-if="loading" :cols="columnsForTab.length" :rows="3" class="mb-4" />

      <!-- Error -->
      <ErrorState v-else-if="error" :message="error" @retry="load" />

      <!-- Empty -->
      <EmptyState
        v-else-if="!filtered.length"
        title="Belum ada data"
        :description="`Belum ada ${tabLabel[activeTab].article.toLowerCase()} yang ditambahkan.`"
        @action="openCreate"
      />

      <!-- Table -->
      <template v-else>
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b text-left">
                <th v-for="col in columnsForTab" :key="col.key" class="py-2 px-2 font-medium text-muted-foreground">{{ col.label }}</th>
                <th class="py-2 px-2 font-medium text-muted-foreground w-20">{{ t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paged" :key="item.id" class="border-b hover:bg-muted/50 transition-colors">
                <td v-for="col in columnsForTab" :key="col.key" class="py-1.5 px-2">{{ item[col.key] || '-' }}</td>
                <td class="py-1.5 px-2">
                  <div class="flex items-center gap-1">
                    <Button variant="ghost" size="xs" @click="openEdit(item)">{{ t('common.edit') }}</Button>
                    <Button variant="ghost" size="xs" class="text-destructive hover:text-destructive" @click="confirmDelete(item)">{{ t('common.delete') }}</Button>
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
    <Dialog
      :model-value="formOpen"
      :title="isEdit ? `Edit ${tabLabel[activeTab].singular}` : `Tambah ${tabLabel[activeTab].singular}`"
      :description="isEdit ? `Perbarui data ${tabLabel[activeTab].article.toLowerCase()}.` : `Isi data ${tabLabel[activeTab].article.toLowerCase()} baru.`"
      compact
      @update:model-value="formOpen = $event"
    >
      <div class="grid grid-cols-1 gap-2 text-[13px]">
        <div>
          <Label class="mb-0.5 text-xs">Name *</Label>
          <Input v-model="form.name" placeholder="Nama" class="h-8 text-[13px] px-2.5" />
        </div>
        <div v-if="activeTab === 'locations' || activeTab === 'departments'">
          <Label class="mb-0.5 text-xs">Description</Label>
          <Input v-model="form.description" placeholder="Deskripsi (opsional)" class="h-8 text-[13px] px-2.5" />
        </div>
        <template v-if="activeTab === 'models'">
          <div>
            <Label class="mb-0.5 text-xs">Brand</Label>
            <Select v-model="form.brand_id" :options="brandOpts" placeholder="Pilih merek" class="h-8 text-[13px] px-2.5" />
          </div>
          <div>
            <Label class="mb-0.5 text-xs">Category</Label>
            <Select v-model="form.category_id" :options="categoryOpts" placeholder="Pilih kategori" class="h-8 text-[13px] px-2.5" />
          </div>
          <div>
            <Label class="mb-0.5 text-xs">Specifications</Label>
            <Input v-model="form.specifications" placeholder="Spesifikasi (opsional)" class="h-8 text-[13px] px-2.5" />
          </div>
        </template>
      </div>
      <template #footer>
        <Button variant="ghost" size="sm" @click="formOpen = false">Batal</Button>
        <Button size="sm" :loading="formLoading" :disabled="!form.name.trim()" @click="submitForm">
          {{ isEdit ? 'Perbarui' : 'Simpan' }}
        </Button>
      </template>
    </Dialog>

    <!-- Delete Confirm -->
    <ConfirmDialog
      :open="confirmOpen"
      title="Hapus Data"
      :description="`Yakin ingin menghapus ${pendingDelete?.name || 'data ini'}? Data yang masih digunakan tidak dapat dihapus.`"
      :loading="deleting"
      @confirm="executeDelete"
      @cancel="confirmOpen = false; pendingDelete = null"
    />
  </div>
</template>
