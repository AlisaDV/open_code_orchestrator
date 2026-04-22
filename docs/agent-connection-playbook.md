# Agent Connection Playbook

Пошаговая инструкция для повторного подключения OpenCode-модулей к новому проекту.

Этот документ написан как рабочий playbook: его можно использовать как ссылку-инструкцию, когда нужно быстро подключить оркестратор, визуализацию, браузерный мост и specialist-агентов к новому проекту.

## Цель

Подключить к проекту 4 слоя:

1. `opencode_orchestrator` — координация, code/task execution, approvals, sessions.
2. `orchestrator_visualizer` — timeline, file impact, verification, browser smoke reports.
3. `browser_operator` — Playwright bridge для живого UI тестирования.
4. specialist-агенты — например `bitrix24_agent`, когда проекту нужна прикладная интеграционная экспертиза.

## Базовый принцип

Не встраивать эти модули внутрь каждого проекта вручную.

Правильная схема:

- проект живет отдельно;
- orchestration stack живет рядом;
- проект подключается через `workspace`, `baseUrl`, project profile и сценарии.

## Подключение к новому проекту

### Шаг 1. Определить тип проекта

Нужно зафиксировать:

- где лежит код проекта;
- как он запускается;
- есть ли backend API;
- есть ли frontend UI;
- нужны ли browser smoke tests;
- нужны ли specialist-интеграции.

Минимальный набор параметров:

```json
{
  "name": "project-name",
  "workspace": "C:/work/project-name",
  "baseUrl": "http://localhost:8080",
  "api": true,
  "ui": true,
  "browserSmoke": true,
  "integrations": []
}
```

### Шаг 2. Подключить orchestrator

Нужно указать:

- `workspace`
- `objective`
- `session_id` при необходимости
- включен ли visualizer

Базовый запуск:

```bash
opencode-orchestrator "Проверить проект, прогнать тесты и обновить документацию" --workspace C:\path\to\project
```

Если нужен persistent context:

```bash
opencode-orchestrator "Продолжить работу над проектом" --workspace C:\path\to\project --session-id project-session
```

### Шаг 3. Подключить visualizer

Visualizer работает рядом и использует локальное хранилище `.opencode_observer/`.

Запуск API/dashboard:

```bash
orchestrator-visualizer-api
```

Открыть dashboard:

```text
http://127.0.0.1:8787/dashboard
```

Что должен показывать visualizer:

- runs
- events timeline
- file impact
- approvals
- verification
- browser smoke summary

### Шаг 4. Подключить browser operator

Если проект имеет UI, поднять браузерный мост.

Установка:

```bash
cd browser_operator
npm install
npm run install:browsers
```

Запуск:

```bash
cd browser_operator
npm start
```

Проверка:

```text
http://127.0.0.1:8790/health
```

### Шаг 5. Подключить browser smoke к проекту

Если проект уже поднят локально, указать его URL.

Для Project 01 это:

```bash
cd browser_operator
set PROJECT01_URL=http://localhost:8081
npm run smoke:project01
```

При успешной настройке smoke-run должен:

- открыть UI проекта;
- пройти ключевые сценарии;
- записать `report.json`;
- автоматически импортировать результат в visualizer.

### Шаг 6. Проверить auto-import в visualizer

После smoke-run visualizer должен видеть latest browser smoke report.

Проверка через API:

```text
GET /browser-smoke/latest
```

Проверка в dashboard:

- слева должен появиться блок `Latest Browser Smoke`;
- должны отображаться сценарии;
- должны быть ссылки на `screenshot`, `console`, `network`.

### Шаг 7. Подключить specialist-агента

Если проект зависит от внешней платформы, подключается отдельный specialist-модуль.

Пример:

- `bitrix24_agent`
- `telegram_agent`
- `amo_agent`

Правило:

- specialist не живет внутри проекта;
- specialist живет как отдельный knowledge/execution module;
- orchestrator делегирует в него задачи по доменной области.

Пример готового specialist-модуля в этом репозитории:

- `src/bitrix24_agent/`

Для orchestrator specialist подключается через `enabled_specialists`.

Пример на Python:

```python
from opencode_orchestrator import OrchestratorConfig, run_orchestrator

config = OrchestratorConfig(
    workspace=r"C:\work\my-project",
    objective="Подготовить интеграцию с Bitrix24",
    enabled_specialists=["bitrix24"],
)

result = run_orchestrator(config)
```

После этого manager agent получает specialist tools:

- `bitrix24_manifest`
- `bitrix24_consult`
- `bitrix24_generate`
- `bitrix24_debug`
- `bitrix24_execute`

## Рекомендуемая структура для нового проекта

Если проект хранится в том же репозитории:

```text
/
|-- src/opencode_orchestrator/
|-- src/orchestrator_visualizer/
|-- browser_operator/
|-- docs/
`-- projects/
    `-- 02-project-name/
```

Если проект внешний:

- orchestration stack остается в этом репозитории;
- проект лежит в своей директории;
- подключение идет через `--workspace` и `baseUrl`.

## Что нужно прислать, чтобы быстро подключить новый проект

Достаточно прислать:

1. ссылку на этот playbook;
2. путь к `workspace`;
3. `baseUrl`;
4. как запускать проект;
5. какие сценарии критичны;
6. нужны ли specialist-интеграции.

Минимальный шаблон сообщения:

```text
Подключаем новый проект.
Workspace: C:\work\my-project
Base URL: http://localhost:3000
Run command: npm run dev
Есть UI: да
Нужен browser smoke: да
Нужны integrations: bitrix24
Критичные сценарии: login, create order, admin approval
```

## Чеклист подключения

### A. Infra

- проект запускается локально;
- база данных доступна;
- `baseUrl` отвечает;
- browser operator поднят;
- visualizer поднят.

### B. Orchestrator

- указан корректный `workspace`;
- задан `objective`;
- при необходимости задан `session_id`;
- visualizer включен.

### C. Browser smoke

- есть набор сценариев;
- smoke-run создает `report.json`;
- report auto-import попадает в visualizer;
- артефакты доступны на диске.

### D. Specialist agents

- knowledge pack локально сохранен;
- secrets не зашиты в docs;
- есть playbooks по типовым операциям;
- orchestrator знает, когда делегировать в specialist.

## Правила качества

### Не делать

- не копировать orchestration code в каждый проект;
- не хранить токены в документации;
- не строить тестирование только на UI без API/логов;
- не запускать browser smoke без артефактов.

### Делать

- хранить сценарии как переиспользуемые playbooks;
- сохранять screenshots, console, network;
- импортировать browser smoke в visualizer автоматически;
- держать specialist knowledge packs локально и версионировать их.

## Команды по умолчанию

### Orchestrator

```bash
opencode-orchestrator "Проверить проект" --workspace C:\path\to\project
```

### Visualizer

```bash
orchestrator-visualizer-api
```

### Browser Operator

```bash
cd browser_operator
npm start
```

### Browser Smoke

```bash
cd browser_operator
npm run smoke:project01
```

## Что дальше улучшать

1. Ввести единый `project.agent.json` profile.
2. Автоматически загружать scenarios по profile.
3. Автоматически связывать browser smoke runs с конкретными orchestrator run ids.
4. Добавить specialist registry для Bitrix24 и других интеграций.
