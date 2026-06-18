import { defineStore } from 'pinia'
import i18n from '@/i18n'

const LOCALE_KEY = 'iams-locale'

export const useLocaleStore = defineStore('locale', {
  state: () => ({
    available: ['id', 'en'],
  }),
  getters: {
    current: () => i18n.global.locale.value,
    currentLabel() {
      const labels = { id: 'Bahasa Indonesia', en: 'English' }
      return labels[i18n.global.locale.value] || i18n.global.locale.value
    },
  },
  actions: {
    setLocale(code) {
      if (this.available.includes(code)) {
        i18n.global.locale.value = code
        try { localStorage.setItem(LOCALE_KEY, code) } catch (_) { /* ignore */ }
      }
    },
  },
})
