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
  } else {
    form.value = {
      asset_tag: '', serial_number: '', po_number: '', model_id: '', location_id: '', user_id: '',
      status: 'Available', purchase_date: '', warranty_months: '', os_license: '',
      ip_address: '', mac_address: '', hostname: '', vlan: '', credential: '',
    }
  }
})

const statusOpts = ['Active', 'Available', 'Repair', 'Disposed'].map((s) => ({ label: s, value: s }))
const locationOpts = computed(() => props.locations.map((l) => ({ label: l.name, value: String(l.id) })))
const modelOpts = computed(() => props.models.map((m) => ({ label: `${m.brand_name} ${m.name}`, value: String(m.id) })))
const userOpts = computed(() => [{ label: 'IT Inventory / Server', value: '' }, ...props.users.map((u) => ({ label: u.name, value: String(u.id) }))])

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

    ui.pushToast({ title: 'Berhasil', description: isCreate.value ? 'Aset berhasil ditambahkan.' : 'Aset berhasil diperbarui.', variant: 'success' })
    emit('saved')
    emit('update:modelValue', false)
  } catch (err) {
    ui.pushToast({ title: 'Gagal', description: err.data?.error || 'Terjadi kesalahan saat menyimpan aset.', variant: 'destructive' })
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

      <div class="sm:col-span-2">
        <Label for="af-credential" class="mb-0.5 text-xs">{{ isCreate ? 'Credential (simpan terenkripsi)' : 'Update Credential' }}</Label>
        <Input id="af-credential" v-model="form.credential" type="password" placeholder="Biarkan kosong jika tidak diubah" autocomplete="off" class="h-8 text-[13px] px-2.5" />
        <p class="text-[11px] text-muted-foreground mt-0.5">Credential disimpan terenkripsi di backend dan tidak ditampilkan kembali.</p>
      </div>
    </div>

    <template #footer>
      <Button variant="ghost" size="sm" @click="$emit('update:modelValue', false)">Batal</Button>
      <Button size="sm" :loading="loading" :disabled="!form.asset_tag || !form.serial_number || !form.model_id || !form.location_id" @click="submit">
        {{ isCreate ? 'Simpan Aset' : 'Perbarui' }}
      </Button>
    </template>
  </Dialog>
</template>
