from __future__ import annotations

from .models import BusinessRuleFinding, BusinessRuleReviewRequest, BusinessRuleReviewResult


class BusinessRulesAgentRuntime:
    def consult(self, query: str) -> BusinessRuleReviewResult:
        checklist = [
            "Check domain invariants and forbidden state combinations.",
            "Check lifecycle transitions and who is allowed to trigger them.",
            "Check whether linked entities remain consistent after updates or side effects.",
            "Check whether the implementation still matches the real business process and not only old code assumptions.",
        ]
        return BusinessRuleReviewResult(
            mode="consult",
            summary=f"Business rules guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Review the behavior as a domain process, not only as code paths."],
        )

    def generate(self, request: BusinessRuleReviewRequest) -> BusinessRuleReviewResult:
        findings: list[BusinessRuleFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.state_transition_changed or any(token in lowered for token in ["status", "stage", "transition", "lifecycle", "state"]):
            findings.append(
                BusinessRuleFinding(
                    severity="high",
                    title="State transition changes require invariant review",
                    rationale="Domain bugs often appear when a technically allowed transition violates process rules or skips mandatory intermediate states.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check which transitions are allowed, forbidden, or conditional.",
                        "Check whether role and timing restrictions are preserved.",
                    ],
                )
            )
        if request.approval_logic_changed or any(token in lowered for token in ["approve", "approval", "delegate", "confirm", "escalate"]):
            findings.append(
                BusinessRuleFinding(
                    severity="high",
                    title="Approval-related changes should be reviewed against real process policy",
                    rationale="Approval flows are easy to break by preserving technical flow while changing who is allowed to approve, delegate, or finalize.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check actor permissions and ownership semantics.",
                        "Check whether approval side effects are consistent across all related entities.",
                    ],
                )
            )
        if request.cross_entity_consistency_changed or any(token in lowered for token in ["link", "bind", "sync", "relation", "consistency"]):
            findings.append(
                BusinessRuleFinding(
                    severity="medium",
                    title="Cross-entity rule changes need consistency review",
                    rationale="Business semantics often depend on multiple entities staying aligned, not on a single record being valid in isolation.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check whether dependent entities stay aligned after create/update/delete.",
                        "Check whether downstream workflows still receive the expected signals.",
                    ],
                )
            )
        if request.external_business_process_changed or any(token in lowered for token in ["crm", "bitrix", "workflow", "process", "integration"]):
            findings.append(
                BusinessRuleFinding(
                    severity="medium",
                    title="External process integration may drift from actual business meaning",
                    rationale="Integrations often preserve transport correctness while silently changing the semantics expected by users or downstream systems.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check whether external system field mapping still matches the intended business meaning.",
                        "Check whether process timing and ownership assumptions stayed valid.",
                    ],
                )
            )

        if not findings:
            findings.append(
                BusinessRuleFinding(
                    severity="low",
                    title="No obvious high-risk business-rule signature detected from summary alone",
                    rationale="Business rule review still requires reading the actual process and invariants behind the code.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect domain rules, actor permissions, and lifecycle semantics directly."],
                )
            )

        checklist = [
            "State invariants",
            "Approval policy",
            "Cross-entity consistency",
            "Process timing",
            "External semantic alignment",
        ]
        return BusinessRuleReviewResult(
            mode="generate",
            summary="Business-rules findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate findings against the actual business process, not just existing code behavior."],
        )

    def debug(self, problem: str) -> BusinessRuleReviewResult:
        findings = [
            BusinessRuleFinding(
                severity="medium",
                title="Likely domain-process mismatch",
                rationale="Business bugs often come from hidden rule drift: the code still runs, but the real process semantics have been broken.",
                recommendations=[
                    "Compare expected business workflow with actual implemented transitions and side effects.",
                    "Check whether an invariant or actor rule was dropped implicitly.",
                ],
            )
        ]
        checklist = [
            "What state or policy should have prevented this?",
            "What actor was allowed to do something that should not be allowed?",
            "Which related entity became inconsistent with the main object?",
        ]
        return BusinessRuleReviewResult(
            mode="debug",
            summary=f"Business-rules debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Trace the issue through the business process model before changing implementation details."],
        )
