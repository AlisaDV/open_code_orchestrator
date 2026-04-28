from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
Mode = Literal["consult", "generate", "debug"]


class ReleaseReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    tests_green: bool | None = None
    docs_updated: bool | None = None
    migrations_present: bool | None = None
    rollback_plan_present: bool | None = None
    notes: list[str] = Field(default_factory=list)


class ReleaseFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ReleaseReviewResult(BaseModel):
    mode: Mode
    summary: str
    findings: list[ReleaseFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
