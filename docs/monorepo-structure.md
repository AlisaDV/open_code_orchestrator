# Monorepo Structure

## Current Layout

```text
open_code_orchestrator/
|-- src/opencode_orchestrator/        # Python orchestration layer
|-- tests/                            # Python tests for orchestrator
|-- projects/
|   `-- 01-task-support-app/          # First verification project
`-- docs/                             # Cross-project architecture docs
```

## Target Layout

```text
open_code_orchestrator/
|-- orchestrator/
|   |-- pyproject.toml
|   |-- README.md
|   |-- src/opencode_orchestrator/
|   `-- tests/
|-- projects/
|   |-- 01-task-support-app/
|   |   |-- build.gradle.kts
|   |   |-- src/
|   |   `-- docs/
|   `-- 02-<next-project>/
|       |-- <project files>
|       `-- docs/
`-- docs/
    |-- monorepo-structure.md
    `-- delivery-roadmap.md
```

## Responsibility Boundaries

- `orchestrator`: OpenAI Agents SDK manager, roles, guardrails, sessions, approvals.
- `projects/01-task-support-app`: first end-to-end product used to validate orchestrator workflows.
- `projects/02-*`: second validation product, added only after project 01 is complete.
- `docs/`: shared architectural documentation, delivery conventions, and cross-project process maps.

## Phase Strategy

1. Phase 1: structure, architecture, ERD, API map, implementation plan.
2. Phase 2: auth and user domain.
3. Phase 3: tasks, comments, alarms.
4. Phase 4: support chat and WebSocket updates.
5. Phase 5: admin APIs and broadcast scheduler.
6. Phase 6: simple HTML/CSS/JS frontend.
7. Phase 7: tests, verification, runbook.
8. Phase 8: visualization and constructor-style documentation.

## Notes

- The repository currently still keeps the Python orchestrator package at the root. The target physical move into `orchestrator/` is planned once the first product stabilizes, to avoid breaking the already-tested Python package mid-stream.
- All new product work should go only into numbered directories under `projects/`.
