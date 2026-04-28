from __future__ import annotations

from .models import DataSyncFinding, DataSyncReviewRequest, DataSyncReviewResult


class DataSyncAgentRuntime:
    def consult(self, query: str) -> DataSyncReviewResult:
        checklist = [
            "Check sync direction and source-of-truth assumptions.",
            "Check idempotency, deduplication, and conflict handling.",
            "Check pagination or batch cursor continuity.",
            "Check checkpointing and restart behavior after partial failure.",
            "Check reconciliation and drift detection paths.",
        ]
        return DataSyncReviewResult(
            mode="consult",
            summary=f"Data sync guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Inspect the sync as a long-running stateful process, not as isolated API calls."],
        )

    def generate(self, request: DataSyncReviewRequest) -> DataSyncReviewResult:
        findings: list[DataSyncFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.import_flow or request.export_flow or any(token in lowered for token in ["sync", "import", "export", "batch", "cursor"]):
            findings.append(
                DataSyncFinding(
                    severity="high",
                    title="Sync flow should be reviewed for restartability and correctness",
                    rationale="Data pipelines usually fail on partial progress, duplicate delivery, or state drift rather than on happy-path transport.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check batch boundaries, cursor handling, and resume semantics.",
                        "Check source-of-truth and conflict resolution assumptions.",
                    ],
                )
            )
        if request.checkpointing_present is False or any(token in lowered for token in ["resume", "checkpoint", "offset", "marker"]):
            findings.append(
                DataSyncFinding(
                    severity="high",
                    title="Checkpointing and partial failure recovery need explicit review",
                    rationale="Without explicit progress markers, recovery after interruption can skip or duplicate data.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Verify persisted progress markers or replay-safe restart strategy.",
                        "Check failure injection path for mid-batch interruption.",
                    ],
                )
            )
        if request.dedup_logic_present is False or any(token in lowered for token in ["duplicate", "dedup", "idempotent", "upsert"]):
            findings.append(
                DataSyncFinding(
                    severity="medium",
                    title="Duplicate handling and idempotency need review",
                    rationale="Many sync bugs surface as duplicated entities or conflicting updates after retries or reruns.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check natural keys, idempotency keys, or upsert rules.",
                        "Check whether retried batches can create duplicates.",
                    ],
                )
            )
        if request.reconciliation_present is False or any(token in lowered for token in ["reconcile", "drift", "consistency check", "backfill"]):
            findings.append(
                DataSyncFinding(
                    severity="medium",
                    title="Missing reconciliation or drift-detection path should be reviewed",
                    rationale="A sync can appear successful while silently diverging from the source unless there is a verification strategy.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check whether counts, hashes, timestamps, or periodic compare jobs exist.",
                        "Check whether drift can be detected without full manual audit.",
                    ],
                )
            )

        if not findings:
            findings.append(
                DataSyncFinding(
                    severity="low",
                    title="No obvious high-risk sync signature detected from summary alone",
                    rationale="Sync correctness still requires direct inspection of batching, restart, and dedup behavior.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect state progression and reconciliation logic directly."],
                )
            )

        checklist = [
            "Source of truth",
            "Checkpointing",
            "Dedup/idempotency",
            "Retry and resume safety",
            "Reconciliation/drift detection",
        ]
        return DataSyncReviewResult(
            mode="generate",
            summary="Data sync findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate findings against actual sync state machine and recovery behavior."],
        )

    def debug(self, problem: str) -> DataSyncReviewResult:
        findings = [
            DataSyncFinding(
                severity="medium",
                title="Likely sync state or recovery mismatch",
                rationale="Escaped sync problems usually come from duplicate processing, missing checkpoints, or drift that no one measured.",
                recommendations=[
                    "Check the last persisted progress marker and replay semantics.",
                    "Check dedup and conflict resolution behavior under retry.",
                ],
            )
        ]
        checklist = [
            "Was progress persisted safely?",
            "Can the same batch replay without duplication?",
            "Is there evidence of drift between source and destination?",
        ]
        return DataSyncReviewResult(
            mode="debug",
            summary=f"Data sync debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Trace the bug through progress markers, dedup rules, and reconciliation outputs."],
        )
