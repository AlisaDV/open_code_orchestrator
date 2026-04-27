from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
ObservabilityMode = Literal["consult", "generate", "debug"]


class ObservabilityReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    logging_touched: bool | None = None
    metrics_touched: bool | None = None
    tracing_touched: bool | None = None
    alerting_touched: bool | None = None
    notes: list[str] = Field(default_factory=list)


class ObservabilityFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ObservabilityReviewResult(BaseModel):
    mode: ObservabilityMode
    summary: str
    findings: list[ObservabilityFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
