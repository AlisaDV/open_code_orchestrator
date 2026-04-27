from __future__ import annotations

from .models import ReviewFinding, ReviewRequest, ReviewResult


class ReviewerAgentRuntime:
    def consult(self, query: str) -> ReviewResult:
        checklist = [
            "Check for behavioral regressions before style issues.",
            "Look for missing negative-path tests.",
            "Look for hidden coupling across modules or services.",
            "Check auth, permissions, validation, and error handling if relevant.",
        ]
        return ReviewResult(
            mode="consult",
            summary=f"Review guidance prepared for query: {query}",
            review_checklist=checklist,
            next_steps=["Inspect changed files and prioritize findings by severity."],
        )

    def generate(self, request: ReviewRequest) -> ReviewResult:
        findings: list[ReviewFinding] = []
        checklist = [
            "Confirm changed flows still satisfy original contract.",
            "Confirm new external dependencies have guardrails and retries.",
            "Confirm tests cover the riskiest changed behavior.",
            "Confirm docs reflect real implemented behavior only.",
        ]

        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()
        if any(token in lowered for token in ["auth", "token", "permission", "role", "security"]):
            findings.append(
                ReviewFinding(
                    severity="high",
                    title="Auth or permission changes need explicit negative-path review",
                    rationale="Security-sensitive changes often regress on unauthorized or partially authorized paths.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Verify unauthorized access is rejected consistently.",
                        "Add tests for insufficient permissions and malformed credentials.",
                    ],
                )
            )
        if any(token in lowered for token in ["integration", "api", "webhook", "oauth", "bitrix", "external"]):
            findings.append(
                ReviewFinding(
                    severity="medium",
                    title="External integration changes should be reviewed for failure handling",
                    rationale="Integration code usually fails on retries, partial responses, or rate limits rather than happy paths.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check retry/backoff and idempotency assumptions.",
                        "Check structured logging around external requests.",
                    ],
                )
            )
        if request.tests_present is False:
            findings.append(
                ReviewFinding(
                    severity="high",
                    title="Changed behavior is not backed by tests",
                    rationale="Without regression tests, future edits can silently break intended behavior.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Add at least one regression or smoke test for the changed flow."],
                )
            )

        if not findings:
            findings.append(
                ReviewFinding(
                    severity="low",
                    title="No obvious risk signature detected from summary alone",
                    rationale="The review request does not expose a strong risk pattern, but code inspection is still required.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect changed files directly and verify tests match the change scope."],
                )
            )

        return ReviewResult(
            mode="generate",
            summary="Review findings scaffold generated from changed scope.",
            findings=findings,
            review_checklist=checklist,
            next_steps=["Read the changed files and validate each finding against actual code paths."],
        )

    def debug(self, problem: str) -> ReviewResult:
        findings = [
            ReviewFinding(
                severity="medium",
                title="Likely review gap led to escaped regression",
                rationale="A production or test failure often means a negative path, state edge case, or integration fallback was not reviewed deeply enough.",
                affected_areas=[],
                recommendations=[
                    "Reconstruct the exact changed behavior that introduced the issue.",
                    "Add a regression test for the failing scenario before fixing it.",
                ],
            )
        ]
        checklist = [
            "Compare expected behavior vs actual behavior.",
            "Identify missing test or missing guardrail.",
            "Check if the regression came from hidden coupling across files.",
        ]
        return ReviewResult(
            mode="debug",
            summary=f"Review-debug guidance prepared for problem: {problem}",
            findings=findings,
            review_checklist=checklist,
            next_steps=["Review the original change set with regression-first focus."],
        )
