from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]
DataSyncMode = Literal["consult", "generate", "debug"]


class DataSyncReviewRequest(BaseModel):
    summary: str
    files: list[str] = Field(default_factory=list)
    changed_areas: list[str] = Field(default_factory=list)
    import_flow: bool | None = None
    export_flow: bool | None = None
    checkpointing_present: bool | None = None
    dedup_logic_present: bool | None = None
    reconciliation_present: bool | None = None
    notes: list[str] = Field(default_factory=list)


class DataSyncFinding(BaseModel):
    severity: Severity
    title: str
    rationale: str
    affected_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class DataSyncReviewResult(BaseModel):
    mode: DataSyncMode
    summary: str
    findings: list[DataSyncFinding] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
