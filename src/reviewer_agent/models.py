from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
ReviewMode = Literal["consult", "generate", "debug"]


class ReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    tests_present: bool | None = None
    notes: list[str] = Field(default_factory=list)


class ReviewFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ReviewResult(BaseModel):
    mode: ReviewMode
    summary: str
    findings: list[ReviewFinding] = Field(default_factory=list)
    review_checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
