from __future__ import annotations

from pydantic import BaseModel, Field


class RunSummary(BaseModel):
    run_id: str
    status: str
    objective: str
    started_at: str
    finished_at: str | None = None
    event_count: int = 0
    file_count: int = 0
    approval_count: int = 0
    verification_count: int = 0


class FileImpactAggregate(BaseModel):
    path: str
    change_count: int = 0
    agents: list[str] = Field(default_factory=list)
    phases: list[str] = Field(default_factory=list)
    last_change_type: str | None = None
    last_summary: str | None = None
