/**
 * apiClient - Flask backend integration.
 *
 * Security rules enforced by this client:
 * - credentials: 'include' is used on every request so the HttpOnly cookie
 *   containing the JWT is forwarded by the browser.
 * - JWT is never stored in localStorage/sessionStorage.
 * - CSRF token is fetched on first state-changing request and kept in memory.
 * - On 401 the user is redirected to the login page.
 * - On 403 CSRF mismatch the token is refreshed once and the request retried.
 */

const BASE = import.meta.env.VITE_API_BASE_URL || '/api'

let csrfToken = null

function isStateChanging(method) {
  return method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS'
}

async function fetchCsrfToken() {
  const res = await fetch(`${BASE}/auth/csrf-token`, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  })
  const body = await parseJson(res)
  csrfToken = body?.data?.csrf_token || body?.csrf_token || null
  return csrfToken
}

async function ensureCsrfToken() {
  if (csrfToken) return csrfToken
  return fetchCsrfToken()
}

function csrfHeaders() {
  return csrfToken ? { 'X-CSRF-Token': csrfToken } : {}
}

async function parseJson(res) {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return { error: text }
  }
}

function buildError(res, data) {
  const message = data?.error || `Request failed with status ${res.status}`
  const err = new Error(message)
  err.status = res.status
  err.data = data
  return err
}

function redirectToLogin() {
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname + window.location.search)}`
  }
}

async function parseResponse(res, opts = {}) {
  const payload = await parseJson(res)
  if (!res.ok) {
    if (res.status === 401 && !opts.noRedirect) {
      redirectToLogin()
    }
    throw buildError(res, payload)
  }
  // Backend wraps list/single resources in { data: ... }; auth endpoints return flat objects.
  const data = payload && typeof payload === 'object' && 'data' in payload ? payload.data : payload
  return { data, status: res.status }
}

async function request(method, path, body = null, options = {}) {
  const headers = {
    Accept: 'application/json',
    ...(body !== null ? { 'Content-Type': 'application/json' } : {}),
    ...options.headers,
  }

  if (isStateChanging(method)) {
    await ensureCsrfToken()
    Object.assign(headers, csrfHeaders())
  }

  const fetchOptions = {
    method,
    credentials: 'include',
    headers,
  }
  if (body !== null) {
    fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body)
  }

  const res = await fetch(`${BASE}${path}`, fetchOptions)

  // If CSRF was rejected, refresh token once and retry.
  if (res.status === 403 && isStateChanging(method)) {
    const data = await parseJson(res)
    const msg = (data?.error || '').toLowerCase()
    if (msg.includes('csrf')) {
      csrfToken = null
      await fetchCsrfToken()
      Object.assign(headers, csrfHeaders())
      const retryRes = await fetch(`${BASE}${path}`, fetchOptions)
      return parseResponse(retryRes, options)
    }
  }
  return parseResponse(res, options)

}

const get = (path, opts = {}) => request('GET', path, null, opts)
const post = (path, body, opts = {}) => request('POST', path, body, opts)
const put = (path, body, opts = {}) => request('PUT', path, body, opts)
const patch = (path, body, opts = {}) => request('PATCH', path, body, opts)
const del = (path, opts = {}) => request('DELETE', path, null, opts)

export const apiClient = {
  base: BASE,

  // Auth
  getCsrfToken: () => get('/auth/csrf-token'),
  login: (credentials) => post('/auth/login', credentials),
  logout: () => post('/auth/logout', {}),
  me: () => get('/auth/me', { noRedirect: true }),

  // Users / Roles (admin)
  listUsers: () => get('/users?per_page=1000'),
  createUser: (payload) => post('/users', payload),
  getUser: (id) => get(`/users/${id}`),
  updateUser: (id, payload) => put(`/users/${id}`, payload),
  deleteUser: (id) => del(`/users/${id}`),

  listRoles: () => get('/roles'),
  createRole: (payload) => post('/roles', payload),
  updateRole: (id, payload) => put(`/roles/${id}`, payload),
  deleteRole: (id) => del(`/roles/${id}`),

  // Assets
  listAssets: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/assets${qs ? `?${qs}` : ''}`)
  },
  createAsset: (payload) => post('/assets', payload),
  getAsset: (id) => get(`/assets/${id}`),
  updateAsset: (id, payload) => put(`/assets/${id}`, payload),
  deleteAsset: (id) => del(`/assets/${id}`),
  getNetworkDetails: (id) => get(`/assets/${id}/network-details`),
  updateNetworkDetails: (id, payload) => put(`/assets/${id}/network-details`, payload),
  getCredentialStatus: (id) => get(`/assets/${id}/credential-status`),
  listCredentials: (id) => get(`/assets/${id}/credentials`),
  createCredential: (id, payload) => post(`/assets/${id}/credentials`, payload),
  updateCredential: (id, cid, payload) => put(`/assets/${id}/credentials/${cid}`, payload),
  deleteCredential: (id, cid) => del(`/assets/${id}/credentials/${cid}`),
  revealCredential: (id, cid) => get(`/assets/${id}/credentials/${cid}/reveal`),

  // Incidents
  listIncidents: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/incidents${qs ? `?${qs}` : ''}`)
  },
  createIncident: (payload) => post('/incidents', payload),
  getIncident: (id) => get(`/incidents/${id}`),
  updateIncident: (id, payload) => put(`/incidents/${id}`, payload),
  deleteIncident: (id) => del(`/incidents/${id}`),

  // Problems
  listProblems: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/problems${qs ? `?${qs}` : ''}`)
  },
  createProblem: (payload) => post('/problems', payload),
  getProblem: (id) => get(`/problems/${id}`),
  updateProblem: (id, payload) => put(`/problems/${id}`, payload),
  deleteProblem: (id) => del(`/problems/${id}`),

  // Audit logs
  listAuditLogs: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 100 }).toString()
    return get(`/audit-logs${qs ? `?${qs}` : ''}`)
  },

  // Master data
  listDepartments: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/departments${qs ? `?${qs}` : ''}`)
  },
  createDepartment: (payload) => post('/departments', payload),
  updateDepartment: (id, payload) => put(`/departments/${id}`, payload),
  deleteDepartment: (id) => del(`/departments/${id}`),

  listLocations: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/locations${qs ? `?${qs}` : ''}`)
  },
  createLocation: (payload) => post('/locations', payload),
  updateLocation: (id, payload) => put(`/locations/${id}`, payload),
  deleteLocation: (id) => del(`/locations/${id}`),

  listCategories: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/categories${qs ? `?${qs}` : ''}`)
  },
  createCategory: (payload) => post('/categories', payload),
  updateCategory: (id, payload) => put(`/categories/${id}`, payload),
  deleteCategory: (id) => del(`/categories/${id}`),

  listBrands: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/brands${qs ? `?${qs}` : ''}`)
  },
  createBrand: (payload) => post('/brands', payload),
  updateBrand: (id, payload) => put(`/brands/${id}`, payload),
  deleteBrand: (id) => del(`/brands/${id}`),

  listModels: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/models${qs ? `?${qs}` : ''}`)
  },
  createModel: (payload) => post('/models', payload),
  updateModel: (id, payload) => put(`/models/${id}`, payload),
  deleteModel: (id) => del(`/models/${id}`),

  // Requests
  listRequests: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/requests${qs ? `?${qs}` : ''}`)
  },
  getRequest: (id) => get(`/requests/${id}`),
  createRequest: (payload) => post('/requests', payload),
  updateRequest: (id, payload) => put(`/requests/${id}`, payload),
  deleteRequest: (id) => del(`/requests/${id}`),

  // Changes
  listChanges: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 1000 }).toString()
    return get(`/changes${qs ? `?${qs}` : ''}`)
  },
  getChange: (id) => get(`/changes/${id}`),
  createChange: (payload) => post('/changes', payload),
  updateChange: (id, payload) => put(`/changes/${id}`, payload),
  deleteChange: (id) => del(`/changes/${id}`),
  approveChange: (id, payload) => post(`/changes/${id}/approve`, payload || {}),
  rejectChange: (id, payload) => post(`/changes/${id}/reject`, payload || {}),

  // Reports
  fullAssetReport: () => get('/reports/assets/full'),
  assetStatusSummary: () => get('/reports/assets/status-summary'),
  assetsByPo: (poNumber) => get(`/reports/assets/by-po?po_number=${encodeURIComponent(poNumber)}`),
  assetsWarrantyExpiring: (months = 3) => get(`/reports/assets/warranty-expiring?months=${months}`),
}

export default apiClient
