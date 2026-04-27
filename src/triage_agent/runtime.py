from __future__ import annotations

from .models import TriageFinding, TriageRequest, TriageResult


class TriageAgentRuntime:
    def consult(self, query: str) -> TriageResult:
        checklist = [
            "Clarify expected vs actual behavior.",
            "Capture reproduction steps and environment.",
            "Identify whether issue is UI, backend, infra, DB, security, or external integration related.",
            "Decide which specialist should receive the issue next.",
        ]
        return TriageResult(
            mode="consult",
            summary=f"Triage guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Normalize the issue into a reproducible report before assigning work."],
        )

    def generate(self, request: TriageRequest) -> TriageResult:
        lowered = f"{request.title} {request.description} {' '.join(request.area_hints)}".lower()
        findings: list[TriageFinding] = []
        checklist = [
            "Expected vs actual behavior recorded",
            "Environment identified",
            "Reproduction steps validated",
            "Likely owner and specialist selected",
        ]

        if request.ui_involved or any(token in lowered for token in ["button", "page", "form", "ui", "frontend", "redirect"]):
            findings.append(
                TriageFinding(
                    severity="medium",
                    classification="ui-flow-issue",
                    rationale="The issue appears to involve user interaction, browser flow, or screen behavior.",
                    likely_owners=["frontend", "qa"],
                    next_agents=["frontend_ui", "reviewer"],
                    reproduction_gaps=[] if request.reproduction_steps else ["Missing click/type/submit reproduction sequence"],
                )
            )
        if request.external_integration_involved or any(token in lowered for token in ["webhook", "oauth", "api", "bitrix", "integration", "callback"]):
            findings.append(
                TriageFinding(
                    severity="high",
                    classification="integration-issue",
                    rationale="The issue likely touches an external API contract, callback path, or auth/rate-limit behavior.",
                    likely_owners=["integration", "backend"],
                    next_agents=["api_integration", "bitrix24"],
                    reproduction_gaps=[] if request.logs_present else ["Need request/response or callback evidence"],
                )
            )
        if any(token in lowered for token in ["permission", "token", "forbidden", "unauthorized", "secret", "security"]):
            findings.append(
                TriageFinding(
                    severity="high",
                    classification="security-sensitive-issue",
                    rationale="The issue may involve authorization, token validity, or secret handling and should be handled carefully.",
                    likely_owners=["backend", "security"],
                    next_agents=["security", "reviewer"],
                    reproduction_gaps=[] if request.logs_present else ["Need auth context or failing credential path"],
                )
            )
        if any(token in lowered for token in ["migration", "database", "sql", "constraint", "query", "performance"]):
            findings.append(
                TriageFinding(
                    severity="high",
                    classification="database-issue",
                    rationale="The issue likely involves schema, migrations, query behavior, or consistency under load.",
                    likely_owners=["backend", "db"],
                    next_agents=["database", "observability"],
                    reproduction_gaps=[] if request.logs_present else ["Need query/schema/runtime evidence"],
                )
            )
        if any(token in lowered for token in ["deploy", "docker", "startup", "ci", "env", "service down"]):
            findings.append(
                TriageFinding(
                    severity="high",
                    classification="deployment-issue",
                    rationale="The issue likely originates from environment drift, startup order, or deployment configuration.",
                    likely_owners=["platform", "backend"],
                    next_agents=["devops", "observability"],
                    reproduction_gaps=[] if request.environment else ["Need exact environment and startup context"],
                )
            )

        if not findings:
            findings.append(
                TriageFinding(
                    severity="low",
                    classification="general-issue",
                    rationale="Not enough structured evidence to classify strongly yet.",
                    likely_owners=["reviewer"],
                    next_agents=["reviewer"],
                    reproduction_gaps=["Need more structured reproduction and environment details"],
                )
            )

        return TriageResult(
            mode="generate",
            summary="Issue triage scaffold generated from report details.",
            findings=findings,
            checklist=checklist,
            next_steps=["Assign the issue to the first matching specialist and collect missing evidence immediately."],
        )

    def debug(self, problem: str) -> TriageResult:
        findings = [
            TriageFinding(
                severity="medium",
                classification="triage-gap",
                rationale="The issue likely lacked enough structured evidence at intake, causing slower routing or wrong ownership.",
                likely_owners=["triage"],
                next_agents=["reviewer", "observability"],
                reproduction_gaps=["Clarify exact environment, expected behavior, and first failing step"],
            )
        ]
        checklist = [
            "Was the issue classified to the correct subsystem?",
            "Were reproduction steps complete enough?",
            "Were logs, traces, or screenshots attached?",
        ]
        return TriageResult(
            mode="debug",
            summary=f"Triage-debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Refine the incident template so the same issue type is routed faster next time."],
        )
