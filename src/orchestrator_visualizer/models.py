from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class RunStatus(StrEnum):
    STARTED = "started"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(StrEnum):
    RUN_STARTED = "run_started"
    PHASE_STARTED = "phase_started"
    PHASE_FINISHED = "phase_finished"
    AGENT_CALLED = "agent_called"
    AGENT_FINISHED = "agent_finished"
    TOOL_CALLED = "tool_called"
    TOOL_FINISHED = "tool_finished"
    FILE_CHANGED = "file_changed"
    TEST_STARTED = "test_started"
    TEST_FINISHED = "test_finished"
    BUILD_STARTED = "build_started"
    BUILD_FINISHED = "build_finished"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_RESOLVED = "approval_resolved"
    RUN_FINISHED = "run_finished"
    ERROR = "error"


class ApprovalStatus(StrEnum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"


class ChangeType(StrEnum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"


class VerificationKind(StrEnum):
    TEST = "test"
    BUILD = "build"
    RUN = "run"
    LINT = "lint"
    DOCS = "docs"


class VerificationStatus(StrEnum):
    STARTED = "started"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RunRecord(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str | None = None
    objective: str
    status: RunStatus = RunStatus.STARTED
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: datetime | None = None
    model: str | None = None
    workspace: str | None = None
    summary: str | None = None


class EventRecord(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    session_id: str | None = None
    event_type: EventType
    phase: str | None = None
    agent: str | None = None
    status: str | None = None
    ts: datetime = Field(default_factory=utc_now)
    title: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class FileImpactRecord(BaseModel):
    run_id: str
    event_id: str | None = None
    path: str
    change_type: ChangeType
    summary: str | None = None
    agent: str | None = None
    phase: str | None = None
    ts: datetime = Field(default_factory=utc_now)


class ApprovalRecord(BaseModel):
    approval_id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.REQUESTED
    requested_at: datetime = Field(default_factory=utc_now)
    resolved_at: datetime | None = None
    resolution_note: str | None = None


class VerificationRecord(BaseModel):
    run_id: str
    kind: VerificationKind
    status: VerificationStatus
    command: str | None = None
    duration_ms: int | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    ts: datetime = Field(default_factory=utc_now)


class BrowserSmokeStepRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    step_name: str = Field(validation_alias="name")
    status: str
    started_at: datetime | None = Field(default=None, validation_alias="startedAt")
    finished_at: datetime | None = Field(default=None, validation_alias="finishedAt")
    details: dict[str, Any] | str | None = None
    error: str | None = None


class BrowserSmokeScenarioRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_name: str = Field(validation_alias="name")
    status: str
    started_at: datetime | None = Field(default=None, validation_alias="startedAt")
    finished_at: datetime | None = Field(default=None, validation_alias="finishedAt")
    result: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    steps: list[BrowserSmokeStepRecord] = Field(default_factory=list)


class BrowserSmokeReportRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    report_id: str = Field(default_factory=lambda: str(uuid4()))
    source_path: str | None = Field(default=None, validation_alias="sourcePath")
    target_url: str = Field(validation_alias="targetUrl")
    started_at: datetime | None = Field(default=None, validation_alias="startedAt")
    finished_at: datetime | None = Field(default=None, validation_alias="finishedAt")
    total: int = 0
    passed: int = 0
    failed: int = 0
    scenarios: list[BrowserSmokeScenarioRecord] = Field(default_factory=list)
