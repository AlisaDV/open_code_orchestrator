from __future__ import annotations

from .models import MigrationFinding, MigrationReviewRequest, MigrationReviewResult


class MigrationAgentRuntime:
    def consult(self, query: str) -> MigrationReviewResult:
        checklist = [
            "Check upgrade order and dependency compatibility windows.",
            "Check deprecations, renamed settings, and removed behaviors.",
            "Check whether old and new runtime versions must coexist during rollout.",
            "Check rollback feasibility after partial migration.",
        ]
        return MigrationReviewResult(
            mode="consult",
            summary=f"Migration guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Treat migration as a staged compatibility problem, not just a version bump."],
        )

    def generate(self, request: MigrationReviewRequest) -> MigrationReviewResult:
        findings: list[MigrationFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.dependency_upgrade or any(token in lowered for token in ["upgrade", "version", "dependency", "framework", "sdk"]):
            findings.append(
                MigrationFinding(
                    severity="high",
                    title="Dependency upgrade requires compatibility and transitive impact review",
                    rationale="Version upgrades often break at integration boundaries, transitive APIs, or runtime assumptions rather than at import time.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check release notes, deprecated APIs, and transitive dependency behavior.",
                        "Check whether build/test/runtime environments all use the same upgraded dependency graph.",
                    ],
                )
            )
        if request.config_upgrade or any(token in lowered for token in ["config", "setting", "env", "flag", "profile"]):
            findings.append(
                MigrationFinding(
                    severity="medium",
                    title="Configuration migration needs old-to-new mapping review",
                    rationale="Migrations often fail because code was upgraded but runtime configuration semantics changed silently.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check renamed, removed, or newly required settings.",
                        "Check defaults changed by the upgraded runtime or framework.",
                    ],
                )
            )
        if request.api_contract_upgrade or any(token in lowered for token in ["api", "contract", "schema", "response", "payload"]):
            findings.append(
                MigrationFinding(
                    severity="high",
                    title="API contract migration should be reviewed for backward compatibility",
                    rationale="Consumers often break on field removals, type changes, or altered response timing more than on obvious syntax changes.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check whether old consumers still work during rollout.",
                        "Check compatibility shims or phased contract changes if needed.",
                    ],
                )
            )
        if request.deprecation_removal or any(token in lowered for token in ["deprecated", "legacy", "remove old", "drop support"]):
            findings.append(
                MigrationFinding(
                    severity="medium",
                    title="Deprecation removal needs consumer and rollout review",
                    rationale="Removing old paths is correct long-term, but can break forgotten consumers or old persisted states.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check whether any external or internal consumers still depend on the legacy path.",
                        "Check whether persisted data or configs require one-time conversion.",
                    ],
                )
            )

        if not findings:
            findings.append(
                MigrationFinding(
                    severity="low",
                    title="No obvious high-risk migration signature detected from summary alone",
                    rationale="Migration review still requires explicit compatibility analysis and staged rollout reasoning.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect compatibility boundaries, rollout order, and rollback assumptions directly."],
                )
            )

        checklist = [
            "Dependency compatibility",
            "Deprecated behavior removal",
            "Config mapping",
            "Contract backward compatibility",
            "Rollback and staged rollout",
        ]
        return MigrationReviewResult(
            mode="generate",
            summary="Migration findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate findings against real upgrade notes, runtime config, and rollout sequence."],
        )

    def debug(self, problem: str) -> MigrationReviewResult:
        findings = [
            MigrationFinding(
                severity="medium",
                title="Likely compatibility-window or removed-behavior mismatch",
                rationale="Migration failures usually come from an assumption that the new version is a drop-in replacement when some runtime, config, or contract detail actually changed.",
                recommendations=[
                    "Check release notes and deprecated/removed behaviors.",
                    "Check whether old and new components had to coexist during rollout.",
                ],
            )
        ]
        checklist = [
            "Which assumption changed between old and new versions?",
            "Is there config or contract drift?",
            "Could the failure be caused by mixed-version rollout?",
        ]
        return MigrationReviewResult(
            mode="debug",
            summary=f"Migration-debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Trace the issue through version, config, and compatibility boundaries before patching symptoms."],
        )
