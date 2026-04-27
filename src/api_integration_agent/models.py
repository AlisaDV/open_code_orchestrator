from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
ApiIntegrationMode = Literal["consult", "generate", "debug"]


class ApiIntegrationReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    oauth_touched: bool | None = None
    webhook_touched: bool | None = None
    retry_logic_touched: bool | None = None
    pagination_touched: bool | None = None
    notes: list[str] = Field(default_factory=list)


class ApiIntegrationFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ApiIntegrationReviewResult(BaseModel):
    mode: ApiIntegrationMode
    summary: str
    findings: list[ApiIntegrationFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
