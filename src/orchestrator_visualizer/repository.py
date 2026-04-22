from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

from .config import VisualizerConfig
from .db import connect, init_db
from pathlib import Path

from .models import ApprovalRecord, BrowserSmokeReportRecord, EventRecord, FileImpactRecord, RunRecord, VerificationRecord
from .repository_types import FileImpactAggregate, RunSummary


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class VisualizerRepository:
    def __init__(self, config: VisualizerConfig):
        self.config = config
        init_db(config)

    def upsert_run(self, run: RunRecord) -> None:
        with connect(self.config) as conn:
            conn.execute(
                """
                insert into runs (run_id, session_id, objective, status, started_at, finished_at, model, workspace, summary)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(run_id) do update set
                    session_id=excluded.session_id,
                    objective=excluded.objective,
                    status=excluded.status,
                    started_at=excluded.started_at,
                    finished_at=excluded.finished_at,
                    model=excluded.model,
                    workspace=excluded.workspace,
                    summary=excluded.summary
                """,
                (
                    run.run_id,
                    run.session_id,
                    run.objective,
                    run.status.value,
                    _iso(run.started_at),
                    _iso(run.finished_at),
                    run.model,
                    run.workspace,
                    run.summary,
                ),
            )
            conn.commit()

    def add_event(self, event: EventRecord) -> None:
        with connect(self.config) as conn:
            conn.execute(
                """
                insert into events (event_id, run_id, session_id, event_type, phase, agent, status, ts, title, payload_json)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.run_id,
                    event.session_id,
                    event.event_type.value,
                    event.phase,
                    event.agent,
                    event.status,
                    _iso(event.ts),
                    event.title,
                    json.dumps(event.payload, ensure_ascii=True),
                ),
            )
            conn.commit()

    def add_file_impact(self, record: FileImpactRecord) -> None:
        with connect(self.config) as conn:
            conn.execute(
                """
                insert into file_impacts (run_id, event_id, path, change_type, summary, agent, phase, ts)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.run_id,
                    record.event_id,
                    record.path,
                    record.change_type.value,
                    record.summary,
                    record.agent,
                    record.phase,
                    _iso(record.ts),
                ),
            )
            conn.commit()

    def upsert_approval(self, record: ApprovalRecord) -> None:
        with connect(self.config) as conn:
            conn.execute(
                """
                insert into approvals (approval_id, run_id, tool_name, arguments_json, status, requested_at, resolved_at, resolution_note)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(approval_id) do update set
                    tool_name=excluded.tool_name,
                    arguments_json=excluded.arguments_json,
                    status=excluded.status,
                    requested_at=excluded.requested_at,
                    resolved_at=excluded.resolved_at,
                    resolution_note=excluded.resolution_note
                """,
                (
                    record.approval_id,
                    record.run_id,
                    record.tool_name,
                    json.dumps(record.arguments, ensure_ascii=True),
                    record.status.value,
                    _iso(record.requested_at),
                    _iso(record.resolved_at),
                    record.resolution_note,
                ),
            )
            conn.commit()

    def add_verification(self, record: VerificationRecord) -> None:
        with connect(self.config) as conn:
            conn.execute(
                """
                insert into verification_results (run_id, kind, command, status, duration_ms, details_json, ts)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.run_id,
                    record.kind.value,
                    record.command,
                    record.status.value,
                    record.duration_ms,
                    json.dumps(record.details, ensure_ascii=True),
                    _iso(record.ts),
                ),
            )
            conn.commit()

    def upsert_browser_smoke_report(self, report: BrowserSmokeReportRecord) -> None:
        with connect(self.config) as conn:
            conn.execute(
                """
                insert into browser_smoke_reports (report_id, source_path, target_url, started_at, finished_at, total, passed, failed, report_json)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(report_id) do update set
                    source_path=excluded.source_path,
                    target_url=excluded.target_url,
                    started_at=excluded.started_at,
                    finished_at=excluded.finished_at,
                    total=excluded.total,
                    passed=excluded.passed,
                    failed=excluded.failed,
                    report_json=excluded.report_json
                """,
                (
                    report.report_id,
                    report.source_path,
                    report.target_url,
                    _iso(report.started_at),
                    _iso(report.finished_at),
                    report.total,
                    report.passed,
                    report.failed,
                    json.dumps(report.model_dump(mode="json"), ensure_ascii=True),
                ),
            )
            conn.commit()

    def import_browser_smoke_report_file(self, file_path: str | Path) -> BrowserSmokeReportRecord:
        path = Path(file_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        report = BrowserSmokeReportRecord.model_validate({**payload, "sourcePath": str(path)})
        self.upsert_browser_smoke_report(report)
        return report

    def list_runs(self) -> list[RunSummary]:
        with connect(self.config) as conn:
            rows = conn.execute(
                """
                select
                    r.run_id,
                    r.status,
                    r.objective,
                    r.started_at,
                    r.finished_at,
                    (select count(*) from events e where e.run_id = r.run_id) as event_count,
                    (select count(distinct f.path) from file_impacts f where f.run_id = r.run_id) as file_count,
                    (select count(*) from approvals a where a.run_id = r.run_id) as approval_count,
                    (select count(*) from verification_results v where v.run_id = r.run_id) as verification_count
                from runs r
                order by r.started_at desc
                """
            ).fetchall()
        return [RunSummary.model_validate(dict(row)) for row in rows]

    def list_browser_smoke_reports(self) -> list[BrowserSmokeReportRecord]:
        with connect(self.config) as conn:
            rows = conn.execute(
                "select report_json from browser_smoke_reports order by finished_at desc, started_at desc"
            ).fetchall()
        return [BrowserSmokeReportRecord.model_validate(json.loads(row["report_json"])) for row in rows]

    def latest_browser_smoke_report(self) -> BrowserSmokeReportRecord | None:
        reports = self.list_browser_smoke_reports()
        return reports[0] if reports else None

    def get_run(self, run_id: str) -> RunRecord | None:
        with connect(self.config) as conn:
            row = conn.execute(
                "select * from runs where run_id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return RunRecord(
            run_id=row["run_id"],
            session_id=row["session_id"],
            objective=row["objective"],
            status=row["status"],
            started_at=datetime.fromisoformat(row["started_at"]),
            finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
            model=row["model"],
            workspace=row["workspace"],
            summary=row["summary"],
        )

    def list_events(self, run_id: str) -> list[EventRecord]:
        with connect(self.config) as conn:
            rows = conn.execute(
                "select * from events where run_id = ? order by ts asc",
                (run_id,),
            ).fetchall()
        return [
            EventRecord(
                event_id=row["event_id"],
                run_id=row["run_id"],
                session_id=row["session_id"],
                event_type=row["event_type"],
                phase=row["phase"],
                agent=row["agent"],
                status=row["status"],
                ts=datetime.fromisoformat(row["ts"]),
                title=row["title"],
                payload=json.loads(row["payload_json"]),
            )
            for row in rows
        ]

    def aggregate_file_impacts(self, run_id: str) -> list[FileImpactAggregate]:
        with connect(self.config) as conn:
            rows = conn.execute(
                "select * from file_impacts where run_id = ? order by ts asc",
                (run_id,),
            ).fetchall()

        grouped: dict[str, dict[str, object]] = defaultdict(
            lambda: {
                "change_count": 0,
                "agents": set(),
                "phases": set(),
                "last_change_type": None,
                "last_summary": None,
            }
        )

        for row in rows:
            entry = grouped[row["path"]]
            entry["change_count"] = int(entry["change_count"]) + 1
            if row["agent"]:
                entry["agents"].add(row["agent"])
            if row["phase"]:
                entry["phases"].add(row["phase"])
            entry["last_change_type"] = row["change_type"]
            entry["last_summary"] = row["summary"]

        return [
            FileImpactAggregate(
                path=path,
                change_count=int(values["change_count"]),
                agents=sorted(values["agents"]),
                phases=sorted(values["phases"]),
                last_change_type=values["last_change_type"],
                last_summary=values["last_summary"],
            )
            for path, values in sorted(grouped.items())
        ]

    def list_approvals(self, run_id: str) -> list[ApprovalRecord]:
        with connect(self.config) as conn:
            rows = conn.execute(
                "select * from approvals where run_id = ? order by requested_at asc",
                (run_id,),
            ).fetchall()
        return [
            ApprovalRecord(
                approval_id=row["approval_id"],
                run_id=row["run_id"],
                tool_name=row["tool_name"],
                arguments=json.loads(row["arguments_json"] or "{}"),
                status=row["status"],
                requested_at=datetime.fromisoformat(row["requested_at"]),
                resolved_at=datetime.fromisoformat(row["resolved_at"]) if row["resolved_at"] else None,
                resolution_note=row["resolution_note"],
            )
            for row in rows
        ]

    def list_verification_results(self, run_id: str) -> list[VerificationRecord]:
        with connect(self.config) as conn:
            rows = conn.execute(
                "select * from verification_results where run_id = ? order by ts asc",
                (run_id,),
            ).fetchall()
        return [
            VerificationRecord(
                run_id=row["run_id"],
                kind=row["kind"],
                status=row["status"],
                command=row["command"],
                duration_ms=row["duration_ms"],
                details=json.loads(row["details_json"] or "{}"),
                ts=datetime.fromisoformat(row["ts"]),
            )
            for row in rows
        ]
