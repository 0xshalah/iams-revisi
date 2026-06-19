// Central menu config for sidebar (desktop & mobile).
// Used by Sidebar.vue and MobileSidebar.vue so the role-based menu stays in sync.
export const navMenu = [
  { name: 'dashboard',   label: 'Dashboard',    icon: 'home',      roles: ['Administrator', 'Operator'], i18nKey: 'navigation.dashboard' },
  { name: 'assets',      label: 'Assets',       icon: 'box',       roles: ['Administrator', 'Operator'], i18nKey: 'navigation.assets' },
  { name: 'incidents',   label: 'Incidents',    icon: 'alert',     roles: ['Administrator', 'Operator'], i18nKey: 'navigation.incidents' },
  { name: 'problems',    label: 'Problems',     icon: 'puzzle',    roles: ['Administrator', 'Operator'], i18nKey: 'navigation.problems' },
  { name: 'requests',    label: 'Requests',     icon: 'clipboard', roles: ['Administrator', 'Operator'], i18nKey: 'navigation.requests' },
  { name: 'changes',     label: 'Changes',      icon: 'refresh',   roles: ['Administrator', 'Operator'], i18nKey: 'navigation.changes' },
  { name: 'master-data', label: 'Master Data',  icon: 'database',  roles: ['Administrator'],              i18nKey: 'navigation.masterData' },
  { name: 'users-roles', label: 'Users / Roles',icon: 'users',     roles: ['Administrator'],              i18nKey: 'navigation.usersRoles' },
  { name: 'audit-logs',  label: 'Audit Logs',   icon: 'history',   roles: ['Administrator'],              i18nKey: 'navigation.auditLogs' },
  { name: 'reports',     label: 'Reports',      icon: 'file-text', roles: ['Administrator'],              i18nKey: 'navigation.reports' },
]

export function menuForRole(role) {
  return navMenu.filter((m) => m.roles.includes(role))
}

export function labelForRoute(routeName) {
  return navMenu.find((m) => m.name === routeName)?.label || 'Dashboard'
}
