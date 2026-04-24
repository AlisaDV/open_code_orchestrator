from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

from agents import function_tool
from pydantic import Field

from .config import OrchestratorConfig


def list_available_specialists() -> list[str]:
    return ["bitrix24"]


def build_specialist_tools(config: OrchestratorConfig):
    normalized = {item.strip().lower() for item in config.enabled_specialists}
    if not normalized.intersection({"bitrix24", "bitrix24_agent"}):
        return []

    from bitrix24_agent import Bitrix24AgentRuntime, Bitrix24Config, Bitrix24MethodRequest

    integration_settings = config.integration_settings("bitrix24")
    bitrix_config = Bitrix24Config(
        workspace=config.workspace,
        auth_mode=integration_settings.auth_mode if integration_settings and integration_settings.auth_mode else "webhook",
        allow_live_requests=integration_settings.allow_live_requests if integration_settings else False,
    )

    runtime = Bitrix24AgentRuntime(bitrix_config)

    def _parse_params(params_json: str) -> dict:
        if not params_json.strip():
            return {}
        return json.loads(params_json)

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

    return [
        bitrix24_manifest,
        bitrix24_consult,
        bitrix24_generate,
        bitrix24_debug,
        bitrix24_execute,
    ]
