import { chromium, firefox, webkit } from 'playwright'
import { randomUUID } from 'node:crypto'

const BROWSERS = { chromium, firefox, webkit }
const MAX_LOG_ITEMS = 300

function pushBounded(list, item) {
  list.push(item)
  if (list.length > MAX_LOG_ITEMS) {
    list.shift()
  }
}

export class BrowserSessionManager {
  constructor() {
    this.sessions = new Map()
  }

  async create(options) {
    const id = randomUUID()
    const launcher = BROWSERS[options.browser]
    const browser = await launcher.launch({ headless: options.headless })
    const context = await browser.newContext({ viewport: options.viewport })
    const page = await context.newPage()
    const consoleLog = []
    const networkLog = []

    page.on('console', (message) => {
      pushBounded(consoleLog, {
        ts: new Date().toISOString(),
        type: message.type(),
        text: message.text(),
      })
    })

    page.on('requestfinished', async (request) => {
      const response = await request.response()
      pushBounded(networkLog, {
        ts: new Date().toISOString(),
        method: request.method(),
        url: request.url(),
        status: response?.status() ?? null,
        resourceType: request.resourceType(),
      })
    })

    const session = {
      id,
      browserName: options.browser,
      baseUrl: options.baseUrl ?? null,
      browser,
      context,
      page,
      consoleLog,
      networkLog,
      createdAt: new Date().toISOString(),
    }
    this.sessions.set(id, session)
    return this.serialize(session)
  }

  list() {
    return [...this.sessions.values()].map((session) => this.serialize(session))
  }

  get(id) {
    const session = this.sessions.get(id)
    if (!session) return null
    return session
  }

  serialize(session) {
    return {
      id: session.id,
      browserName: session.browserName,
      baseUrl: session.baseUrl,
      createdAt: session.createdAt,
      url: session.page.url(),
      consoleCount: session.consoleLog.length,
      networkCount: session.networkLog.length,
    }
  }

  snapshot(session) {
    return {
      id: session.id,
      browserName: session.browserName,
      baseUrl: session.baseUrl,
      createdAt: session.createdAt,
      url: session.page.url(),
      consoleCount: session.consoleLog.length,
      networkCount: session.networkLog.length,
    }
  }

  async open(session, payload) {
    await session.page.goto(payload.url, { waitUntil: payload.waitUntil, timeout: payload.timeoutMs })
    return { url: session.page.url() }
  }

  async click(session, payload) {
    await session.page.locator(payload.selector).click({ timeout: payload.timeoutMs })
    return { selector: payload.selector, ok: true }
  }

  async type(session, payload) {
    const locator = session.page.locator(payload.selector)
    if (payload.clear) {
      await locator.fill('', { timeout: payload.timeoutMs })
    }
    await locator.fill(payload.text, { timeout: payload.timeoutMs })
    return { selector: payload.selector, length: payload.text.length }
  }

  async select(session, payload) {
    await session.page.locator(payload.selector).selectOption(payload.value, { timeout: payload.timeoutMs })
    return { selector: payload.selector, value: payload.value }
  }

  async waitFor(session, payload) {
    await session.page.locator(payload.selector).waitFor({ state: payload.state, timeout: payload.timeoutMs })
    return { selector: payload.selector, state: payload.state }
  }

  async submit(session, payload) {
    await session.page.locator(payload.selector).evaluate(
      (form) => {
        form.requestSubmit()
      },
      null,
      { timeout: payload.timeoutMs }
    )
    return { selector: payload.selector, ok: true }
  }

  async text(session, payload) {
    const text = await session.page.locator(payload.selector).textContent({ timeout: payload.timeoutMs })
    return { selector: payload.selector, text }
  }

  async html(session, payload) {
    const html = await session.page.locator(payload.selector).innerHTML({ timeout: payload.timeoutMs })
    return { selector: payload.selector, html }
  }

  async screenshot(session, payload) {
    await session.page.screenshot({ path: payload.path, fullPage: payload.fullPage })
    return { path: payload.path }
  }

  getConsole(session) {
    return session.consoleLog
  }

  getNetwork(session) {
    return session.networkLog
  }

  async close(id) {
    const session = this.sessions.get(id)
    if (!session) return false
    await session.context.close()
    await session.browser.close()
    this.sessions.delete(id)
    return true
  }
}
