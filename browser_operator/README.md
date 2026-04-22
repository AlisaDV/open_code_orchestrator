# Browser Operator

Playwright-based browser bridge for UI testing from the orchestrator side.

## Goal

Provide a stable local service that can:

- open pages
- click elements
- type into inputs
- select dropdown values
- wait for selectors
- read text or HTML
- take screenshots
- collect console messages
- collect network activity

This is a bridge for controlled browser automation, not a browser extension.

## Architecture

```text
browser_operator/
|-- package.json
|-- README.md
`-- src/
    |-- server.js           # Express HTTP server
    |-- session-manager.js  # Browser/session lifecycle
    `-- schemas.js          # Request validation
```

## Transport

The bridge exposes a local HTTP API. This keeps it easy to call from Python orchestrator code or shell commands.

## Session Model

Each browser session owns:

- one Playwright browser
- one browser context
- one active page
- rolling console log
- rolling network log

## Initial Endpoints

- `GET /health`
- `POST /sessions`
- `GET /sessions`
- `GET /sessions/:id`
- `DELETE /sessions/:id`
- `POST /sessions/:id/open`
- `POST /sessions/:id/click`
- `POST /sessions/:id/type`
- `POST /sessions/:id/select`
- `POST /sessions/:id/wait-for`
- `POST /sessions/:id/submit`
- `POST /sessions/:id/text`
- `POST /sessions/:id/html`
- `POST /sessions/:id/screenshot`
- `GET /sessions/:id/console`
- `GET /sessions/:id/network`

## Install

```bash
cd browser_operator
npm install
npm run install:browsers
```

## Run

```bash
cd browser_operator
npm start
```

Default URL:

```text
http://127.0.0.1:8790
```

## Project 01 Smoke Run

If the target app is already running, execute the prepared UI smoke suite:

```bash
cd browser_operator
npm run smoke:project01
```

Optional target override:

```bash
set PROJECT01_URL=http://localhost:8081
npm run smoke:project01
```

By default the generated `report.json` is automatically imported into `orchestrator_visualizer`.

Disable auto-import if needed:

```bash
set BROWSER_SMOKE_AUTO_IMPORT=0
npm run smoke:project01
```

Artifacts on failure are written to:

```text
browser_operator/artifacts/project01-smoke/
```

Each smoke run also writes:

- `report.json` with scenario summary and step-by-step results
- `success.png` or `failure.png` per scenario
- `*.console.json` per scenario
- `*.network.json` per scenario

## Intended Usage From Orchestrator

1. create a session
2. open the app URL
3. run a sequence of UI actions
4. read text/HTML/screenshot/logs
5. close the session

## Quality Constraints

- explicit session lifecycle
- bounded log buffers to avoid memory leaks
- input validation on every route
- deterministic timeouts per action
- no hidden global browser state shared across unrelated sessions
