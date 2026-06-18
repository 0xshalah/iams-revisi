<script setup>
import { onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  size: { type: String, default: 'md' }, // sm | md | lg
  compact: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

function close() { emit('update:modelValue', false) }
function onKey(e) { if (e.key === 'Escape') close() }

watch(() => props.modelValue, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})

const sizeCls = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' }
</script>

<template>
  <teleport to="body">
    <transition name="dialog">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4">
        <div
          class="absolute inset-0 z-0 bg-black/50 backdrop-blur-[2px]"
          data-testid="dialog-backdrop"
          @click="close"
        />
        <div
          :class="['relative z-10 w-full card-surface shadow-xl animate-fade-in flex flex-col', sizeCls[size], compact ? 'max-h-[80vh]' : 'max-h-[85vh]']"
          role="dialog"
          aria-modal="true"
        >
          <div v-if="title || description" :class="['border-b border-border shrink-0', compact ? 'p-3' : 'p-5']">
            <h3 v-if="title" class="text-base font-semibold tracking-tight">{{ title }}</h3>
            <p v-if="description" :class="['text-sm text-muted-foreground', compact ? 'mt-0.5' : 'mt-1']">{{ description }}</p>
          </div>
          <div :class="['overflow-y-auto', compact ? 'p-3' : 'p-5']">
            <slot />
          </div>
          <div v-if="$slots.footer" :class="['border-t border-border flex items-center justify-end gap-2 bg-secondary/40 rounded-b-xl shrink-0', compact ? 'px-3 py-2.5' : 'px-5 py-4']">
            <slot name="footer" />
          </div>
          <button
            class="absolute top-3 right-3 h-8 w-8 inline-flex items-center justify-center rounded-md hover:bg-secondary text-muted-foreground"
            @click="close"
            aria-label="Close"
            data-testid="dialog-close-btn"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<style scoped>
.dialog-enter-active { transition: all 0.25s cubic-bezier(0.25, 0.1, 0.25, 1); }
.dialog-leave-active { transition: all 0.15s ease-in; }
.dialog-enter-from { opacity: 0; transform: scale(0.95) translateY(8px); }
.dialog-leave-to { opacity: 0; transform: scale(0.97) translateY(4px); }
</style>
