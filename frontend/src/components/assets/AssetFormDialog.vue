<script setup>
import { ref, watch, computed } from 'vue'
import apiClient from '@/services/apiClient'
import { useUiStore } from '@/stores/ui'
import { useI18n } from 'vue-i18n'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'

const { t } = useI18n()
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  asset: { type: Object, default: null },
  locations: { type: Array, default: () => [] },
  models: { type: Array, default: () => [] },
  users: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const ui = useUiStore()
const isCreate = computed(() => !props.asset)
const loading = ref(false)

const form = ref({
  asset_tag: '',
  serial_number: '',
  po_number: '',
  model_id: '',
  location_id: '',
  user_id: '',
  status: 'Available',
  purchase_date: '',
  warranty_months: '',
  os_license: '',
  ip_address: '',
  mac_address: '',
  hostname: '',
  vlan: '',
  credential: '',
})

watch(() => props.modelValue, (open) => {
  if (!open) return
  if (props.asset) {
    form.value = {
      asset_tag: props.asset.asset_tag || '',
      serial_number: props.asset.serial_number || '',
      po_number: props.asset.po_number || '',
      model_id: props.asset.model_id || '',
      location_id: props.asset.location_id || '',
      user_id: props.asset.user_id || '',
      status: props.asset.status || 'Active',
      purchase_date: props.asset.purchase_date || '',
      warranty_months: props.asset.warranty_months || '',
      os_license: props.asset.os_license || '',
      ip_address: props.asset.ip_address || '',
      mac_address: props.asset.mac_address || '',
      hostname: props.asset.hostname || '',
      vlan: props.asset.vlan || '',
      credential: '',
    }
    fetchCredentials()
  } else {
    form.value = {
      asset_tag: '', serial_number: '', po_number: '', model_id: '', location_id: '', user_id: '',
      status: 'Available', purchase_date: '', warranty_months: '', os_license: '',
      ip_address: '', mac_address: '', hostname: '', vlan: '', credential: '',
    }
    credentials.value = []
  }
})

const statusOpts = ['Active', 'Available', 'Repair', 'Disposed'].map((s) => ({ label: s, value: s }))
const locationOpts = computed(() => props.locations.map((l) => ({ label: l.name, value: String(l.id) })))
const modelOpts = computed(() => props.models.map((m) => ({ label: `${m.brand_name} ${m.name}`, value: String(m.id) })))
const userOpts = computed(() => [{ label: 'IT Inventory / Server', value: '' }, ...props.users.map((u) => ({ label: u.name, value: String(u.id) }))])

const credentials = ref([])
const credForm = ref({ credential_type: 'SSH', username: '', password: '', notes: '' })
const credReveal = ref({})
const editingCredId = ref(null)
const credTypeOpts = ['SSH', 'Web Console', 'SNMP', 'Telnet', 'RDP', 'API Key', 'Other'].map(s => ({ label: s, value: s }))

async function fetchCredentials() {
  if (!props.asset?.id) return
  try { credentials.value = (await apiClient.listCredentials(props.asset.id)).data?.data || [] }
  catch (_) { credentials.value = [] }
}

async function addOrUpdateCredential() {
  if (!props.asset?.id) return
  try {
    if (editingCredId.value) {
      const payload = { credential_type: credForm.value.credential_type, username: credForm.value.username || undefined, notes: credForm.value.notes || undefined }
      if (credForm.value.password.trim()) payload.password = credForm.value.password.trim()
      await apiClient.updateCredential(props.asset.id, editingCredId.value, payload)
      ui.pushToast({ title: t('common.success'), description: 'Kredensial diperbarui.', variant: 'success' })
    } else {
      if (!credForm.value.password.trim()) return
      await apiClient.createCredential(props.asset.id, credForm.value)
      ui.pushToast({ title: t('common.success'), description: 'Kredensial ditambahkan.', variant: 'success' })
    }
    credForm.value = { credential_type: 'SSH', username: '', password: '', notes: '' }
    editingCredId.value = null
    fetchCredentials()
  } catch (err) { ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' }) }
}

function editCredential(cred) {
  credForm.value = { credential_type: cred.credential_type, username: cred.username || '', password: '', notes: cred.notes || '' }
  editingCredId.value = cred.id
}

function cancelEdit() {
  credForm.value = { credential_type: 'SSH', username: '', password: '', notes: '' }
  editingCredId.value = null
}

async function revealCredential(credId) {
  try {
    const r = await apiClient.revealCredential(props.asset.id, credId)
    credReveal.value[credId] = r.data?.data?.password || '***'
    ui.pushToast({ title: t('common.success'), description: 'Password ditampilkan (tercatat di audit log).', variant: 'info' })
    setTimeout(() => { delete credReveal.value[credId] }, 5000)
  } catch (err) { ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' }) }
}

async function deleteCredential(credId) {
  try {
    await apiClient.deleteCredential(props.asset.id, credId)
    ui.pushToast({ title: t('common.success'), description: 'Kredensial dihapus.', variant: 'success' })
    fetchCredentials()
  } catch (err) { ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' }) }
}

async function submit() {
  const payload = {
    asset_tag: form.value.asset_tag.trim(),
    serial_number: form.value.serial_number.trim() || undefined,
    po_number: form.value.po_number.trim() || undefined,
    model_id: form.value.model_id ? Number(form.value.model_id) : undefined,
    location_id: form.value.location_id ? Number(form.value.location_id) : undefined,
    user_id: form.value.user_id ? Number(form.value.user_id) : undefined,
    status: form.value.status,
    purchase_date: form.value.purchase_date || undefined,
    warranty_months: form.value.warranty_months ? Number(form.value.warranty_months) : undefined,
    os_license: form.value.os_license.trim() || undefined,
  }

  const network = {}
  if (form.value.ip_address.trim()) network.ip_address = form.value.ip_address.trim()
  if (form.value.mac_address.trim()) network.mac_address = form.value.mac_address.trim()
  if (form.value.hostname.trim()) network.hostname = form.value.hostname.trim()
  if (form.value.vlan.trim()) network.vlan = form.value.vlan.trim()
  if (Object.keys(network).length) payload.network_detail = network

  const credential = form.value.credential.trim()

  loading.value = true
  try {
    let assetId = props.asset?.id
    if (isCreate.value) {
      const created = await apiClient.createAsset(payload)
      assetId = created.data?.id
    } else {
      await apiClient.updateAsset(assetId, payload)
    }

    if (credential && assetId) {
      await apiClient.updateCredential(assetId, { credential })
    }

    ui.pushToast({ title: t('common.success'), description: isCreate.value ? `Aset ${t('toast.created')}.` : `Aset ${t('toast.updated')}.`, variant: 'success' })
    emit('saved')
    emit('update:modelValue', false)
  } catch (err) {
    ui.pushToast({ title: t('common.failed'), description: err.data?.error || t('toast.failed'), variant: 'destructive' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog
    :model-value="modelValue"
    :title="isCreate ? 'Tambah Aset' : 'Edit Aset'"
    :description="isCreate ? 'Isi informasi aset baru.' : `Perbarui data ${asset?.asset_tag}.`"
    size="lg"
    compact
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[13px]">
      <div>
        <Label for="af-tag" class="mb-0.5 text-xs">Asset Tag *</Label>
        <Input id="af-tag" v-model="form.asset_tag" placeholder="AST-..." class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-serial" class="mb-0.5 text-xs">Serial Number *</Label>
        <Input id="af-serial" v-model="form.serial_number" placeholder="SN..." class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-model" class="mb-0.5 text-xs">Model *</Label>
        <Select id="af-model" v-model="form.model_id" :options="modelOpts" placeholder="Pilih model" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-location" class="mb-0.5 text-xs">Lokasi *</Label>
        <Select id="af-location" v-model="form.location_id" :options="locationOpts" placeholder="Pilih lokasi" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-po" class="mb-0.5 text-xs">PO Number</Label>
        <Input id="af-po" v-model="form.po_number" placeholder="PO/..." class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-status" class="mb-0.5 text-xs">Status</Label>
        <Select id="af-status" v-model="form.status" :options="statusOpts" placeholder="Pilih status" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-user" class="mb-0.5 text-xs">Pengguna</Label>
        <Select id="af-user" v-model="form.user_id" :options="userOpts" placeholder="Pilih pengguna" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-purchase" class="mb-0.5 text-xs">Tanggal Pembelian</Label>
        <Input id="af-purchase" v-model="form.purchase_date" type="date" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-warranty" class="mb-0.5 text-xs">Garansi (bulan)</Label>
        <Input id="af-warranty" v-model="form.warranty_months" type="number" min="0" placeholder="36" class="h-8 text-[13px] px-2.5" />
      </div>
      <div>
        <Label for="af-os" class="mb-0.5 text-xs">OS/License</Label>
        <Input id="af-os" v-model="form.os_license" placeholder="-" class="h-8 text-[13px] px-2.5" />
      </div>

      <div class="sm:col-span-2 border-t border-border pt-2 mt-0.5">
        <p class="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">Detail Jaringan</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div>
            <Label for="af-ip" class="mb-0.5 text-xs">IP Address</Label>
            <Input id="af-ip" v-model="form.ip_address" placeholder="10.x.x.x" class="h-8 text-[13px] px-2.5" />
          </div>
          <div>
            <Label for="af-mac" class="mb-0.5 text-xs">MAC Address</Label>
            <Input id="af-mac" v-model="form.mac_address" placeholder="00:00:00:00:00:00" class="h-8 text-[13px] px-2.5" />
          </div>
          <div>
            <Label for="af-hostname" class="mb-0.5 text-xs">Hostname</Label>
            <Input id="af-hostname" v-model="form.hostname" placeholder="hostname" class="h-8 text-[13px] px-2.5" />
          </div>
          <div>
            <Label for="af-vlan" class="mb-0.5 text-xs">VLAN</Label>
            <Input id="af-vlan" v-model="form.vlan" placeholder="VLAN" class="h-8 text-[13px] px-2.5" />
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <!-- Credentials — pinned above buttons, always visible -->
      <div v-if="!isCreate" class="w-full text-left border-t border-border pt-2 pb-1 mb-1">
        <p class="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">Kredensial Perangkat</p>
        <div v-if="credentials.length" class="space-y-1 mb-1.5">
          <div v-for="cred in credentials" :key="cred.id" class="flex items-center gap-2 rounded-md border border-border bg-muted/30 px-2 py-1">
            <span class="text-[11px] font-medium">{{ cred.credential_type }}</span>
            <span class="text-[10px] text-muted-foreground">{{ cred.username || '-' }}</span>
            <span class="text-[11px] font-mono text-muted-foreground">••••••••</span>
            <input v-if="credReveal[cred.id]" :value="credReveal[cred.id]" readonly class="text-[11px] font-mono bg-transparent w-20" />
            <span class="flex-1"></span>
            <Button variant="ghost" size="xs" class="h-6 w-6 p-0 shrink-0" @click="revealCredential(cred.id)" title="Lihat">👁</Button>
            <Button variant="ghost" size="xs" class="h-6 w-6 p-0 shrink-0" @click="editCredential(cred)" title="Edit">✎</Button>
            <Button variant="ghost" size="xs" class="h-6 w-6 p-0 shrink-0 text-destructive" @click="deleteCredential(cred.id)" title="Hapus">✕</Button>
          </div>
        </div>
        <div class="grid grid-cols-4 sm:grid-cols-5 gap-1">
          <Select v-model="credForm.credential_type" :options="credTypeOpts" class="h-7 text-[11px] px-1.5" />
          <Input v-model="credForm.username" placeholder="User" class="h-7 text-[11px] px-1.5" />
          <Input v-model="credForm.password" type="password" placeholder="Pass" autocomplete="off" class="h-7 text-[11px] px-1.5 col-span-2 sm:col-span-2" />
          <Button size="xs" class="h-7 text-[10px] sm:col-span-1" :disabled="!credForm.password.trim()" @click="addOrUpdateCredential">{{ editingCredId ? 'Update' : '+ Tambah' }}</Button>
        </div>
      </div>
      <div class="flex items-center justify-end gap-2 w-full">
        <Button variant="ghost" size="sm" @click="$emit('update:modelValue', false)">Batal</Button>
        <Button size="sm" :loading="loading" :disabled="!form.asset_tag || !form.serial_number || !form.model_id || !form.location_id" @click="submit">
          {{ isCreate ? 'Simpan Aset' : 'Perbarui' }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>
