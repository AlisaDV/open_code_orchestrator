# Delivery Roadmap

## Project 01

- Goal: validate the orchestrator on a medium-size full-stack system with auth, CRUD, scheduler, chat, and admin tooling.
- Stack:
  - backend: Kotlin, Spring Boot, Spring Security, JWT, Hibernate/JPA, PostgreSQL, Scheduled, WebSocket
  - frontend: simple HTML, CSS, JavaScript
- Validation focus:
  - multi-step backend implementation
  - DB-driven domain with non-trivial relations
  - real-time flows
  - admin and user zones
  - repeatable tests and local runbook

## Project 02

- Starts only after Project 01 is functionally complete, documented, and tested.
- Should stress different orchestrator behaviors than Project 01.

## Definition Of Done For Each Phase

1. Code exists in the expected module.
2. Docs are updated for the phase.
3. Build/test commands are executable locally.
4. Risks and next steps are explicitly written down.
