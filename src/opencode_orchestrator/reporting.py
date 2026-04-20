from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class OrchestratorReport(BaseModel):
    objective: str = Field(description="Original objective for the orchestration run.")
    summary: str = Field(description="Short summary of the completed work.")
    completed: list[str] = Field(default_factory=list, description="Completed actions.")
    evidence: list[str] = Field(default_factory=list, description="Concrete commands, files, or outputs that support the summary.")
    risks: list[str] = Field(default_factory=list, description="Remaining gaps, blockers, or unverified areas.")
    next_steps: list[str] = Field(default_factory=list, description="Useful follow-up actions.")


class PendingApproval(BaseModel):
    index: int
    tool_name: str
    arguments: str | None = None
    agent_name: str | None = None
    call_id: str | None = None


class OrchestratorOutcome(BaseModel):
    status: Literal["completed", "awaiting_approval"]
    objective: str
    report: OrchestratorReport | None = None
    state_path: str | None = None
    approvals: list[PendingApproval] = Field(default_factory=list)
