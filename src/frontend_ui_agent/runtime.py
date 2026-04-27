from __future__ import annotations

from .models import FrontendUiFinding, FrontendUiReviewRequest, FrontendUiReviewResult


class FrontendUiAgentRuntime:
    def consult(self, query: str) -> FrontendUiReviewResult:
        checklist = [
            "Check whether the primary user journey is still completable.",
            "Check form behavior, validation feedback, loading states, and empty states.",
            "Check navigation and role-based redirection paths.",
            "Check accessibility basics: labels, focus, semantics, and readable feedback.",
        ]
        return FrontendUiReviewResult(
            mode="consult",
            summary=f"Frontend UI guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Review the UI from the user's task flow perspective, not only from component structure."],
        )

    def generate(self, request: FrontendUiReviewRequest) -> FrontendUiReviewResult:
        findings: list[FrontendUiFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.forms_touched or any(token in lowered for token in ["form", "submit", "input", "validation", "field"]):
            findings.append(
                FrontendUiFinding(
                    severity="high",
                    title="Form flow changes need validation and submission-path review",
                    rationale="UI bugs often hide in disabled states, missing validation messages, or submit mechanics that appear clickable but do not complete the action.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check valid, invalid, and partially filled form states.",
                        "Check that submit action really triggers network flow and updates UI state.",
                    ],
                )
            )
        if request.navigation_touched or any(token in lowered for token in ["redirect", "route", "navigation", "menu", "page"]):
            findings.append(
                FrontendUiFinding(
                    severity="medium",
                    title="Navigation changes should be reviewed for role and state transitions",
                    rationale="Broken redirects or hidden navigation mismatches often strand users in incomplete flows.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check post-login and role-based navigation.",
                        "Check whether refresh or direct URL access still lands on correct screens.",
                    ],
                )
            )
        if request.accessibility_touched or any(token in lowered for token in ["a11y", "accessibility", "label", "focus", "screen reader"]):
            findings.append(
                FrontendUiFinding(
                    severity="medium",
                    title="Accessibility-sensitive changes need interaction review",
                    rationale="Accessible structure tends to regress silently when visual edits remove labels, semantics, or feedback discoverability.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check labels, focus order, button semantics, and readable status messages.",
                        "Check that feedback is not color-only or position-only.",
                    ],
                )
            )
        if request.browser_flow_touched or any(token in lowered for token in ["ui", "browser", "click", "smoke", "flow"]):
            findings.append(
                FrontendUiFinding(
                    severity="high",
                    title="Browser flow changes should be reviewed against real interaction paths",
                    rationale="Component-level correctness is not enough if the actual click/type/submit sequence fails in the browser.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Run browser smoke or Playwright scenario against the changed flow.",
                        "Check console/network artifacts when the visible UI looks correct but flow still fails.",
                    ],
                )
            )

        if not findings:
            findings.append(
                FrontendUiFinding(
                    severity="low",
                    title="No obvious high-risk UI signature detected from summary alone",
                    rationale="UI review still requires checking real user flows and state transitions.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect the changed flow in the browser and verify state, feedback, and navigation."],
                )
            )

        checklist = [
            "Primary user journey",
            "Form submit and validation",
            "Navigation and role transitions",
            "Feedback/loading/empty/error states",
            "Accessibility basics",
        ]
        return FrontendUiReviewResult(
            mode="generate",
            summary="Frontend UI findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate findings against the real browser flow, not only static code review."],
        )

    def debug(self, problem: str) -> FrontendUiReviewResult:
        findings = [
            FrontendUiFinding(
                severity="medium",
                title="Likely broken user journey or invisible state mismatch",
                rationale="UI regressions often come from state changes that do not surface correctly through visible feedback, navigation, or actual form submission behavior.",
                recommendations=[
                    "Reproduce the full click/type/submit path in browser automation.",
                    "Check network and console output along the exact failing path.",
                ],
            )
        ]
        checklist = [
            "Can the user finish the journey end-to-end?",
            "Do visible states match network reality?",
            "Does feedback appear in the right place and time?",
        ]
        return FrontendUiReviewResult(
            mode="debug",
            summary=f"Frontend UI debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Inspect the failing UI path with browser smoke and step-level artifacts."],
        )
