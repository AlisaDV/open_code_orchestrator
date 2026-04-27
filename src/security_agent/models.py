from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
SecurityMode = Literal["consult", "generate", "debug"]


class SecurityReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    auth_touched: bool | None = None
    external_integration: bool | None = None
    secrets_present: bool | None = None
    notes: list[str] = Field(default_factory=list)


class SecurityFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class SecurityReviewResult(BaseModel):
    mode: SecurityMode
    summary: str
    findings: list[SecurityFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
