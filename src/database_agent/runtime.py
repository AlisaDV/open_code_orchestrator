from __future__ import annotations

from .models import DatabaseFinding, DatabaseReviewRequest, DatabaseReviewResult


class DatabaseAgentRuntime:
    def consult(self, query: str) -> DatabaseReviewResult:
        checklist = [
            "Check whether schema changes are backward-compatible enough for the deployment path.",
            "Check whether indexes still match read and write patterns.",
            "Check migration ordering, nullability, defaults, and data backfill needs.",
            "Check query shape, join fan-out, and consistency guarantees.",
        ]
        return DatabaseReviewResult(
            mode="consult",
            summary=f"Database review guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Inspect schema, migrations, and affected queries together rather than in isolation."],
        )

    def generate(self, request: DatabaseReviewRequest) -> DatabaseReviewResult:
        findings: list[DatabaseFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.schema_changed or any(token in lowered for token in ["schema", "table", "column", "entity", "relation", "constraint"]):
            findings.append(
                DatabaseFinding(
                    severity="high",
                    title="Schema change requires migration and rollback review",
                    rationale="Schema edits can break reads/writes, deployments, and existing data if not paired with safe migration strategy.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Verify migration order, nullability, defaults, and backfill assumptions.",
                        "Check whether old application versions can coexist during rollout.",
                    ],
                )
            )
        if request.migration_present is False and (request.schema_changed or "migration" in lowered):
            findings.append(
                DatabaseFinding(
                    severity="critical",
                    title="Schema-related change appears to lack explicit migration handling",
                    rationale="Direct schema drift without controlled migration is a common source of deployment failure and data inconsistency.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Add explicit migration or document why runtime schema generation is safe here.",
                    ],
                )
            )
        if request.query_changed or any(token in lowered for token in ["query", "repository", "join", "list", "search", "filter"]):
            findings.append(
                DatabaseFinding(
                    severity="medium",
                    title="Changed query paths should be reviewed for index fit and fan-out",
                    rationale="A query can be functionally correct but still become an operational bottleneck after data volume grows.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check sort/filter/index alignment.",
                        "Check for N+1 patterns and unnecessary wide loads.",
                    ],
                )
            )
        if any(token in lowered for token in ["delete", "cascade", "foreign key", "ownership", "consistency"]):
            findings.append(
                DatabaseFinding(
                    severity="high",
                    title="Delete and consistency semantics need explicit review",
                    rationale="Relationship changes often regress through broken cleanup order, missing cascades, or orphaned references.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Review FK direction, cleanup ordering, and orphan handling.",
                        "Add tests around delete/update side effects.",
                    ],
                )
            )

        if not findings:
            findings.append(
                DatabaseFinding(
                    severity="low",
                    title="No obvious high-risk DB signature detected from summary alone",
                    rationale="Database review still needs direct inspection of schema and query paths.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect migrations, repositories, and entity relationships directly."],
                )
            )

        checklist = [
            "Schema compatibility",
            "Migration safety",
            "Index/query alignment",
            "Delete/cascade/orphan handling",
            "Operational performance after data growth",
        ]
        return DatabaseReviewResult(
            mode="generate",
            summary="Database review findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate findings against actual entity, migration, and query changes."],
        )

    def debug(self, problem: str) -> DatabaseReviewResult:
        findings = [
            DatabaseFinding(
                severity="medium",
                title="Likely database contract or consistency gap",
                rationale="Escaped DB issues often come from migration mismatch, hidden FK coupling, or query shape drift.",
                recommendations=[
                    "Compare runtime schema with expected application schema.",
                    "Reproduce on realistic data volume if performance-related.",
                ],
            )
        ]
        checklist = [
            "Check migration history and current schema.",
            "Check query filters and joins.",
            "Check delete/update side effects and orphan records.",
        ]
        return DatabaseReviewResult(
            mode="debug",
            summary=f"Database-debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Trace the failure to schema, migration, or query behavior before patching symptoms."],
        )
