from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
DatabaseMode = Literal["consult", "generate", "debug"]


class DatabaseReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    schema_changed: bool | None = None
    migration_present: bool | None = None
    query_changed: bool | None = None
    notes: list[str] = Field(default_factory=list)


class DatabaseFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class DatabaseReviewResult(BaseModel):
    mode: DatabaseMode
    summary: str
    findings: list[DatabaseFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
