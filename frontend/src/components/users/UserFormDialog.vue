<script setup>
import { ref, watch, computed } from 'vue'
import apiClient from '@/services/apiClient'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import { useUiStore } from '@/stores/ui'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  user: { type: Object, default: null },
  roles: { type: Array, default: () => [] },
  departments: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const ui = useUiStore()
const isCreate = computed(() => !props.user)
const loading = ref(false)

const form = ref({
  name: '',
  email: '',
  password: '',
  role_id: '',
  department_id: '',
  is_active: true,
})

watch(() => props.modelValue, (open) => {
  if (!open) return
  if (props.user) {
    form.value = {
      name: props.user.name || '',
      email: props.user.email || '',
      password: '',
      role_id: props.user.role_id || '',
      department_id: props.user.department_id || '',
    is_active: props.user.is_active !== false ? 'true' : 'false',
  }
} else {
  form.value = { name: '', email: '', password: '', role_id: '', department_id: '', is_active: 'true' }
}
})

const roleOpts = computed(() => props.roles.map((r) => ({ label: r.name, value: String(r.id) })))
const deptOpts = computed(() => [{ label: '—', value: '' }, ...props.departments.map((d) => ({ label: d.name, value: String(d.id) }))])
const statusOpts = [{ label: 'Aktif', value: 'true' }, { label: 'Nonaktif', value: 'false' }]

async function submit() {
  const payload = {
    name: form.value.name.trim(),
    email: form.value.email.trim().toLowerCase(),
    role_id: form.value.role_id ? Number(form.value.role_id) : undefined,
    department_id: form.value.department_id ? Number(form.value.department_id) : undefined,
    is_active: form.value.is_active === 'true',
  }
  if (form.value.password.trim()) {
    payload.password = form.value.password.trim()
  }

  loading.value = true
  try {
    if (isCreate.value) {
      await apiClient.createUser(payload)
    } else {
      await apiClient.updateUser(props.user.id, payload)
    }
    ui.pushToast({ title: 'Berhasil', description: isCreate.value ? 'Pengguna berhasil ditambahkan.' : 'Pengguna berhasil diperbarui.', variant: 'success' })
    emit('saved')
    emit('update:modelValue', false)
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Terjadi kesalahan saat menyimpan pengguna.', variant: 'destructive' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog
    :model-value="modelValue"
    :title="isCreate ? 'Tambah Pengguna' : 'Edit Pengguna'"
    :description="isCreate ? 'Buat akun pengguna baru.' : `Perbarui ${user?.name}.`"
    size="md"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="space-y-4 text-sm">
      <div>
        <Label for="uf-name">Nama *</Label>
        <Input id="uf-name" v-model="form.name" placeholder="Nama lengkap" />
      </div>
      <div>
        <Label for="uf-email">Email *</Label>
        <Input id="uf-email" v-model="form.email" type="email" placeholder="email@iams.local" />
      </div>
      <div>
        <Label for="uf-password">{{ isCreate ? 'Password *' : 'Password (biarkan kosong jika tidak diubah)' }}</Label>
        <Input id="uf-password" v-model="form.password" type="password" autocomplete="off" placeholder="••••••••" />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <Label for="uf-role">Role *</Label>
          <Select id="uf-role" v-model="form.role_id" :options="roleOpts" placeholder="Pilih role" />
        </div>
        <div>
          <Label for="uf-dept">Departemen</Label>
          <Select id="uf-dept" v-model="form.department_id" :options="deptOpts" placeholder="Pilih departemen" />
        </div>
      </div>
      <div>
        <Label for="uf-status">Status</Label>
        <Select id="uf-status" v-model="form.is_active" :options="statusOpts" placeholder="Pilih status" />
      </div>
    </div>

    <template #footer>
      <Button variant="ghost" @click="$emit('update:modelValue', false)">Batal</Button>
      <Button :loading="loading" :disabled="!form.name || !form.email || (!form.password && isCreate) || !form.role_id" @click="submit">
        {{ isCreate ? 'Simpan Pengguna' : 'Perbarui' }}
      </Button>
    </template>
  </Dialog>
</template>
