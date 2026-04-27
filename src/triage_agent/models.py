from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
Mode = Literal["consult", "generate", "debug"]


class TriageRequest(BaseModel):
    title: str
    description: str
    environment: str | None = None
    area_hints: list[str] = Field(default_factory=list)
    reproduction_steps: list[str] = Field(default_factory=list)
    logs_present: bool | None = None
    ui_involved: bool | None = None
    external_integration_involved: bool | None = None


class TriageFinding(BaseModel):
    severity: Severity
    classification: str
    rationale: str
    likely_owners: list[str] = Field(default_factory=list)
    next_agents: list[str] = Field(default_factory=list)
    reproduction_gaps: list[str] = Field(default_factory=list)


class TriageResult(BaseModel):
    mode: Mode
    summary: str
    findings: list[TriageFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
