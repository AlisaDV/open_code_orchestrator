# OpenCode Orchestrator

Monorepo for the Python orchestration layer plus numbered verification projects.

## Workspace Layout

- `src/opencode_orchestrator/`: Python orchestration layer
- `tests/`: Python tests for the orchestration layer
- `projects/01-task-support-app/`: first full-stack validation project
- `docs/`: shared monorepo and delivery docs

## Phase 1 Docs

- `docs/monorepo-structure.md`
- `docs/delivery-roadmap.md`
- `docs/agent-connection-playbook.md`
- `docs/agent-team-map.md`
- `projects/01-task-support-app/docs/architecture.md`
- `projects/01-task-support-app/docs/erd.mmd`
- `projects/01-task-support-app/docs/processes.mmd`
- `projects/01-task-support-app/docs/api-map.md`

Минимальный, но уже более практичный multi-agent orchestration-слой на `OpenAI Agents SDK`.

Оркестратор запускает менеджер-агента, который делегирует задачи четырем специалистам:

- `Coder` меняет код.
- `Tester` запускает тесты, lint и build.
- `Documenter` обновляет `README` и документацию.
- `Runner` пытается запустить проект и снять результат.

Все агенты работают в одном локальном workspace и используют общий набор инструментов:

- чтение файлов;
- запись файлов;
- просмотр структуры workspace;
- запуск shell-команд.

## Что добавлено поверх стартового каркаса

- `sessions` через `SQLiteSession` для памяти между прогонами;
- structured final output через `Pydantic`-схему `OrchestratorReport`;
- guardrails на shell-команды и защищенные пути;
- approval flow для `write_text_file` и `run_command`;
- сохранение `RunState` и resume paused runs;
- JSON-вывод из CLI, удобный для CI и внешней оркестрации.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Нужна переменная окружения `OPENAI_API_KEY`.

PowerShell:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

## Запуск

Обычный запуск:

```bash
opencode-orchestrator "Разобраться в проекте, прогнать тесты, обновить документацию и попробовать запустить приложение"
```

С памятью между запусками:

```bash
opencode-orchestrator "Продолжить работу по проекту" --session-id demo-run
```

Против другой рабочей папки:

```bash
opencode-orchestrator "Исправить сборку и обновить README" --workspace C:\path\to\repo
```

Без записи в файлы:

```bash
opencode-orchestrator "Проверить проект и составить отчет" --read-only
```

Ограничить объем истории из session:

```bash
opencode-orchestrator "Продолжить анализ" --session-id repo-42 --session-history-limit 40
```

## Approval Flow

По умолчанию включен `--approval-mode write_run`, то есть оркестратор ставит на паузу попытки:

- писать файлы;
- запускать shell-команды.

Вместо финального отчета CLI вернет JSON со статусом `awaiting_approval`, списком pending approvals и путем к сохраненному `RunState`.

Пример первого запуска:

```bash
opencode-orchestrator "Обновить README и прогнать тесты"
```

Пример ответа:

```json
{
  "status": "awaiting_approval",
  "objective": "Обновить README и прогнать тесты",
  "state_path": "C:\\repo\\.opencode_orchestrator\\pending_state.json",
  "approvals": [
    {
      "index": 1,
      "tool_name": "run_command",
      "arguments": "{\"command\":\"pytest\"}"
    }
  ]
}
```

Потом можно продолжить:

```bash
opencode-orchestrator --resume --approve-all
```

Или выборочно:

```bash
opencode-orchestrator --resume --approve 1,2 --reject 3
```

Если флаги approve/reject не переданы, CLI спросит интерактивно по каждому pending item.

Отключить approvals можно так:

```bash
opencode-orchestrator "Проверить проект" --approval-mode none
```

## Формат результата

CLI печатает один из двух JSON-ответов.

Завершенный прогон:

```json
{
  "status": "completed",
  "objective": "...",
  "report": {
    "objective": "...",
    "summary": "...",
    "completed": ["..."],
    "evidence": ["..."],
    "risks": ["..."],
    "next_steps": ["..."]
  }
}
```

Пауза на approval:

```json
{
  "status": "awaiting_approval",
  "objective": "...",
  "state_path": "...",
  "approvals": [
    {
      "index": 1,
      "tool_name": "run_command",
      "arguments": "..."
    }
  ]
}
```

## Guardrails

Сейчас есть базовые ограничения:

- запрещены явно опасные shell-паттерны вроде `rm`, `del`, `git reset --hard`, пайпов и редиректов;
- запрещена запись в защищенные пути вроде `.env`, `.git/`, `credentials.json`, `secrets/`;
- запрещено читать вероятно бинарные файлы как текст;
- нельзя выйти за пределы workspace.

Это не sandbox и не полноценная policy-engine система, но для стартового orchestration-слоя уже снижает риск случайно опасных действий.

## Основные файлы

- `src/opencode_orchestrator/config.py`
- `src/opencode_orchestrator/tools.py`
- `src/opencode_orchestrator/approval.py`
- `src/opencode_orchestrator/reporting.py`
- `src/opencode_orchestrator/agents.py`
- `src/opencode_orchestrator/orchestrator.py`
- `src/opencode_orchestrator/cli.py`

## Ограничения

- shell по-прежнему выполняется локально на машине пользователя;
- guardrails работают по policy-паттернам и не заменяют sandbox isolation;
- запись файлов сделана полной заменой содержимого файла;
- approvals сейчас завязаны на function-tool flow, а не на отдельный UI/backend;
- роли остаются prompt-driven, без жесткой state machine.

## Следующие логичные шаги

1. Перевести shell в sandbox/container execution.
2. Сохранять pending approvals в отдельном хранилище или БД.
3. Разделить профили агентов под frontend/backend/devops.
4. Добавить экспорт traces и интеграцию с CI.
