from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
DevOpsMode = Literal["consult", "generate", "debug"]


class DevOpsReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    docker_touched: bool | None = None
    ci_touched: bool | None = None
    env_touched: bool | None = None
    deploy_path_changed: bool | None = None
    notes: list[str] = Field(default_factory=list)


class DevOpsFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class DevOpsReviewResult(BaseModel):
    mode: DevOpsMode
    summary: str
    findings: list[DevOpsFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
