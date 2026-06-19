import { defineStore } from 'pinia'
import apiClient from '@/services/apiClient'

/**
 * Auth store - integrated with Flask backend.
 *
 * - JWT is stored in an HttpOnly cookie by the backend; this store NEVER
 *   touches localStorage/sessionStorage for tokens.
 * - Only a non-sensitive "remember email" hint is persisted, if the user opts in.
 * - On startup the store attempts to restore the session via /api/auth/me.
 */
const REMEMBER_KEY = 'iams-remember'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    error: null,
    loading: false,
    initialized: false,
  }),
  getters: {
    isAuthenticated: (s) => !!s.user,
    role: (s) => s.user?.role_name ?? null,
    isAdmin: (s) => s.user?.role_name === 'Administrator',
  },
  actions: {
    async initSession() {
      try {
        const res = await apiClient.me()
        this.user = res.data?.user ?? null
      } catch (err) {
        this.user = null
        // 401 is expected for guests — do NOT redirect
      } finally {
        this.initialized = true
      }
    },

    async login({ email, password, remember = true }) {
      this.loading = true
      this.error = null
      try {
        const res = await apiClient.login({ email, password })
        this.user = res.data?.user ?? null
        if (this.user) {
          try {
            if (remember) {
              localStorage.setItem(REMEMBER_KEY, JSON.stringify({ email: this.user.email }))
            } else {
              localStorage.removeItem(REMEMBER_KEY)
            }
          } catch (_) { /* ignore */ }
        }
        return { ok: true }
      } catch (err) {
        this.error = err.data?.error || 'Email atau password tidak valid.'
        return { ok: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async logout() {
      // Clear local state immediately for instant UX. API call happens
      // in background — the important thing is clearing the cookie + state.
      const logoutPromise = apiClient.logout().catch(() => {})
      this.user = null
      this.error = null
      try { localStorage.removeItem(REMEMBER_KEY) } catch (_) { /* ignore */ }
      await logoutPromise
    },

    getRememberedEmail() {
      try {
        const raw = localStorage.getItem(REMEMBER_KEY)
        if (!raw) return ''
        const parsed = JSON.parse(raw)
        return parsed.email || ''
      } catch (_) { return '' }
    },
  },
})
