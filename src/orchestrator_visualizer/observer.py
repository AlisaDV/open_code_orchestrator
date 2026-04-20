from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import VisualizerConfig
from .models import (
    ApprovalRecord,
    ApprovalStatus,
    ChangeType,
    EventRecord,
    EventType,
    FileImpactRecord,
    RunRecord,
    RunStatus,
    VerificationKind,
    VerificationRecord,
    VerificationStatus,
)
from .repository import VisualizerRepository


class VisualizerObserver:
    def __init__(self, config: VisualizerConfig):
        self.config = config
        self.repository = VisualizerRepository(config)

    def run_started(self, objective: str, *, run_id: str | None = None, session_id: str | None = None, model: str | None = None, workspace: str | None = None) -> RunRecord:
        run = RunRecord(
            run_id=run_id or RunRecord(objective=objective).run_id,
            session_id=session_id,
            objective=objective,
            status=RunStatus.RUNNING,
            model=model,
            workspace=workspace,
        )
        self.repository.upsert_run(run)
        self._emit_jsonl(run.run_id, {
            "type": "run_started",
            "run": run.model_dump(mode="json"),
        })
        self.repository.add_event(
            EventRecord(
                run_id=run.run_id,
                session_id=session_id,
                event_type=EventType.RUN_STARTED,
                title="Run started",
                payload={"objective": objective, "workspace": workspace, "model": model},
            )
        )
        return run

    def event(self, event: EventRecord) -> None:
        self.repository.add_event(event)
        self._emit_jsonl(event.run_id, event.model_dump(mode="json"))

    def file_changed(self, record: FileImpactRecord) -> None:
        self.repository.add_file_impact(record)
        self.repository.add_event(
            EventRecord(
                run_id=record.run_id,
                event_type=EventType.FILE_CHANGED,
                phase=record.phase,
                agent=record.agent,
                title=f"File {record.change_type.value}",
                payload={
                    "path": record.path,
                    "change_type": record.change_type.value,
                    "summary": record.summary,
                },
            )
        )
        self._emit_jsonl(record.run_id, {
            "type": "file_changed",
            "record": record.model_dump(mode="json"),
        })

    def approval_requested(self, record: ApprovalRecord) -> None:
        self.repository.upsert_approval(record)
        self.repository.add_event(
            EventRecord(
                run_id=record.run_id,
                event_type=EventType.APPROVAL_REQUESTED,
                status=record.status.value,
                title=f"Approval requested for {record.tool_name}",
                payload={"approval_id": record.approval_id, "arguments": record.arguments},
            )
        )
        self._emit_jsonl(record.run_id, {
            "type": "approval_requested",
            "record": record.model_dump(mode="json"),
        })

    def approval_resolved(self, approval_id: str, *, run_id: str, tool_name: str, status: ApprovalStatus, arguments: dict[str, Any] | None = None, resolution_note: str | None = None) -> ApprovalRecord:
        record = ApprovalRecord(
            approval_id=approval_id,
            run_id=run_id,
            tool_name=tool_name,
            arguments=arguments or {},
            status=status,
            resolution_note=resolution_note,
        )
        if status != ApprovalStatus.REQUESTED:
            from .models import utc_now
            record.resolved_at = utc_now()
        self.repository.upsert_approval(record)
        self.repository.add_event(
            EventRecord(
                run_id=run_id,
                event_type=EventType.APPROVAL_RESOLVED,
                status=status.value,
                title=f"Approval {status.value}",
                payload={"approval_id": approval_id, "tool_name": tool_name, "resolution_note": resolution_note},
            )
        )
        self._emit_jsonl(run_id, {
            "type": "approval_resolved",
            "record": record.model_dump(mode="json"),
        })
        return record

    def verification_result(self, record: VerificationRecord) -> None:
        self.repository.add_verification(record)
        event_type = EventType.TEST_FINISHED if record.kind == VerificationKind.TEST else EventType.BUILD_FINISHED
        self.repository.add_event(
            EventRecord(
                run_id=record.run_id,
                event_type=event_type,
                status=record.status.value,
                title=f"{record.kind.value} {record.status.value}",
                payload={"command": record.command, "duration_ms": record.duration_ms, "details": record.details},
            )
        )
        self._emit_jsonl(record.run_id, {
            "type": "verification_result",
            "record": record.model_dump(mode="json"),
        })

    def run_finished(self, run: RunRecord, *, status: RunStatus, summary: str | None = None) -> RunRecord:
        from .models import utc_now

        run.status = status
        run.summary = summary
        run.finished_at = utc_now()
        self.repository.upsert_run(run)
        self.repository.add_event(
            EventRecord(
                run_id=run.run_id,
                session_id=run.session_id,
                event_type=EventType.RUN_FINISHED,
                status=status.value,
                title="Run finished",
                payload={"summary": summary},
            )
        )
        self._emit_jsonl(run.run_id, {
            "type": "run_finished",
            "run": run.model_dump(mode="json"),
        })
        return run

    def _emit_jsonl(self, run_id: str, payload: dict[str, Any]) -> None:
        self.config.ensure_directories()
        path = Path(self.config.events_dir) / f"{run_id}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
