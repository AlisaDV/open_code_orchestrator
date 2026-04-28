from __future__ import annotations

from .models import ReleaseFinding, ReleaseReviewRequest, ReleaseReviewResult


class ReleaseAgentRuntime:
    def consult(self, query: str) -> ReleaseReviewResult:
        checklist = [
            "Check that the changed behavior is tested and documented.",
            "Check rollout prerequisites and migration needs.",
            "Check observability and rollback readiness.",
            "Check whether user-facing or operator-facing release notes are needed.",
        ]
        return ReleaseReviewResult(
            mode="consult",
            summary=f"Release guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Treat release readiness as an operational decision, not only a code-complete decision."],
        )

    def generate(self, request: ReleaseReviewRequest) -> ReleaseReviewResult:
        findings: list[ReleaseFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.tests_green is False:
            findings.append(
                ReleaseFinding(
                    severity="critical",
                    title="Release should not proceed while verification is failing",
                    rationale="A release without green verification has an elevated chance of immediate rollback or incident creation.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Resolve failing tests or explicitly narrow release scope before rollout."],
                )
            )
        if request.docs_updated is False or any(token in lowered for token in ["operator", "runbook", "docs", "release notes"]):
            findings.append(
                ReleaseFinding(
                    severity="medium",
                    title="Release documentation and operator notes need review",
                    rationale="Operational confusion after release often comes from missing rollout notes, config changes, or changed user behavior not being documented.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Update release notes and runbooks for changed behavior.",
                        "Document any new env vars, flags, or operational steps.",
                    ],
                )
            )
        if request.migrations_present or any(token in lowered for token in ["migration", "schema", "deploy order"]):
            findings.append(
                ReleaseFinding(
                    severity="high",
                    title="Migration-bearing release requires rollout order review",
                    rationale="Releases that change data contracts need explicit sequencing and failure planning.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check migration timing relative to application deployment.",
                        "Check backward compatibility during rollout window.",
                    ],
                )
            )
        if request.rollback_plan_present is False or any(token in lowered for token in ["rollback", "feature flag", "fallback"]):
            findings.append(
                ReleaseFinding(
                    severity="high",
                    title="Rollback or fallback path should be explicit",
                    rationale="Without a rollback path, even a small release issue can become a prolonged outage or manual recovery event.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Document rollback steps or feature-flag disable path.",
                        "Check whether data migrations are reversible or mitigated.",
                    ],
                )
            )

        if not findings:
            findings.append(
                ReleaseFinding(
                    severity="low",
                    title="No obvious release blocker detected from summary alone",
                    rationale="Final release readiness still needs explicit operational sign-off.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Run through release checklist and verify rollout context before shipping."],
                )
            )

        checklist = [
            "Verification green",
            "Docs/runbooks updated",
            "Migration order understood",
            "Rollback path present",
            "Operational visibility after release",
        ]
        return ReleaseReviewResult(
            mode="generate",
            summary="Release readiness findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Convert findings into explicit go/no-go release checklist before rollout."],
        )

    def debug(self, problem: str) -> ReleaseReviewResult:
        findings = [
            ReleaseFinding(
                severity="medium",
                title="Likely release-readiness gap",
                rationale="Release incidents often happen because rollout assumptions, migration timing, or rollback options were incomplete rather than because code was never tested locally.",
                recommendations=[
                    "Reconstruct the exact release sequence and compare it with the intended checklist.",
                    "Check whether rollback or mitigation existed and was usable in practice.",
                ],
            )
        ]
        checklist = [
            "Was there a green verification signal before release?",
            "Were docs and env changes communicated?",
            "Did rollout order match the assumptions?",
            "Could rollback have been executed quickly?",
        ]
        return ReleaseReviewResult(
            mode="debug",
            summary=f"Release-debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Turn the incident into a stricter release gate or checklist item."],
        )
