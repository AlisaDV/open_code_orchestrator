# Reviewer Agent

Specialist module for findings-first code review.

## Goal

Help the orchestrator perform structured review work that prioritizes:

- bugs
- risks
- regressions
- missing tests
- unsafe assumptions

## Scope

This module does not replace reading code directly. It provides:

- review heuristics
- severity-oriented findings scaffolds
- review checklists
- review-debug guidance

## Modes

- `consult` — explain how to review a change area
- `generate` — generate likely findings/checklist from a summarized change scope
- `debug` — explain where review likely missed a regression

## Recommended Usage

Use before commit, before PR, or after bug escape.
