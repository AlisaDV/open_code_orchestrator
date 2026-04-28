from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
Mode = Literal["consult", "generate", "debug"]


class MigrationReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    dependency_upgrade: bool | None = None
    config_upgrade: bool | None = None
    api_contract_upgrade: bool | None = None
    deprecation_removal: bool | None = None
    notes: list[str] = Field(default_factory=list)


class MigrationFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class MigrationReviewResult(BaseModel):
    mode: Mode
    summary: str
    findings: list[MigrationFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
