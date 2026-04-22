const DEFAULT_BASE_URL = process.env.BROWSER_OPERATOR_URL || 'http://127.0.0.1:8790'

export class BridgeClient {
  constructor(baseUrl = DEFAULT_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, '')
  }

  async request(path, options = {}) {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    })
    const text = await response.text()
    let body = null
    try {
      body = text ? JSON.parse(text) : null
    } catch {
      body = text
    }
    if (!response.ok) {
      throw new Error(`Bridge ${response.status} ${response.statusText}: ${JSON.stringify(body)}`)
    }
    return body
  }

  health() {
    return this.request('/health', { method: 'GET', headers: {} })
  }

  createSession(payload = {}) {
    return this.request('/sessions', { method: 'POST', body: JSON.stringify(payload) })
  }

  getSession(id) {
    return this.request(`/sessions/${id}`, { method: 'GET', headers: {} })
  }

  listSessions() {
    return this.request('/sessions', { method: 'GET', headers: {} })
  }

  deleteSession(id) {
    return this.request(`/sessions/${id}`, { method: 'DELETE', headers: {} })
  }

  open(id, payload) {
    return this.request(`/sessions/${id}/open`, { method: 'POST', body: JSON.stringify(payload) })
  }

  click(id, payload) {
    return this.request(`/sessions/${id}/click`, { method: 'POST', body: JSON.stringify(payload) })
  }

  type(id, payload) {
    return this.request(`/sessions/${id}/type`, { method: 'POST', body: JSON.stringify(payload) })
  }

  select(id, payload) {
    return this.request(`/sessions/${id}/select`, { method: 'POST', body: JSON.stringify(payload) })
  }

  waitFor(id, payload) {
    return this.request(`/sessions/${id}/wait-for`, { method: 'POST', body: JSON.stringify(payload) })
  }

  submit(id, payload) {
    return this.request(`/sessions/${id}/submit`, { method: 'POST', body: JSON.stringify(payload) })
  }

  text(id, payload) {
    return this.request(`/sessions/${id}/text`, { method: 'POST', body: JSON.stringify(payload) })
  }

  html(id, payload) {
    return this.request(`/sessions/${id}/html`, { method: 'POST', body: JSON.stringify(payload) })
  }

  screenshot(id, payload) {
    return this.request(`/sessions/${id}/screenshot`, { method: 'POST', body: JSON.stringify(payload) })
  }

  console(id) {
    return this.request(`/sessions/${id}/console`, { method: 'GET', headers: {} })
  }

  network(id) {
    return this.request(`/sessions/${id}/network`, { method: 'GET', headers: {} })
  }
}

export async function poll(assertion, { timeoutMs = 15000, intervalMs = 400, message = 'poll timeout' } = {}) {
  const started = Date.now()
  while (Date.now() - started < timeoutMs) {
    const value = await assertion()
    if (value) return value
    await new Promise((resolve) => setTimeout(resolve, intervalMs))
  }
  throw new Error(message)
}
