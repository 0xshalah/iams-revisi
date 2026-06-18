import { defineStore } from 'pinia'

let toastId = 0

export const useUiStore = defineStore('ui', {
  state: () => ({
    sidebarOpen: true, // desktop
    mobileSidebarOpen: false,
    toasts: [],
  }),
  actions: {
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
    },
    openMobileSidebar() { this.mobileSidebarOpen = true },
    closeMobileSidebar() { this.mobileSidebarOpen = false },
    pushToast({ title, description = '', variant = 'default', duration = 2500 }) {
      const id = ++toastId
      this.toasts.push({ id, title, description, variant })
      setTimeout(() => this.dismissToast(id), duration)
      return id
    },
    dismissToast(id) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },
  },
})
