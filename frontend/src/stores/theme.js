import { defineStore } from 'pinia'

const THEME_KEY = 'iams-theme'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    /** @type {'light'|'dark'} */
    mode: 'light',
    resolved: 'light',
  }),
  actions: {
    init() {
      const saved = localStorage.getItem(THEME_KEY)
      this.mode = ['light', 'dark'].includes(saved) ? saved : 'light'
      this.apply()
    },
    setMode(mode, clickX, clickY) {
      this.mode = mode
      localStorage.setItem(THEME_KEY, mode)
      this.transition(() => this.apply(), clickX, clickY)
    },
    apply() {
      const isDark = this.mode === 'dark'
      this.resolved = isDark ? 'dark' : 'light'
      document.documentElement.classList.toggle('dark', isDark)
    },
    transition(update, cx, cy) {
      if (!document.startViewTransition) { update(); return }
      const isDark = this.resolved === 'dark'
      const x = cx ?? 0
      const y = cy ?? 0
      const maxRadius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y))
      const expanded = `circle(${maxRadius}px at ${x}px ${y}px)`
      const collapsed = `circle(0px at ${x}px ${y}px)`

      if (isDark) {
        document.documentElement.dataset.transitionMode = 'sunrise'
        const t = document.startViewTransition(() => update())
        t.ready.then(() => {
          document.documentElement.animate(
            { clipPath: [collapsed, expanded] },
            { duration: 500, easing: 'ease-in', pseudoElement: '::view-transition-new(root)' }
          )
        })
        t.finished.then(() => { delete document.documentElement.dataset.transitionMode })
      } else {
        delete document.documentElement.dataset.transitionMode
        const t = document.startViewTransition(() => update())
        t.ready.then(() => {
          document.documentElement.animate(
            { clipPath: [expanded, collapsed] },
            { duration: 400, easing: 'ease-out', fill: 'forwards', pseudoElement: '::view-transition-old(root)' }
          )
        })
      }
    },
  },
})
