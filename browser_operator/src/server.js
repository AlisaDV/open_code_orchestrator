import express from 'express'
import { ZodError } from 'zod'

import { BrowserSessionManager } from './session-manager.js'
import {
  clickSchema,
  createSessionSchema,
  openSchema,
  readSchema,
  screenshotSchema,
  selectSchema,
  submitSchema,
  typeSchema,
  waitForSchema,
} from './schemas.js'

const app = express()
const port = process.env.BROWSER_OPERATOR_PORT || 8790
const manager = new BrowserSessionManager()

app.use(express.json({ limit: '1mb' }))

function sendValidationError(res, error) {
  if (error instanceof ZodError) {
    return res.status(400).json({ error: 'validation_error', details: error.issues })
  }
  return res.status(500).json({ error: 'internal_error', message: String(error) })
}

function requireSession(req, res) {
  const session = manager.get(req.params.id)
  if (!session) {
    res.status(404).json({ error: 'session_not_found' })
    return null
  }
  return session
}

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' })
})

app.get('/sessions', (_req, res) => {
  res.json(manager.list())
})

app.post('/sessions', async (req, res) => {
  try {
    const payload = createSessionSchema.parse(req.body ?? {})
    const session = await manager.create(payload)
    res.status(201).json(session)
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.get('/sessions/:id', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  res.json(manager.snapshot(session))
})

app.delete('/sessions/:id', async (req, res) => {
  const ok = await manager.close(req.params.id)
  if (!ok) {
    res.status(404).json({ error: 'session_not_found' })
    return
  }
  res.json({ ok: true })
})

app.post('/sessions/:id/open', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = openSchema.parse(req.body ?? {})
    res.json(await manager.open(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.post('/sessions/:id/click', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = clickSchema.parse(req.body ?? {})
    res.json(await manager.click(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.post('/sessions/:id/type', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = typeSchema.parse(req.body ?? {})
    res.json(await manager.type(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.post('/sessions/:id/select', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = selectSchema.parse(req.body ?? {})
    res.json(await manager.select(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.post('/sessions/:id/wait-for', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = waitForSchema.parse(req.body ?? {})
    res.json(await manager.waitFor(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.post('/sessions/:id/submit', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = submitSchema.parse(req.body ?? {})
    res.json(await manager.submit(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.post('/sessions/:id/text', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = readSchema.parse(req.body ?? {})
    res.json(await manager.text(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.post('/sessions/:id/html', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = readSchema.parse(req.body ?? {})
    res.json(await manager.html(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.post('/sessions/:id/screenshot', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  try {
    const payload = screenshotSchema.parse(req.body ?? {})
    res.json(await manager.screenshot(session, payload))
  } catch (error) {
    sendValidationError(res, error)
  }
})

app.get('/sessions/:id/console', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  res.json(manager.getConsole(session))
})

app.get('/sessions/:id/network', async (req, res) => {
  const session = requireSession(req, res)
  if (!session) return
  res.json(manager.getNetwork(session))
})

app.listen(port, () => {
  console.log(`browser_operator listening on http://127.0.0.1:${port}`)
})
