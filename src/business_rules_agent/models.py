from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
Mode = Literal["consult", "generate", "debug"]


class BusinessRuleReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    state_transition_changed: bool | None = None
    approval_logic_changed: bool | None = None
    cross_entity_consistency_changed: bool | None = None
    external_business_process_changed: bool | None = None
    notes: list[str] = Field(default_factory=list)


class BusinessRuleFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class BusinessRuleReviewResult(BaseModel):
    mode: Mode
    summary: str
    findings: list[BusinessRuleFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
