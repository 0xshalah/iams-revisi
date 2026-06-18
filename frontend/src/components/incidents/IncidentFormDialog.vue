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
  incident: { type: Object, default: null },
  assets: { type: Array, default: () => [] },
  users: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const ui = useUiStore()
const isCreate = computed(() => !props.incident)
const loading = ref(false)

const form = ref({
  title: '',
  description: '',
  asset_id: '',
  severity: 'Medium',
  status: 'Open',
  assignee_id: '',
})

watch(() => props.modelValue, (open) => {
  if (!open) return
  if (props.incident) {
    form.value = {
      title: props.incident.title || '',
      description: props.incident.description || '',
      asset_id: props.incident.asset_id || '',
      severity: props.incident.severity || 'Medium',
      status: props.incident.status || 'Open',
      assignee_id: props.incident.assignee_id || '',
    }
  } else {
    form.value = { title: '', description: '', asset_id: '', severity: 'Medium', status: 'Open', assignee_id: '' }
  }
})

const severityOpts = ['Critical', 'High', 'Medium', 'Low'].map((s) => ({ label: s, value: s }))
const statusOpts = ['Open', 'In Progress', 'Resolved', 'Closed'].map((s) => ({ label: s, value: s }))
const assetOpts = computed(() => [{ label: '—', value: '' }, ...props.assets.map((a) => ({ label: `${a.asset_tag} (${a.category_name})`, value: String(a.id) }))])
const userOpts = computed(() => [{ label: '—', value: '' }, ...props.users.map((u) => ({ label: u.name, value: String(u.id) }))])

async function submit() {
  const payload = {
    title: form.value.title.trim(),
    description: form.value.description.trim() || undefined,
    asset_id: form.value.asset_id ? Number(form.value.asset_id) : undefined,
    severity: form.value.severity,
    status: form.value.status,
    assignee_id: form.value.assignee_id ? Number(form.value.assignee_id) : undefined,
  }

  loading.value = true
  try {
    if (isCreate.value) {
      await apiClient.createIncident(payload)
    } else {
      await apiClient.updateIncident(props.incident.id, payload)
    }
    ui.pushToast({ title: 'Berhasil', description: isCreate.value ? 'Insiden berhasil dibuat.' : 'Insiden berhasil diperbarui.', variant: 'success' })
    emit('saved')
    emit('update:modelValue', false)
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Terjadi kesalahan saat menyimpan insiden.', variant: 'destructive' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog
    :model-value="modelValue"
    :title="isCreate ? 'Insiden Baru' : 'Edit Insiden'"
    :description="isCreate ? 'Catat gangguan operasional.' : `Perbarui ${incident?.code}.`"
    size="lg"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
      <div class="sm:col-span-2">
        <Label for="if-title">Judul *</Label>
        <Input id="if-title" v-model="form.title" placeholder="Ringkas masalah..." />
      </div>
      <div>
        <Label for="if-severity">Severity *</Label>
        <Select id="if-severity" v-model="form.severity" :options="severityOpts" placeholder="Pilih severity" />
      </div>
      <div>
        <Label for="if-status">Status</Label>
        <Select id="if-status" v-model="form.status" :options="statusOpts" placeholder="Pilih status" />
      </div>
      <div>
        <Label for="if-asset">Aset Terkait</Label>
        <Select id="if-asset" v-model="form.asset_id" :options="assetOpts" placeholder="Pilih aset" />
      </div>
      <div>
        <Label for="if-assignee">Assignee</Label>
        <Select id="if-assignee" v-model="form.assignee_id" :options="userOpts" placeholder="Pilih assignee" />
      </div>
      <div class="sm:col-span-2">
        <Label for="if-desc">Deskripsi</Label>
        <textarea id="if-desc" v-model="form.description" rows="3" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2" placeholder="Detail insiden..." />
      </div>
    </div>

    <template #footer>
      <Button variant="ghost" @click="$emit('update:modelValue', false)">Batal</Button>
      <Button :loading="loading" :disabled="!form.title" @click="submit">
        {{ isCreate ? 'Simpan Insiden' : 'Perbarui' }}
      </Button>
    </template>
  </Dialog>
</template>
