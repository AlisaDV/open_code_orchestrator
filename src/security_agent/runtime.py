from __future__ import annotations

from .models import SecurityFinding, SecurityReviewRequest, SecurityReviewResult


class SecurityAgentRuntime:
    def consult(self, query: str) -> SecurityReviewResult:
        checklist = [
            "Check authentication and authorization boundaries.",
            "Check secret handling, env usage, and accidental exposure paths.",
            "Check unsafe input handling, file paths, command execution, and serialization boundaries.",
            "Check external integrations for token scope, callback verification, and replay/idempotency risks.",
        ]
        return SecurityReviewResult(
            mode="consult",
            summary=f"Security review guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Inspect changed flows with exploitability and unauthorized access in mind."],
        )

    def generate(self, request: SecurityReviewRequest) -> SecurityReviewResult:
        findings: list[SecurityFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.auth_touched or any(token in lowered for token in ["auth", "token", "jwt", "role", "permission", "oauth"]):
            findings.append(
                SecurityFinding(
                    severity="high",
                    title="Authentication or authorization changes require explicit negative-path validation",
                    rationale="Security regressions often hide in unauthorized, expired, or malformed credential paths rather than happy paths.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Verify unauthorized requests are rejected consistently.",
                        "Add tests for expired, invalid, and insufficient-scope credentials.",
                    ],
                )
            )
        if request.secrets_present or any(token in lowered for token in ["secret", "webhook", "credential", "api key", "password"]):
            findings.append(
                SecurityFinding(
                    severity="critical",
                    title="Secrets handling needs direct review",
                    rationale="Accidental secret exposure or persistence can become an immediate compromise path.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Confirm secrets are not stored in source-controlled docs, fixtures, or frontend assets.",
                        "Use environment/config indirection and redact logs.",
                    ],
                )
            )
        if request.external_integration or any(token in lowered for token in ["webhook", "callback", "integration", "bitrix", "telegram", "external"]):
            findings.append(
                SecurityFinding(
                    severity="medium",
                    title="External integration trust boundaries should be reviewed",
                    rationale="Callbacks, webhook endpoints, and token-based integrations often need signature validation, replay protection, and least-privilege scope checks.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Verify webhook authenticity and replay protections where applicable.",
                        "Check least-privilege scopes and error handling for external calls.",
                    ],
                )
            )
        if any(token in lowered for token in ["path", "file", "upload", "shell", "command", "subprocess"]):
            findings.append(
                SecurityFinding(
                    severity="high",
                    title="File or command execution paths need boundary review",
                    rationale="Path traversal, arbitrary file write, and command injection risks tend to appear when inputs influence filesystem or shell behavior.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check path normalization and workspace boundaries.",
                        "Check command allow/block policy and shell parameter handling.",
                    ],
                )
            )

        if not findings:
            findings.append(
                SecurityFinding(
                    severity="low",
                    title="No obvious high-risk security signature detected from summary alone",
                    rationale="A direct code review is still needed to validate trust boundaries and data flows.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect code paths for hidden trust assumptions and unvalidated inputs."],
                )
            )

        checklist = [
            "Auth/Authz boundaries",
            "Secrets and credentials exposure",
            "Input validation and unsafe deserialization",
            "File, path, and shell execution boundaries",
            "External callback or webhook trust validation",
        ]
        return SecurityReviewResult(
            mode="generate",
            summary="Security review findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate each finding against actual code paths and add regression tests for security-sensitive flows."],
        )

    def debug(self, problem: str) -> SecurityReviewResult:
        findings = [
            SecurityFinding(
                severity="medium",
                title="Likely trust-boundary or validation miss",
                rationale="Escaped security issues are commonly caused by missing negative-path checks, missing scope validation, or implicit trust in external inputs.",
                recommendations=[
                    "Reconstruct the exact input and permission context of the failure.",
                    "Add a focused regression test for the security-sensitive path.",
                ],
            )
        ]
        checklist = [
            "Reproduce with invalid or unauthorized inputs.",
            "Check secrets/token handling.",
            "Check whether external payloads are trusted too early.",
        ]
        return SecurityReviewResult(
            mode="debug",
            summary=f"Security-debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Review the failing path with explicit trust-boundary mapping."],
        )
