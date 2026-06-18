import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import './style.css'

import { useThemeStore } from './stores/theme'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)

// Initialize theme before mount to avoid FOUC
const themeStore = useThemeStore()
themeStore.init()

// Restore session from HttpOnly cookie via backend
const authStore = useAuthStore()
authStore.initSession().finally(() => {
  app.mount('#app')
})
