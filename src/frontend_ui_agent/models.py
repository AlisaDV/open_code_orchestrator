from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
FrontendUiMode = Literal["consult", "generate", "debug"]


class FrontendUiReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    forms_touched: bool | None = None
    navigation_touched: bool | None = None
    accessibility_touched: bool | None = None
    browser_flow_touched: bool | None = None
    notes: list[str] = Field(default_factory=list)


class FrontendUiFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class FrontendUiReviewResult(BaseModel):
    mode: FrontendUiMode
    summary: str
    findings: list[FrontendUiFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
