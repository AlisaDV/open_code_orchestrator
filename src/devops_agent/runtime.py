from __future__ import annotations

from .models import DevOpsFinding, DevOpsReviewRequest, DevOpsReviewResult


class DevOpsAgentRuntime:
    def consult(self, query: str) -> DevOpsReviewResult:
        checklist = [
            "Check runtime dependencies and startup order.",
            "Check environment variables and secrets sources.",
            "Check Dockerfile / compose / service container assumptions.",
            "Check CI pipeline for build, test, and release parity.",
            "Check deploy rollback and readiness assumptions.",
        ]
        return DevOpsReviewResult(
            mode="consult",
            summary=f"DevOps review guidance prepared for query: {query}",
            checklist=checklist,
            next_steps=["Inspect infra files and deployment assumptions together with runtime behavior."],
        )

    def generate(self, request: DevOpsReviewRequest) -> DevOpsReviewResult:
        findings: list[DevOpsFinding] = []
        lowered = f"{request.summary} {' '.join(request.changed_areas)} {' '.join(request.notes)}".lower()

        if request.docker_touched or any(token in lowered for token in ["docker", "container", "image", "compose"]):
            findings.append(
                DevOpsFinding(
                    severity="high",
                    title="Container changes require runtime and dependency review",
                    rationale="Container changes often break only after deployment when startup order, filesystem assumptions, or missing packages differ from local runs.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check entrypoint, working directory, ports, healthcheck, and dependent services.",
                        "Verify image contains all runtime dependencies, not only build-time ones.",
                    ],
                )
            )
        if request.ci_touched or any(token in lowered for token in ["ci", "pipeline", "github actions", "gitlab", "workflow"]):
            findings.append(
                DevOpsFinding(
                    severity="medium",
                    title="CI changes should be reviewed for build parity and missing gates",
                    rationale="Pipelines often silently stop validating important paths after small configuration changes.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check that test, lint, build, and artifact steps still run in the expected order.",
                        "Check branch conditions and secret availability in CI environment.",
                    ],
                )
            )
        if request.env_touched or any(token in lowered for token in ["env", "variable", "secret", "config", "settings"]):
            findings.append(
                DevOpsFinding(
                    severity="high",
                    title="Environment and secret handling needs deployment-path review",
                    rationale="Configuration regressions often appear only outside local development when variables, defaults, and secret sources differ.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check required env vars, defaults, secret sources, and profile-specific behavior.",
                        "Check that no secret is accidentally moved into source-controlled config.",
                    ],
                )
            )
        if request.deploy_path_changed or any(token in lowered for token in ["deploy", "release", "startup", "healthcheck", "readiness"]):
            findings.append(
                DevOpsFinding(
                    severity="high",
                    title="Deployment path changes require readiness and rollback review",
                    rationale="A release can succeed technically while still failing operationally if readiness, migration order, or rollback path is unsafe.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=[
                        "Check startup readiness, health checks, migration order, and rollback path.",
                        "Check whether release depends on one-time manual actions.",
                    ],
                )
            )

        if not findings:
            findings.append(
                DevOpsFinding(
                    severity="low",
                    title="No obvious high-risk infrastructure signature detected from summary alone",
                    rationale="Infra review still requires reading actual deployment and runtime configuration files.",
                    affected_areas=request.changed_areas or request.files,
                    recommendations=["Inspect deployment assumptions, runtime config, and pipeline gates directly."],
                )
            )

        checklist = [
            "Container/runtime parity",
            "Environment and secrets handling",
            "CI gates and artifact flow",
            "Readiness/health checks",
            "Rollback safety",
        ]
        return DevOpsReviewResult(
            mode="generate",
            summary="DevOps review findings scaffold generated from changed scope.",
            findings=findings,
            checklist=checklist,
            next_steps=["Validate findings against actual infra files and deployment procedure."],
        )

    def debug(self, problem: str) -> DevOpsReviewResult:
        findings = [
            DevOpsFinding(
                severity="medium",
                title="Likely deployment or runtime environment mismatch",
                rationale="Operational failures often come from drift between local, CI, and deployed runtime assumptions.",
                recommendations=[
                    "Compare local, CI, and deployed env/config values.",
                    "Check startup logs, health checks, and dependent service readiness.",
                ],
            )
        ]
        checklist = [
            "Check env vars and secrets sources.",
            "Check container image/runtime differences.",
            "Check healthcheck, port, and startup sequencing.",
        ]
        return DevOpsReviewResult(
            mode="debug",
            summary=f"DevOps-debug guidance prepared for problem: {problem}",
            findings=findings,
            checklist=checklist,
            next_steps=["Trace failure to deployment assumptions before changing application code."],
        )
