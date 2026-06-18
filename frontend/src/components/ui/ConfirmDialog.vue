<script setup>
import Dialog from './Dialog.vue'
import Button from './Button.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Konfirmasi tindakan' },
  description: { type: String, default: 'Apakah Anda yakin? Tindakan ini tidak dapat dibatalkan.' },
  confirmText: { type: String, default: 'Hapus' },
  cancelText: { type: String, default: 'Batal' },
  variant: { type: String, default: 'destructive' },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

function cancel() {
  emit('cancel')
  emit('update:modelValue', false)
}
function confirm() {
  emit('confirm')
}
</script>

<template>
  <Dialog
    :model-value="modelValue"
    :title="title"
    :description="description"
    size="sm"
    @update:model-value="(v) => $emit('update:modelValue', v)"
  >
    <slot />
    <template #footer>
      <Button variant="ghost" data-testid="confirm-dialog-cancel-btn" @click="cancel">{{ cancelText }}</Button>
      <Button :variant="variant" :loading="loading" data-testid="confirm-dialog-confirm-btn" @click="confirm">
        {{ confirmText }}
      </Button>
    </template>
  </Dialog>
</template>
