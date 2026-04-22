import { mkdir, writeFile } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import path from 'node:path'

import { BridgeClient, poll } from './bridge-client.js'

const APP_URL = process.env.PROJECT01_URL || 'http://localhost:8081'
const AUTO_IMPORT_VISUALIZER = process.env.BROWSER_SMOKE_AUTO_IMPORT !== '0'
const client = new BridgeClient()
const artifactsDir = path.resolve('artifacts', 'project01-smoke')

async function ensureDir(dir) {
  await mkdir(dir, { recursive: true })
}

function uniqueSuffix() {
  return `${Date.now()}-${Math.floor(Math.random() * 100000)}`
}

async function ensurePage(sessionId, expectedSelector, timeoutMs = 15000) {
  await client.waitFor(sessionId, { selector: expectedSelector, state: 'visible', timeoutMs })
}

async function saveScenarioArtifacts(sessionId, scenarioDir, prefix) {
  await ensureDir(scenarioDir)
  const screenshotPath = path.join(scenarioDir, `${prefix}.png`)
  try {
    await client.screenshot(sessionId, { path: screenshotPath, fullPage: true })
  } catch {
    // best effort
  }
  const consoleLog = await client.console(sessionId).catch(() => [])
  const networkLog = await client.network(sessionId).catch(() => [])
  const consolePath = path.join(scenarioDir, `${prefix}.console.json`)
  const networkPath = path.join(scenarioDir, `${prefix}.network.json`)
  await writeFile(consolePath, JSON.stringify(consoleLog, null, 2), 'utf-8')
  await writeFile(networkPath, JSON.stringify(networkLog, null, 2), 'utf-8')
  return { screenshotPath, consolePath, networkPath, consoleLog, networkLog }
}

async function saveFailureArtifacts(sessionId, scenarioDir) {
  const artifacts = await saveScenarioArtifacts(sessionId, scenarioDir, 'failure')
  return { screenshotPath: artifacts.screenshotPath, consolePath: artifacts.consolePath, networkPath: artifacts.networkPath }
}

async function saveSuccessArtifacts(sessionId, scenarioDir) {
  const artifacts = await saveScenarioArtifacts(sessionId, scenarioDir, 'success')
  return artifacts
}

async function recordStep(report, name, action) {
  const startedAt = new Date().toISOString()
  try {
    const details = await action()
    report.steps.push({ name, status: 'passed', startedAt, finishedAt: new Date().toISOString(), details })
    return details
  } catch (error) {
    report.steps.push({ name, status: 'failed', startedAt, finishedAt: new Date().toISOString(), error: error.message })
    throw error
  }
}

async function scenarioAuthAdmin() {
  const scenarioDir = path.join(artifactsDir, 'auth-admin')
  const report = { name: 'auth-admin', startedAt: new Date().toISOString(), steps: [] }
  const session = await client.createSession({ browser: 'chromium', headless: true, baseUrl: APP_URL })
  try {
    await recordStep(report, 'open-login-page', async () => client.open(session.id, { url: `${APP_URL}/`, waitUntil: 'load' }))
    await recordStep(report, 'wait-login-form', async () => ensurePage(session.id, 'form#login-form button[type="submit"]'))
    await recordStep(report, 'type-admin-email', async () => client.type(session.id, { selector: 'form#login-form input[name="email"]', text: 'admin@local.dev' }))
    await recordStep(report, 'type-admin-password', async () => client.type(session.id, { selector: 'form#login-form input[name="password"]', text: 'admin12345' }))
    await recordStep(report, 'submit-login', async () => client.click(session.id, { selector: 'form#login-form button[type="submit"]' }))
    await recordStep(report, 'wait-admin-heading', async () => ensurePage(session.id, 'h1'))
    const heading = await recordStep(report, 'assert-admin-page', async () => poll(async () => {
      const { text } = await client.text(session.id, { selector: 'h1' })
      return text?.includes('Admin Workspace') ? text : null
    }, { message: 'Admin page did not load' }))
    const successArtifacts = await saveSuccessArtifacts(session.id, scenarioDir)
    report.finishedAt = new Date().toISOString()
    report.status = 'passed'
    report.artifacts = {
      successScreenshot: successArtifacts.screenshotPath,
      console: successArtifacts.consolePath,
      network: successArtifacts.networkPath,
    }
    report.result = { sessionId: session.id, heading }
    return report
  } catch (error) {
    const artifacts = await saveFailureArtifacts(session.id, scenarioDir)
    report.finishedAt = new Date().toISOString()
    report.status = 'failed'
    report.error = error.message
    report.artifacts = artifacts
    return report
  } finally {
    await client.deleteSession(session.id).catch(() => {})
  }
}

async function scenarioUserTaskAndChat() {
  const scenarioDir = path.join(artifactsDir, 'user-task-chat')
  const report = { name: 'user-task-chat', startedAt: new Date().toISOString(), steps: [] }
  const suffix = uniqueSuffix()
  const user = {
    username: `ui-user-${suffix}`,
    email: `ui-user-${suffix}@example.com`,
    password: 'demo12345',
    fullName: `UI User ${suffix}`,
    taskTitle: `Smoke Task ${suffix}`,
    chatTopic: `Smoke Chat ${suffix}`,
    chatMessage: `Smoke message ${suffix}`,
  }

  const session = await client.createSession({ browser: 'chromium', headless: true, baseUrl: APP_URL })
  try {
    await recordStep(report, 'open-register-page', async () => client.open(session.id, { url: `${APP_URL}/`, waitUntil: 'load' }))
    await recordStep(report, 'wait-register-form', async () => ensurePage(session.id, 'form#register-form button[type="submit"]'))
    await recordStep(report, 'type-username', async () => client.type(session.id, { selector: 'form#register-form input[name="username"]', text: user.username }))
    await recordStep(report, 'type-email', async () => client.type(session.id, { selector: 'form#register-form input[name="email"]', text: user.email }))
    await recordStep(report, 'type-password', async () => client.type(session.id, { selector: 'form#register-form input[name="password"]', text: user.password }))
    await recordStep(report, 'type-fullname', async () => client.type(session.id, { selector: 'form#register-form input[name="fullName"]', text: user.fullName }))
    await recordStep(report, 'submit-register', async () => client.click(session.id, { selector: 'form#register-form button[type="submit"]' }))
    await recordStep(report, 'wait-user-heading', async () => ensurePage(session.id, 'h1'))
    await recordStep(report, 'assert-user-page', async () => poll(async () => {
      const { text } = await client.text(session.id, { selector: 'h1' })
      return text?.includes('User Workspace') ? text : null
    }, { message: 'User page did not load' }))

    await recordStep(report, 'type-task-title', async () => client.type(session.id, { selector: 'form#task-form input[name="title"]', text: user.taskTitle }))
    await recordStep(report, 'type-task-description', async () => client.type(session.id, { selector: 'form#task-form textarea[name="description"]', text: 'Task created by browser operator' }))
    await recordStep(report, 'select-task-priority', async () => client.select(session.id, { selector: 'form#task-form select[name="priority"]', value: 'HIGH' }))
    await recordStep(report, 'select-task-status', async () => client.select(session.id, { selector: 'form#task-form select[name="status"]', value: 'OPEN' }))
    await recordStep(report, 'submit-task', async () => client.click(session.id, { selector: 'form#task-form button[type="submit"]' }))
    await recordStep(report, 'assert-task-rendered', async () => poll(async () => {
      const { html } = await client.html(session.id, { selector: '#task-list' })
      return html?.includes(user.taskTitle) ? html : null
    }, { message: 'Created task not rendered' }))

    await recordStep(report, 'type-chat-topic', async () => client.type(session.id, { selector: 'form#chat-open-form input[name="topic"]', text: user.chatTopic }))
    await recordStep(report, 'open-chat', async () => client.click(session.id, { selector: 'form#chat-open-form button[type="submit"]' }))
    await recordStep(report, 'assert-chat-rendered', async () => poll(async () => {
      const { html } = await client.html(session.id, { selector: '#chat-list' })
      return html?.includes(user.chatTopic) ? html : null
    }, { message: 'Chat topic not rendered' }))

    await recordStep(report, 'select-chat', async () => client.click(session.id, { selector: '[data-chat-open]' }))
    await recordStep(report, 'wait-message-form', async () => ensurePage(session.id, '#message-form textarea[name="content"]'))
    await recordStep(report, 'type-chat-message', async () => client.type(session.id, { selector: '#message-form textarea[name="content"]', text: user.chatMessage }))
    await recordStep(report, 'send-chat-message', async () => client.submit(session.id, { selector: '#message-form' }))
    await recordStep(report, 'assert-chat-message', async () => poll(async () => {
      const { html } = await client.html(session.id, { selector: '#message-list' })
      return html?.includes(user.chatMessage) ? html : null
    }, { message: 'Chat message not rendered' }))

    const successArtifacts = await saveSuccessArtifacts(session.id, scenarioDir)
    report.finishedAt = new Date().toISOString()
    report.status = 'passed'
    report.artifacts = {
      successScreenshot: successArtifacts.screenshotPath,
      console: successArtifacts.consolePath,
      network: successArtifacts.networkPath,
    }
    report.result = { sessionId: session.id, userEmail: user.email, taskTitle: user.taskTitle, chatTopic: user.chatTopic }
    return report
  } catch (error) {
    const artifacts = await saveFailureArtifacts(session.id, scenarioDir)
    report.finishedAt = new Date().toISOString()
    report.status = 'failed'
    report.error = error.message
    report.artifacts = artifacts
    return report
  } finally {
    await client.deleteSession(session.id).catch(() => {})
  }
}

async function scenarioAdminBroadcast() {
  const scenarioDir = path.join(artifactsDir, 'admin-broadcast')
  const report = { name: 'admin-broadcast', startedAt: new Date().toISOString(), steps: [] }
  const suffix = uniqueSuffix()
  const broadcast = {
    title: `Smoke Broadcast ${suffix}`,
    body: `Broadcast body ${suffix}`,
  }

  const session = await client.createSession({ browser: 'chromium', headless: true, baseUrl: APP_URL })
  try {
    await recordStep(report, 'open-login-page', async () => client.open(session.id, { url: `${APP_URL}/`, waitUntil: 'load' }))
    await recordStep(report, 'wait-login-form', async () => ensurePage(session.id, 'form#login-form button[type="submit"]'))
    await recordStep(report, 'type-admin-email', async () => client.type(session.id, { selector: 'form#login-form input[name="email"]', text: 'admin@local.dev' }))
    await recordStep(report, 'type-admin-password', async () => client.type(session.id, { selector: 'form#login-form input[name="password"]', text: 'admin12345' }))
    await recordStep(report, 'submit-login', async () => client.click(session.id, { selector: 'form#login-form button[type="submit"]' }))
    await recordStep(report, 'assert-admin-page', async () => poll(async () => {
      const { text } = await client.text(session.id, { selector: 'h1' })
      return text?.includes('Admin Workspace') ? text : null
    }, { message: 'Admin page did not load for broadcast scenario' }))

    await recordStep(report, 'type-broadcast-title', async () => client.type(session.id, { selector: 'form#broadcast-form input[name="title"]', text: broadcast.title }))
    await recordStep(report, 'type-broadcast-body', async () => client.type(session.id, { selector: 'form#broadcast-form textarea[name="body"]', text: broadcast.body }))
    await recordStep(report, 'select-broadcast-status', async () => client.select(session.id, { selector: 'form#broadcast-form select[name="status"]', value: 'ACTIVE' }))
    await recordStep(report, 'submit-broadcast', async () => client.click(session.id, { selector: 'form#broadcast-form button[type="submit"]' }))
    await recordStep(report, 'assert-broadcast-rendered', async () => poll(async () => {
      const { html } = await client.html(session.id, { selector: '#broadcast-list' })
      return html?.includes(broadcast.title) ? html : null
    }, { message: 'Broadcast not rendered' }))

    await recordStep(report, 'run-broadcasts', async () => client.click(session.id, { selector: '#run-broadcasts' }))
    await recordStep(report, 'assert-broadcast-run-status', async () => poll(async () => {
      const { text } = await client.text(session.id, { selector: '#admin-status' })
      return text?.includes('Active broadcasts triggered.') ? text : null
    }, { message: 'Broadcast run status not updated' }))

    const successArtifacts = await saveSuccessArtifacts(session.id, scenarioDir)
    report.finishedAt = new Date().toISOString()
    report.status = 'passed'
    report.artifacts = {
      successScreenshot: successArtifacts.screenshotPath,
      console: successArtifacts.consolePath,
      network: successArtifacts.networkPath,
    }
    report.result = { sessionId: session.id, broadcastTitle: broadcast.title }
    return report
  } catch (error) {
    const artifacts = await saveFailureArtifacts(session.id, scenarioDir)
    report.finishedAt = new Date().toISOString()
    report.status = 'failed'
    report.error = error.message
    report.artifacts = artifacts
    return report
  } finally {
    await client.deleteSession(session.id).catch(() => {})
  }
}

async function run() {
  await ensureDir(artifactsDir)
  console.log('Bridge health:', await client.health())

  const results = []
  results.push(await scenarioAuthAdmin())
  results.push(await scenarioUserTaskAndChat())
  results.push(await scenarioAdminBroadcast())

  const summary = {
    startedAt: results[0]?.startedAt || new Date().toISOString(),
    finishedAt: new Date().toISOString(),
    targetUrl: APP_URL,
    total: results.length,
    passed: results.filter((item) => item.status === 'passed').length,
    failed: results.filter((item) => item.status === 'failed').length,
    scenarios: results,
  }

  const reportPath = path.join(artifactsDir, 'report.json')
  await writeFile(reportPath, JSON.stringify(summary, null, 2), 'utf-8')

  if (AUTO_IMPORT_VISUALIZER) {
    const importerPath = path.resolve('..', 'scripts', 'import_browser_smoke_report.py')
    const result = spawnSync('py', ['-3', importerPath, reportPath], {
      cwd: process.cwd(),
      encoding: 'utf-8',
    })
    summary.visualizerImport = {
      enabled: true,
      exitCode: result.status,
      stdout: result.stdout?.trim() || '',
      stderr: result.stderr?.trim() || '',
      ok: result.status === 0,
    }
  } else {
    summary.visualizerImport = {
      enabled: false,
      ok: false,
    }
  }

  await writeFile(reportPath, JSON.stringify(summary, null, 2), 'utf-8')

  console.log(JSON.stringify(summary, null, 2))
  console.log(`Report written to ${reportPath}`)

  if (summary.failed > 0) {
    process.exitCode = 1
  }
}

run().catch((error) => {
  console.error(error.stack || String(error))
  process.exit(1)
})
