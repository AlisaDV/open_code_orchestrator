from __future__ import annotations

from .models import ObservabilityFinding, ObservabilityReviewRequest, ObservabilityReviewResult


class ObservabilityAgentRuntime:
    def consult(self, query: str) -> ObservabilityReviewResult:
        checklist = [
            "Check whether failures produce actionable logs with enough context.",
            "Check whether high-value flows emit metrics or counters.",
            "Check whether long or multi-step flows are traceable across boundaries.",
            "Check whether alerts can be derived from emitted signals.",
        ]
        return ObservabilityReviewResult(
            mode="consult",
            summary=f"Observability guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Inspect whether operators can diagnose failure without reproducing locally."],
        )

    def generate(self, request: ObservabilityReviewRequest) -> ObservabilityReviewResult:
        findings: list[ObservabilityFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.logging_touched or any(token in lowered for token in ["log", "logger", "exception", "error handling"]):
            findings.append(
                ObservabilityFinding(
                    severity="high",
                    title="Logging changes need context and redaction review",
                    rationale="Logs are only useful if they preserve enough context without leaking secrets or noise.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check correlation/context fields and message usefulness.",
                        "Check secret or PII leakage in log lines.",
                    ],
                )
            )
        if request.metrics_touched or any(token in lowered for token in ["metric", "counter", "latency", "throughput", "prometheus"]):
            findings.append(
                ObservabilityFinding(
                    severity="medium",
                    title="Metrics changes should be reviewed for cardinality and actionability",
                    rationale="Metrics can become useless or dangerous if labels explode or if they do not map to decisions or alerts.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check label cardinality and metric naming.",
                        "Check that metrics reflect business or operational decisions.",
                    ],
                )
            )
        if request.tracing_touched or any(token in lowered for token in ["trace", "span", "correlation", "workflow"]):
            findings.append(
                ObservabilityFinding(
                    severity="medium",
                    title="Tracing changes should be reviewed for cross-boundary continuity",
                    rationale="Partial tracing is often worse than no tracing because it hides broken segments in critical workflows.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check span boundaries, IDs, and propagation across services or agents.",
                        "Check whether critical steps are represented in traces.",
                    ],
                )
            )
        if request.alerting_touched or any(token in lowered for token in ["alert", "incident", "monitor", "slo", "sla"]):
            findings.append(
                ObservabilityFinding(
                    severity="high",
                    title="Alerting changes should be reviewed for signal quality",
                    rationale="Bad alerting either misses incidents or trains operators to ignore alerts.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check that alerts are based on actionable signals, not noisy symptoms.",
                        "Check that there is enough context to route and diagnose incidents.",
                    ],
                )
            )

        if not findings:
            findings.append(
                ObservabilityFinding(
                    severity="low",
                    title="No obvious observability-specific risk signature detected from summary alone",
                    rationale="Observability still needs direct review of logs, signals, and diagnostic affordances.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect whether a real production failure could be diagnosed from emitted signals."],
                )
            )

        checklist = [
            "Actionable logs",
            "Metric usefulness and cardinality",
            "Trace continuity",
            "Alert quality",
            "Incident diagnosability",
        ]
        return ObservabilityReviewResult(
            mode="generate",
            summary="Observability review findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate findings against real runtime flows and likely production incidents."],
        )

    def debug(self, problem: str) -> ObservabilityReviewResult:
        findings = [
            ObservabilityFinding(
                severity="medium",
                title="Likely diagnosability gap",
                rationale="When incidents are hard to debug, the usual problem is missing context, weak correlation, or missing signals rather than missing code alone.",
                recommendations=[
                    "Check whether logs include identifiers needed to correlate the failing path.",
                    "Check whether metrics and traces can isolate the failing subsystem quickly.",
                ],
            )
        ]
        checklist = [
            "Can the incident be identified from logs alone?",
            "Are metrics available for the failing flow?",
            "Is there trace continuity across the failing path?",
        ]
        return ObservabilityReviewResult(
            mode="debug",
            summary=f"Observability-debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Add the minimum missing signal that would have shortened diagnosis time."],
        )
