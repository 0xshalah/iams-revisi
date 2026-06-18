import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const DashboardLayout = () => import('@/layouts/DashboardLayout.vue')

const routes = [
  {
    path: '/',
    name: 'welcome',
    component: () => import('@/pages/WelcomePage.vue'),
    meta: { public: true },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { public: true },
  },
  {
    path: '/dashboard',
    component: DashboardLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue') },
      { path: 'assets', name: 'assets', component: () => import('@/pages/AssetsPage.vue') },
      { path: 'incidents', name: 'incidents', component: () => import('@/pages/IncidentsPage.vue') },
      { path: 'problems', name: 'problems', component: () => import('@/pages/ProblemsPage.vue') },
      { path: 'requests', name: 'requests', component: () => import('@/pages/RequestsPage.vue') },
      { path: 'changes', name: 'changes', component: () => import('@/pages/ChangesPage.vue') },
      {
        path: 'master-data',
        name: 'master-data',
        component: () => import('@/pages/MasterDataPage.vue'),
        meta: { roles: ['Administrator'] },
      },
      {
        path: 'users-roles',
        name: 'users-roles',
        component: () => import('@/pages/UsersRolesPage.vue'),
        meta: { roles: ['Administrator'] },
      },
      {
        path: 'audit-logs',
        name: 'audit-logs',
        component: () => import('@/pages/AuditLogsPage.vue'),
        meta: { roles: ['Administrator'] },
      },
      {
        path: 'reports',
        name: 'reports',
        component: () => import('@/pages/ReportsPage.vue'),
        meta: { roles: ['Administrator'] },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/pages/NotFoundPage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() { return { top: 0 } },
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Wait until the session has been initialized from the backend
  if (!auth.initialized) {
    await auth.initSession()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { next: to.fullPath } }
  }
  if (to.name === 'welcome' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    if (!auth.user || !to.meta.roles.includes(auth.user.role_name)) {
      return { name: 'dashboard' }
    }
  }
})

export default router
