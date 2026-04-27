from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

from agents import function_tool
from pydantic import Field

from .config import OrchestratorConfig


def list_available_specialists() -> list[str]:
    return ["bitrix24", "reviewer", "security", "database", "devops", "observability", "api_integration", "frontend_ui", "triage"]


def build_specialist_tools(config: OrchestratorConfig):
    normalized = {item.strip().lower() for item in config.enabled_specialists}
    tools = []

    def _parse_params(params_json: str) -> dict:
        if not params_json.strip():
            return {}
        return json.loads(params_json)

    if normalized.intersection({"bitrix24", "bitrix24_agent"}):
        from bitrix24_agent import Bitrix24AgentRuntime, Bitrix24Config, Bitrix24MethodRequest

        integration_settings = config.integration_settings("bitrix24")
        bitrix_config = Bitrix24Config(
            workspace=config.workspace,
            auth_mode=integration_settings.auth_mode if integration_settings and integration_settings.auth_mode else "webhook",
            allow_live_requests=integration_settings.allow_live_requests if integration_settings else False,
        )
        runtime = Bitrix24AgentRuntime(bitrix_config)

        @function_tool
        def bitrix24_consult(
            query: Annotated[str, Field(description="Question or integration task about Bitrix24 API.")],
        ) -> str:
            """Consult the local Bitrix24 knowledge pack."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def bitrix24_generate(
            method: Annotated[str, Field(description="Bitrix24 REST method, for example crm.item.add")],
            params_json: Annotated[str, Field(description="JSON object string with method params")],
            scope_hint: Annotated[str, Field(default="", description="Optional scope hint like crm, task, im, telephony")],
        ) -> str:
            """Build a dry-run execution plan for a Bitrix24 REST method."""
            request = Bitrix24MethodRequest(method=method, params=_parse_params(params_json), scope_hint=scope_hint or None)
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def bitrix24_debug(
            problem: Annotated[str, Field(description="Bitrix24 integration error, symptom, or failing behavior")],
        ) -> str:
            """Debug a Bitrix24 integration problem using the local knowledge pack."""
            return runtime.debug(problem).model_dump_json(indent=2)

        @function_tool
        def bitrix24_execute(
            method: Annotated[str, Field(description="Bitrix24 REST method to execute live")],
            params_json: Annotated[str, Field(description="JSON object string with method params")],
            scope_hint: Annotated[str, Field(default="", description="Optional scope hint")],
        ) -> str:
            """Execute a live Bitrix24 REST request when runtime credentials allow it."""
            request = Bitrix24MethodRequest(method=method, params=_parse_params(params_json), scope_hint=scope_hint or None)
            return runtime.execute(request).model_dump_json(indent=2)

        @function_tool
        def bitrix24_manifest() -> str:
            """Return the local Bitrix24 specialist manifest and connection notes."""
            from bitrix24_agent import BITRIX24_AGENT_MANIFEST

            payload = {
                **BITRIX24_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
                "integration_settings": integration_settings.model_dump(by_alias=True) if integration_settings else None,
                "browser_settings": config.browser_settings() if config.project_profile else None,
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        tools.extend([
            bitrix24_manifest,
            bitrix24_consult,
            bitrix24_generate,
            bitrix24_debug,
            bitrix24_execute,
        ])

    if normalized.intersection({"reviewer", "reviewer_agent", "review"}):
        from reviewer_agent import REVIEWER_AGENT_MANIFEST, ReviewRequest, ReviewerAgentRuntime

        runtime = ReviewerAgentRuntime()

        @function_tool
        def reviewer_manifest() -> str:
            """Return the local reviewer specialist manifest and connection notes."""
            payload = {
                **REVIEWER_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        @function_tool
        def reviewer_consult(
            query: Annotated[str, Field(description="Question about how to review a change, module, or risk area")],
        ) -> str:
            """Consult reviewer heuristics and review principles."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def reviewer_generate(
            summary: Annotated[str, Field(description="Short summary of the change set or review target")],
            files_json: Annotated[str, Field(description="JSON array string of changed files")],
            changed_areas_json: Annotated[str, Field(description="JSON array string of changed areas or modules")],
            tests_present: Annotated[bool, Field(description="Whether relevant tests exist for the change")],
            notes_json: Annotated[str, Field(description="JSON array string of extra notes or assumptions")],
        ) -> str:
            """Generate findings-first review scaffold for a change set."""
            request = ReviewRequest(
                summary=summary,
                files=json.loads(files_json) if files_json.strip() else [],
                changed_areas=json.loads(changed_areas_json) if changed_areas_json.strip() else [],
                tests_present=tests_present,
                notes=json.loads(notes_json) if notes_json.strip() else [],
            )
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def reviewer_debug(
            problem: Annotated[str, Field(description="Regression, escaped bug, or review miss to analyze")],
        ) -> str:
            """Analyze where a review likely missed a regression or risk."""
            return runtime.debug(problem).model_dump_json(indent=2)

        tools.extend([
            reviewer_manifest,
            reviewer_consult,
            reviewer_generate,
            reviewer_debug,
        ])

    if normalized.intersection({"security", "security_agent", "secure"}):
        from security_agent import SECURITY_AGENT_MANIFEST, SecurityAgentRuntime, SecurityReviewRequest

        runtime = SecurityAgentRuntime()

        @function_tool
        def security_manifest() -> str:
            """Return the local security specialist manifest and connection notes."""
            payload = {
                **SECURITY_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        @function_tool
        def security_consult(
            query: Annotated[str, Field(description="Question about auth, secrets, permissions, input validation, or external trust boundaries")],
        ) -> str:
            """Consult security review heuristics and principles."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def security_generate(
            summary: Annotated[str, Field(description="Short summary of the changed security-sensitive scope")],
            files_json: Annotated[str, Field(description="JSON array string of changed files")],
            changed_areas_json: Annotated[str, Field(description="JSON array string of changed areas or modules")],
            auth_touched: Annotated[bool, Field(description="Whether auth/authz was touched")],
            external_integration: Annotated[bool, Field(description="Whether external integrations or callbacks are involved")],
            secrets_present: Annotated[bool, Field(description="Whether secrets, tokens, or credentials are in scope")],
            notes_json: Annotated[str, Field(description="JSON array string of extra notes or assumptions")],
        ) -> str:
            """Generate security findings scaffold for a change set."""
            request = SecurityReviewRequest(
                summary=summary,
                files=json.loads(files_json) if files_json.strip() else [],
                changed_areas=json.loads(changed_areas_json) if changed_areas_json.strip() else [],
                auth_touched=auth_touched,
                external_integration=external_integration,
                secrets_present=secrets_present,
                notes=json.loads(notes_json) if notes_json.strip() else [],
            )
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def security_debug(
            problem: Annotated[str, Field(description="Security issue, suspicious behavior, or escaped vulnerability to analyze")],
        ) -> str:
            """Analyze where a security review likely missed a trust-boundary or validation issue."""
            return runtime.debug(problem).model_dump_json(indent=2)

        tools.extend([
            security_manifest,
            security_consult,
            security_generate,
            security_debug,
        ])

    if normalized.intersection({"database", "database_agent", "db"}):
        from database_agent import DATABASE_AGENT_MANIFEST, DatabaseAgentRuntime, DatabaseReviewRequest

        runtime = DatabaseAgentRuntime()

        @function_tool
        def database_manifest() -> str:
            """Return the local database specialist manifest and connection notes."""
            payload = {
                **DATABASE_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        @function_tool
        def database_consult(
            query: Annotated[str, Field(description="Question about schema, migrations, indexes, query behavior, or consistency")],
        ) -> str:
            """Consult database review heuristics and migration principles."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def database_generate(
            summary: Annotated[str, Field(description="Short summary of the changed database-sensitive scope")],
            files_json: Annotated[str, Field(description="JSON array string of changed files")],
            changed_areas_json: Annotated[str, Field(description="JSON array string of changed areas or modules")],
            schema_changed: Annotated[bool, Field(description="Whether schema or entity structure changed")],
            migration_present: Annotated[bool, Field(description="Whether an explicit migration exists")],
            query_changed: Annotated[bool, Field(description="Whether query or repository logic changed")],
            notes_json: Annotated[str, Field(description="JSON array string of extra notes or assumptions")],
        ) -> str:
            """Generate database findings scaffold for a change set."""
            request = DatabaseReviewRequest(
                summary=summary,
                files=json.loads(files_json) if files_json.strip() else [],
                changed_areas=json.loads(changed_areas_json) if changed_areas_json.strip() else [],
                schema_changed=schema_changed,
                migration_present=migration_present,
                query_changed=query_changed,
                notes=json.loads(notes_json) if notes_json.strip() else [],
            )
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def database_debug(
            problem: Annotated[str, Field(description="Database failure, migration issue, FK problem, or performance symptom to analyze")],
        ) -> str:
            """Analyze likely schema, migration, consistency, or query causes of a DB issue."""
            return runtime.debug(problem).model_dump_json(indent=2)

        tools.extend([
            database_manifest,
            database_consult,
            database_generate,
            database_debug,
        ])

    if normalized.intersection({"devops", "devops_agent", "ops"}):
        from devops_agent import DEVOPS_AGENT_MANIFEST, DevOpsAgentRuntime, DevOpsReviewRequest

        runtime = DevOpsAgentRuntime()

        @function_tool
        def devops_manifest() -> str:
            """Return the local DevOps specialist manifest and connection notes."""
            payload = {
                **DEVOPS_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        @function_tool
        def devops_consult(
            query: Annotated[str, Field(description="Question about Docker, CI/CD, env config, startup wiring, or deployment safety")],
        ) -> str:
            """Consult deployment and infrastructure review heuristics."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def devops_generate(
            summary: Annotated[str, Field(description="Short summary of the infra or deployment-sensitive change")],
            files_json: Annotated[str, Field(description="JSON array string of changed files")],
            changed_areas_json: Annotated[str, Field(description="JSON array string of changed areas or modules")],
            docker_touched: Annotated[bool, Field(description="Whether Docker or container config changed")],
            ci_touched: Annotated[bool, Field(description="Whether CI/CD pipeline files changed")],
            env_touched: Annotated[bool, Field(description="Whether env/config/secrets handling changed")],
            deploy_path_changed: Annotated[bool, Field(description="Whether deployment or startup path changed")],
            notes_json: Annotated[str, Field(description="JSON array string of extra notes or assumptions")],
        ) -> str:
            """Generate DevOps findings scaffold for a change set."""
            request = DevOpsReviewRequest(
                summary=summary,
                files=json.loads(files_json) if files_json.strip() else [],
                changed_areas=json.loads(changed_areas_json) if changed_areas_json.strip() else [],
                docker_touched=docker_touched,
                ci_touched=ci_touched,
                env_touched=env_touched,
                deploy_path_changed=deploy_path_changed,
                notes=json.loads(notes_json) if notes_json.strip() else [],
            )
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def devops_debug(
            problem: Annotated[str, Field(description="Deployment, startup, CI, or runtime environment problem to analyze")],
        ) -> str:
            """Analyze likely deployment or runtime environment causes of an operational issue."""
            return runtime.debug(problem).model_dump_json(indent=2)

        tools.extend([
            devops_manifest,
            devops_consult,
            devops_generate,
            devops_debug,
        ])

    if normalized.intersection({"observability", "observability_agent", "obs"}):
        from observability_agent import OBSERVABILITY_AGENT_MANIFEST, ObservabilityAgentRuntime, ObservabilityReviewRequest

        runtime = ObservabilityAgentRuntime()

        @function_tool
        def observability_manifest() -> str:
            """Return the local observability specialist manifest and connection notes."""
            payload = {
                **OBSERVABILITY_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        @function_tool
        def observability_consult(
            query: Annotated[str, Field(description="Question about logs, metrics, traces, alerting, or incident diagnosability")],
        ) -> str:
            """Consult observability review heuristics and diagnostic principles."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def observability_generate(
            summary: Annotated[str, Field(description="Short summary of the observability-sensitive change")],
            files_json: Annotated[str, Field(description="JSON array string of changed files")],
            changed_areas_json: Annotated[str, Field(description="JSON array string of changed areas or modules")],
            logging_touched: Annotated[bool, Field(description="Whether logging changed")],
            metrics_touched: Annotated[bool, Field(description="Whether metrics changed")],
            tracing_touched: Annotated[bool, Field(description="Whether tracing changed")],
            alerting_touched: Annotated[bool, Field(description="Whether alerting or monitoring changed")],
            notes_json: Annotated[str, Field(description="JSON array string of extra notes or assumptions")],
        ) -> str:
            """Generate observability findings scaffold for a change set."""
            request = ObservabilityReviewRequest(
                summary=summary,
                files=json.loads(files_json) if files_json.strip() else [],
                changed_areas=json.loads(changed_areas_json) if changed_areas_json.strip() else [],
                logging_touched=logging_touched,
                metrics_touched=metrics_touched,
                tracing_touched=tracing_touched,
                alerting_touched=alerting_touched,
                notes=json.loads(notes_json) if notes_json.strip() else [],
            )
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def observability_debug(
            problem: Annotated[str, Field(description="Incident, poor diagnosability, missing signals, or noisy alerting problem")],
        ) -> str:
            """Analyze likely logs/metrics/traces/alerting causes of an observability issue."""
            return runtime.debug(problem).model_dump_json(indent=2)

        tools.extend([
            observability_manifest,
            observability_consult,
            observability_generate,
            observability_debug,
        ])

    if normalized.intersection({"api_integration", "api-integration", "integration", "integration_agent"}):
        from api_integration_agent import API_INTEGRATION_AGENT_MANIFEST, ApiIntegrationAgentRuntime, ApiIntegrationReviewRequest

        runtime = ApiIntegrationAgentRuntime()

        @function_tool
        def api_integration_manifest() -> str:
            """Return the local API integration specialist manifest and connection notes."""
            payload = {
                **API_INTEGRATION_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        @function_tool
        def api_integration_consult(
            query: Annotated[str, Field(description="Question about OAuth, webhooks, retries, pagination, or external API integration quality")],
        ) -> str:
            """Consult external API integration heuristics and resilience principles."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def api_integration_generate(
            summary: Annotated[str, Field(description="Short summary of the integration-sensitive change")],
            files_json: Annotated[str, Field(description="JSON array string of changed files")],
            changed_areas_json: Annotated[str, Field(description="JSON array string of changed areas or modules")],
            oauth_touched: Annotated[bool, Field(description="Whether OAuth/token lifecycle changed")],
            webhook_touched: Annotated[bool, Field(description="Whether webhook/callback handling changed")],
            retry_logic_touched: Annotated[bool, Field(description="Whether retry/backoff logic changed")],
            pagination_touched: Annotated[bool, Field(description="Whether pagination or sync iteration changed")],
            notes_json: Annotated[str, Field(description="JSON array string of extra notes or assumptions")],
        ) -> str:
            """Generate API integration findings scaffold for a change set."""
            request = ApiIntegrationReviewRequest(
                summary=summary,
                files=json.loads(files_json) if files_json.strip() else [],
                changed_areas=json.loads(changed_areas_json) if changed_areas_json.strip() else [],
                oauth_touched=oauth_touched,
                webhook_touched=webhook_touched,
                retry_logic_touched=retry_logic_touched,
                pagination_touched=pagination_touched,
                notes=json.loads(notes_json) if notes_json.strip() else [],
            )
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def api_integration_debug(
            problem: Annotated[str, Field(description="External API integration failure, callback issue, sync bug, or auth problem")],
        ) -> str:
            """Analyze likely distributed-system causes of an external API integration issue."""
            return runtime.debug(problem).model_dump_json(indent=2)

        tools.extend([
            api_integration_manifest,
            api_integration_consult,
            api_integration_generate,
            api_integration_debug,
        ])

    if normalized.intersection({"frontend_ui", "frontend-ui", "ui", "frontend_ui_agent"}):
        from frontend_ui_agent import FRONTEND_UI_AGENT_MANIFEST, FrontendUiAgentRuntime, FrontendUiReviewRequest

        runtime = FrontendUiAgentRuntime()

        @function_tool
        def frontend_ui_manifest() -> str:
            """Return the local frontend UI specialist manifest and connection notes."""
            payload = {
                **FRONTEND_UI_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
                "browser_settings": config.browser_settings() if config.project_profile else None,
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        @function_tool
        def frontend_ui_consult(
            query: Annotated[str, Field(description="Question about forms, UI flows, accessibility, navigation, or browser interaction quality")],
        ) -> str:
            """Consult frontend UI review heuristics and user-flow principles."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def frontend_ui_generate(
            summary: Annotated[str, Field(description="Short summary of the UI-sensitive change")],
            files_json: Annotated[str, Field(description="JSON array string of changed files")],
            changed_areas_json: Annotated[str, Field(description="JSON array string of changed areas or modules")],
            forms_touched: Annotated[bool, Field(description="Whether forms or submit paths changed")],
            navigation_touched: Annotated[bool, Field(description="Whether navigation or redirects changed")],
            accessibility_touched: Annotated[bool, Field(description="Whether accessibility-sensitive structure changed")],
            browser_flow_touched: Annotated[bool, Field(description="Whether browser interaction flow changed")],
            notes_json: Annotated[str, Field(description="JSON array string of extra notes or assumptions")],
        ) -> str:
            """Generate frontend UI findings scaffold for a change set."""
            request = FrontendUiReviewRequest(
                summary=summary,
                files=json.loads(files_json) if files_json.strip() else [],
                changed_areas=json.loads(changed_areas_json) if changed_areas_json.strip() else [],
                forms_touched=forms_touched,
                navigation_touched=navigation_touched,
                accessibility_touched=accessibility_touched,
                browser_flow_touched=browser_flow_touched,
                notes=json.loads(notes_json) if notes_json.strip() else [],
            )
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def frontend_ui_debug(
            problem: Annotated[str, Field(description="Broken form, redirect, stale UI, or browser interaction issue to analyze")],
        ) -> str:
            """Analyze likely UI flow or browser interaction causes of a frontend issue."""
            return runtime.debug(problem).model_dump_json(indent=2)

        tools.extend([
            frontend_ui_manifest,
            frontend_ui_consult,
            frontend_ui_generate,
            frontend_ui_debug,
        ])

    if normalized.intersection({"triage", "triage_agent", "support", "support_triage"}):
        from triage_agent import TRIAGE_AGENT_MANIFEST, TriageAgentRuntime, TriageRequest

        runtime = TriageAgentRuntime()

        @function_tool
        def triage_manifest() -> str:
            """Return the local triage specialist manifest and connection notes."""
            payload = {
                **TRIAGE_AGENT_MANIFEST,
                "available_specialists": list_available_specialists(),
                "workspace": str(Path(config.workspace)),
            }
            return json.dumps(payload, indent=2, ensure_ascii=True)

        @function_tool
        def triage_consult(
            query: Annotated[str, Field(description="Question about issue intake, bug report quality, routing, or reproducibility")],
        ) -> str:
            """Consult issue triage heuristics and intake principles."""
            return runtime.consult(query).model_dump_json(indent=2)

        @function_tool
        def triage_generate(
            title: Annotated[str, Field(description="Short bug report or issue title")],
            description: Annotated[str, Field(description="Detailed issue description")],
            environment: Annotated[str, Field(default="", description="Environment like local, staging, production")],
            area_hints_json: Annotated[str, Field(description="JSON array string of area hints")],
            reproduction_steps_json: Annotated[str, Field(description="JSON array string of reproduction steps")],
            logs_present: Annotated[bool, Field(description="Whether logs or traces are attached")],
            ui_involved: Annotated[bool, Field(description="Whether UI/browser flow is involved")],
            external_integration_involved: Annotated[bool, Field(description="Whether external integrations are involved")],
        ) -> str:
            """Generate structured triage result for a bug report or incident."""
            request = TriageRequest(
                title=title,
                description=description,
                environment=environment or None,
                area_hints=json.loads(area_hints_json) if area_hints_json.strip() else [],
                reproduction_steps=json.loads(reproduction_steps_json) if reproduction_steps_json.strip() else [],
                logs_present=logs_present,
                ui_involved=ui_involved,
                external_integration_involved=external_integration_involved,
            )
            return runtime.generate(request).model_dump_json(indent=2)

        @function_tool
        def triage_debug(
            problem: Annotated[str, Field(description="Problem with routing, wrong owner, poor reproduction, or delayed diagnosis")],
        ) -> str:
            """Analyze where issue intake or routing likely broke down."""
            return runtime.debug(problem).model_dump_json(indent=2)

        tools.extend([
            triage_manifest,
            triage_consult,
            triage_generate,
            triage_debug,
        ])

    return tools
