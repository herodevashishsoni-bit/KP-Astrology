let token = localStorage.getItem('kp_token') || ''

export function setToken(t) {
  token = t || ''
  if (t) localStorage.setItem('kp_token', t)
  else localStorage.removeItem('kp_token')
}
export const hasToken = () => !!token

async function call(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401) {
    setToken('')
    window.dispatchEvent(new Event('kp-logout'))
  }
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : res.statusText)
  return data
}

export const api = {
  status: () => call('GET', '/api/auth/status'),
  setup: (u, p) => call('POST', '/api/auth/setup', { username: u, password: p }),
  login: (u, p) => call('POST', '/api/auth/login', { username: u, password: p }),
  charts: () => call('GET', '/api/charts'),
  createChart: (c) => call('POST', '/api/charts', c),
  updateChart: (id, c) => call('PUT', `/api/charts/${id}`, c),
  deleteChart: (id) => call('DELETE', `/api/charts/${id}`),
  addEvent: (id, e) => call('POST', `/api/charts/${id}/events`, e),
  deleteEvent: (id, eid) => call('DELETE', `/api/charts/${id}/events/${eid}`),
  matters: () => call('GET', '/api/matters'),
  chart: (id, aya) => call('GET', `/api/charts/${id}/chart?ayanamsa=${aya}`),
  dasa: (id, aya, depth) => call('GET', `/api/charts/${id}/dasa?ayanamsa=${aya}&depth=${depth}`),
  bio: (id, aya, aspects = true) => call('GET', `/api/charts/${id}/bio?ayanamsa=${aya}&aspects=${aspects}`),
  ask: (id, matter, lat, lon, aya, years) => call('GET', `/api/charts/${id}/ask?matter=${matter}&lat=${lat}&lon=${lon}&ayanamsa=${aya}&years=${years}`),
  rectify: (body) => call('POST', '/api/rectify', body),
  horary: (body) => call('POST', '/api/horary', body),
  rp: (lat, lon, aya) => call('GET', `/api/rp?lat=${lat}&lon=${lon}&ayanamsa=${aya}`),
}
