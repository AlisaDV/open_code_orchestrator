# Bitrix24 Agent

Specialist knowledge module for Bitrix24 REST API.

## Goal

Provide a reusable agent package that can be attached to any project when Bitrix24 integration work is needed.

The package is knowledge-first:

- local documentation summaries
- endpoint map
- auth and scope notes
- playbooks for common integration tasks

## Current Scope

The current package is a curated starter pack, not a full mirrored copy of every Bitrix24 endpoint page.

Included areas:

- first steps and webhook flow
- OAuth 2.0 full flow
- scopes
- limits and common error handling
- CRM overview and universal methods
- users
- tasks
- chats
- telephony
- disk

## Directory Layout

```text
src/bitrix24_agent/
|-- __init__.py
|-- manifest.py
|-- README.md
|-- endpoint_map.json
|-- knowledge/
|   |-- overview.md
|   |-- auth.md
|   |-- scopes.md
|   |-- limits-and-errors.md
|   |-- crm.md
|   |-- users.md
|   |-- tasks.md
|   |-- chats.md
|   |-- telephony.md
|   `-- disk.md
`-- playbooks/
    |-- create-crm-item.md
    |-- create-task-with-crm-link.md
    |-- create-chat-and-send-message.md
    |-- register-external-call.md
    `-- upload-file-and-link.md
```

## How To Use

### Consult mode

Use local knowledge files to answer:

- which scope is needed
- which endpoint family to use
- webhook vs OAuth
- common rate-limit and error patterns

### Generate mode

Use `endpoint_map.json` and playbooks to generate:

- integration services
- request payload builders
- webhook handlers
- retry and error handling logic

### Execute mode

Should be enabled only when the calling project provides:

- portal domain
- webhook or OAuth credentials through env/config
- explicit permission to perform live Bitrix24 calls

### Debug mode

Use knowledge files for:

- `QUERY_LIMIT_EXCEEDED`
- auth/scope errors
- incorrect method family selection
- wrong object identifiers like `entityTypeId`, `categoryId`, `stageId`

## Key Rules

- never store webhook secrets or OAuth client secrets in the knowledge pack
- prefer official method families over guessed endpoints
- check required scope before generating or executing a request
- for CRM, prefer universal `crm.item.*` when the object is dynamic or when `entityTypeId`-based workflows are needed
- for new chat file flows, prefer `im.v2` file methods over old `im.disk.*`

## Recommended Next Step

Execution layer is now included in starter form:

- `config.py`
- `models.py`
- `client.py`
- `planner.py`
- `runtime.py`

What it supports now:

- dry-run planning
- method family detection
- consult/generate/debug runtime
- optional live execution when credentials are explicitly provided
- practical executors for common playbooks:
  - create CRM item
  - create task with CRM link
  - create chat and send message
  - register external call

If this module is to be used for more serious live integration work, the next layer should be added:

1. richer typed request/response models by method family
2. token refresh workflow for OAuth
3. tested retry policy and rate-limit backoff
4. scenario-level execution playbooks
