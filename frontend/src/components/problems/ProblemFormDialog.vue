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
  problem: { type: Object, default: null },
  users: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const ui = useUiStore()
const isCreate = computed(() => !props.problem)
const loading = ref(false)

const form = ref({
  title: '',
  root_cause_summary: '',
  priority: 'Medium',
  status: 'Open',
  owner_id: '',
})

watch(() => props.modelValue, (open) => {
  if (!open) return
  if (props.problem) {
    form.value = {
      title: props.problem.title || '',
      root_cause_summary: props.problem.root_cause_summary || props.problem.root_cause || '',
      priority: props.problem.priority || 'Medium',
      status: props.problem.status || 'Open',
      owner_id: props.problem.owner_id || '',
    }
  } else {
    form.value = { title: '', root_cause_summary: '', priority: 'Medium', status: 'Open', owner_id: '' }
  }
})

const priorityOpts = ['Critical', 'High', 'Medium', 'Low'].map((s) => ({ label: s, value: s }))
const statusOpts = ['Open', 'Investigating', 'Known Error', 'Closed'].map((s) => ({ label: s, value: s }))
const userOpts = computed(() => [{ label: '—', value: '' }, ...props.users.map((u) => ({ label: u.name, value: String(u.id) }))])

async function submit() {
  const payload = {
    title: form.value.title.trim(),
    root_cause_summary: form.value.root_cause_summary.trim() || undefined,
    priority: form.value.priority,
    status: form.value.status,
    owner_id: form.value.owner_id ? Number(form.value.owner_id) : undefined,
  }

  loading.value = true
  try {
    if (isCreate.value) {
      await apiClient.createProblem(payload)
    } else {
      await apiClient.updateProblem(props.problem.id, payload)
    }
    ui.pushToast({ title: 'Berhasil', description: isCreate.value ? 'Problem berhasil dibuat.' : 'Problem berhasil diperbarui.', variant: 'success' })
    emit('saved')
    emit('update:modelValue', false)
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Terjadi kesalahan saat menyimpan problem.', variant: 'destructive' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog
    :model-value="modelValue"
    :title="isCreate ? 'Problem Baru' : 'Edit Problem'"
    :description="isCreate ? 'Dokumentasikan root cause.' : `Perbarui ${problem?.code}.`"
    size="lg"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
      <div class="sm:col-span-2">
        <Label for="pf-title">Judul *</Label>
        <Input id="pf-title" v-model="form.title" placeholder="Ringkas akar masalah..." />
      </div>
      <div>
        <Label for="pf-priority">Priority *</Label>
        <Select id="pf-priority" v-model="form.priority" :options="priorityOpts" placeholder="Pilih priority" />
      </div>
      <div>
        <Label for="pf-status">Status</Label>
        <Select id="pf-status" v-model="form.status" :options="statusOpts" placeholder="Pilih status" />
      </div>
      <div class="sm:col-span-2">
        <Label for="pf-owner">Owner</Label>
        <Select id="pf-owner" v-model="form.owner_id" :options="userOpts" placeholder="Pilih owner" />
      </div>
      <div class="sm:col-span-2">
        <Label for="pf-root">Root Cause Summary</Label>
        <textarea id="pf-root" v-model="form.root_cause_summary" rows="3" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2" placeholder="Analisis akar masalah..." />
      </div>
    </div>

    <template #footer>
      <Button variant="ghost" @click="$emit('update:modelValue', false)">Batal</Button>
      <Button :loading="loading" :disabled="!form.title" @click="submit">
        {{ isCreate ? 'Simpan Problem' : 'Perbarui' }}
      </Button>
    </template>
  </Dialog>
</template>
