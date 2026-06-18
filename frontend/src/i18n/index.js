import { createI18n } from 'vue-i18n'
import id from './locales/id.js'
import en from './locales/en.js'

function getInitialLocale() {
  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    try { const v = localStorage.getItem('iams-locale'); if (v) return v } catch (_) { /* */ }
  }
  return 'id'
}

const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(),
  fallbackLocale: 'id',
  messages: { id, en },
})

export default i18n
