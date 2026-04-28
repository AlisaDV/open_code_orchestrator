# Agent Team Map

Карта текущей команды агентов и рекомендации по тому, когда какого агента включать.

## 1. Core Runtime

Это базовые роли orchestration-слоя.

### `orchestrator`

- координация задач
- делегирование
- approvals
- sessions
- итоговый отчет

### `coder`

- реализация кода
- минимальные правки
- refactor/fix/feature work

### `tester`

- tests
- lint
- build verification

### `runner`

- запуск проекта
- runtime reproduction
- лог-сигналы и стартовые ошибки

### `documenter`

- README
- docs
- runbooks
- change notes

## 2. Observability And Browser Layers

### `orchestrator_visualizer`

- run timeline
- file impact
- approvals
- verification
- browser smoke reports

### `browser_operator`

- Playwright bridge
- UI automation
- screenshots
- console/network capture

### `browser smoke`

- auth smoke
- user flow smoke
- admin flow smoke
- auto-import into visualizer

## 3. Engineering Specialist Agents

### `reviewer_agent`

Use when:

- нужно findings-first code review
- нужен pre-commit / pre-PR risk scan
- нужно понять, где мог проскочить регресс

Focus:

- bugs
- regressions
- missing tests
- risky assumptions

### `security_agent`

Use when:

- меняются auth/authz paths
- затрагиваются secrets
- появляются внешние callbacks/webhooks
- есть shell/file/input trust boundary

Focus:

- permissions
- token handling
- secret exposure
- injection/trust issues

### `database_agent`

Use when:

- меняются entity/schema/repository/query paths
- есть миграции
- есть FK/cascade/delete semantics

Focus:

- schema compatibility
- migration safety
- index/query fit
- consistency/orphan risks

### `devops_agent`

Use when:

- меняются Docker/CI/CD/env/deploy files
- есть rollout questions
- проект плохо стартует вне локального dev

Focus:

- runtime parity
- env/config
- startup wiring
- rollout/rollback safety

### `observability_agent`

Use when:

- меняются logs/metrics/traces/alerts
- сложно диагностировать инциденты
- нужно понять, хватает ли сигналов для production debugging

Focus:

- signal quality
- correlation
- trace continuity
- actionable alerting

### `api_integration_agent`

Use when:

- интеграция с внешним REST API не доменно-специфична
- важны retries, OAuth, webhooks, idempotency, pagination

Focus:

- auth lifecycle
- callbacks
- retries/backoff
- pagination and sync semantics

### `frontend_ui_agent`

Use when:

- меняются forms, redirects, UI flows
- нужен UI/UX review
- browser smoke находит flaky/broken path

Focus:

- form correctness
- navigation
- feedback states
- accessibility basics

### `triage_agent`

Use when:

- приходит багрепорт или инцидент
- нужно быстро понять, кому отдать задачу дальше

Focus:

- issue classification
- likely owners
- next specialist
- missing evidence

### `data_sync_agent`

Use when:

- есть import/export/sync pipelines
- важны checkpoints, reconciliation, dedup, resume logic

Focus:

- idempotency
- checkpoints
- partial failure recovery
- drift detection

### `business_rules_agent`

Use when:

- есть state machines, approvals, domain invariants
- интеграция может сломать реальный бизнес-процесс при внешне корректном коде

Focus:

- domain semantics
- state transitions
- actor permissions in process
- cross-entity business consistency

### `release_agent`

Use when:

- приближается релиз
- нужно go/no-go решение
- есть migration/deploy/doc/rollback вопросы

Focus:

- release readiness
- rollout order
- rollback
- release notes / operator docs

### `migration_agent`

Use when:

- обновляются framework/library/runtime/API versions
- удаляются deprecated paths
- меняется config semantics

Focus:

- compatibility windows
- staged rollout
- config migration
- removed legacy behavior risk

## 4. Domain Specialists

### `bitrix24_agent`

Use when:

- проект связан с Bitrix24
- нужны consult/generate/debug/execute сценарии по Bitrix24

Focus:

- Bitrix24 auth/scopes/limits/errors
- CRM/tasks/chats/telephony/disk
- Bitrix24-specific playbooks and executors

## 5. Recommended Activation Order

### Almost always on

- `reviewer`
- `security`
- `database`
- `devops`

### Turn on when relevant

- `observability`
- `api_integration`
- `frontend_ui`
- `triage`
- `data_sync`
- `business_rules`
- `release`
- `migration`

### Domain-specific

- `bitrix24`

## 6. Practical Team Presets

### Backend product preset

- `reviewer`
- `security`
- `database`
- `devops`

### Full-stack preset

- `reviewer`
- `security`
- `database`
- `devops`
- `frontend_ui`
- `observability`

### External integration preset

- `reviewer`
- `security`
- `api_integration`
- `data_sync`
- `observability`

### CRM/integration-heavy preset

- `reviewer`
- `security`
- `database`
- `api_integration`
- `data_sync`
- `business_rules`
- `bitrix24`

## 7. Routing Rule Of Thumb

- unknown bug report -> `triage`
- suspicious auth/permissions issue -> `security`
- query/schema/migration issue -> `database`
- Docker/CI/deploy issue -> `devops`
- missing logs/metrics/traces -> `observability`
- webhook/OAuth/pagination/retry problem -> `api_integration`
- broken form/redirect/browser journey -> `frontend_ui`
- sync drift/duplicate processing -> `data_sync`
- broken approval or domain lifecycle -> `business_rules`
- release gate / rollout concern -> `release`
- version upgrade / deprecated path removal -> `migration`
- Bitrix24-specific issue -> `bitrix24`
