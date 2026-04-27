from __future__ import annotations

from .models import ApiIntegrationFinding, ApiIntegrationReviewRequest, ApiIntegrationReviewResult


class ApiIntegrationAgentRuntime:
    def consult(self, query: str) -> ApiIntegrationReviewResult:
        checklist = [
            "Check auth mode and token lifecycle.",
            "Check retries, backoff, and rate-limit handling.",
            "Check idempotency on create/update flows.",
            "Check pagination, partial reads, and sync continuation logic.",
            "Check callback/webhook verification and replay protection.",
        ]
        return ApiIntegrationReviewResult(
            mode="consult",
            summary=f"API integration guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Inspect the integration as a failure-prone distributed system, not as a single request."],
        )

    def generate(self, request: ApiIntegrationReviewRequest) -> ApiIntegrationReviewResult:
        findings: list[ApiIntegrationFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.oauth_touched or any(token in lowered for token in ["oauth", "token", "refresh token", "client secret"]):
            findings.append(
                ApiIntegrationFinding(
                    severity="high",
                    title="OAuth or token lifecycle changes need failure-path review",
                    rationale="Integration outages often come from refresh flow failures, scope drift, or token misuse rather than main request formatting.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check refresh path, token expiry handling, and scope assumptions.",
                        "Check that secrets never move into client-facing code or logs.",
                    ],
                )
            )
        if request.webhook_touched or any(token in lowered for token in ["webhook", "callback", "signature", "event delivery"]):
            findings.append(
                ApiIntegrationFinding(
                    severity="high",
                    title="Webhook or callback path needs trust and replay review",
                    rationale="Inbound integrations often fail on authenticity, retries, duplicate delivery, or ordering assumptions.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check source verification, replay protection, and duplicate event handling.",
                        "Check whether callback processing is idempotent and safe to retry.",
                    ],
                )
            )
        if request.retry_logic_touched or any(token in lowered for token in ["retry", "backoff", "rate limit", "429", "503"]):
            findings.append(
                ApiIntegrationFinding(
                    severity="medium",
                    title="Retry logic should be reviewed for idempotency and amplification risk",
                    rationale="Bad retry logic can create duplicate writes or make rate-limit incidents worse.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check retryable status codes and backoff policy.",
                        "Check create/update operations for idempotent behavior under retry.",
                    ],
                )
            )
        if request.pagination_touched or any(token in lowered for token in ["pagination", "cursor", "page", "batch sync"]):
            findings.append(
                ApiIntegrationFinding(
                    severity="medium",
                    title="Pagination and sync iteration need completeness review",
                    rationale="Integrations often silently drop data when cursors, next-page tokens, or partial read restarts are mishandled.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check cursor or next-page consumption logic.",
                        "Check restart/resume behavior after partial failure.",
                    ],
                )
            )

        if not findings:
            findings.append(
                ApiIntegrationFinding(
                    severity="low",
                    title="No obvious high-risk integration signature detected from summary alone",
                    rationale="Integration review still requires direct inspection of request/response handling and failure paths.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect auth, retries, callbacks, and sync behavior directly in code."],
                )
            )

        checklist = [
            "Auth/token lifecycle",
            "Retry/backoff/idempotency",
            "Pagination/completeness",
            "Webhook trust and replay",
            "Rate-limit and partial failure handling",
        ]
        return ApiIntegrationReviewResult(
            mode="generate",
            summary="API integration review findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate findings against actual request/response and failure-path code."],
        )

    def debug(self, problem: str) -> ApiIntegrationReviewResult:
        findings = [
            ApiIntegrationFinding(
                severity="medium",
                title="Likely distributed-system assumption mismatch",
                rationale="External integrations usually fail because delivery, ordering, retries, auth, or partial failure assumptions were too optimistic.",
                recommendations=[
                    "Check auth validity, scope, and token refresh path.",
                    "Check duplicate delivery, partial failure, and resume behavior.",
                ],
            )
        ]
        checklist = [
            "Check auth and scopes.",
            "Check request/response contract drift.",
            "Check idempotency and retries.",
            "Check pagination or event ordering assumptions.",
        ]
        return ApiIntegrationReviewResult(
            mode="debug",
            summary=f"API integration debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Trace the failure across auth, transport, contract, and retry semantics."],
        )
