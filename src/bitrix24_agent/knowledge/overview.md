# Bitrix24 Agent Overview

Knowledge pack source: official Bitrix24 API docs at `https://apidocs.bitrix24.ru`.

This local pack is optimized for practical agent work, not full archival mirroring.

## What Bitrix24 REST API Covers

- CRM
- users
- tasks
- chats and notifications
- telephony
- disk and files
- automation, widgets, scopes, events

## When To Use This Agent

- integrate a project with Bitrix24
- choose correct endpoint family
- determine required scope
- generate request payloads
- debug auth, limit, or object-id issues

## First Heuristic

1. Decide webhook vs OAuth.
2. Identify scope.
3. Identify product area.
4. Prefer documented endpoint family over guessed naming.
5. Check limits/errors before large sync jobs.

## Core Product Areas In This Pack

- `crm`
- `user`
- `tasks`
- `chats`
- `telephony`
- `disk`
