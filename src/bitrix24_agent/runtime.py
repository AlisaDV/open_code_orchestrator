from __future__ import annotations

from pathlib import Path

from .client import Bitrix24Client
from .config import Bitrix24Config
from .executors import Bitrix24Executors
from .models import (
    Bitrix24ConsultationResult,
    Bitrix24DebugResult,
    Bitrix24ExecutionResult,
    Bitrix24MethodRequest,
)
from .planner import Bitrix24DryRunPlanner
from .utils import load_endpoint_map


class Bitrix24AgentRuntime:
    def __init__(self, config: Bitrix24Config):
        self.config = config
        self.base_dir = Path(__file__).resolve().parent
        self.endpoint_map = load_endpoint_map(self.base_dir)
        self.planner = Bitrix24DryRunPlanner(config)
        self.client = Bitrix24Client(config)
        self.executors = Bitrix24Executors(self)

    def consult(self, query: str) -> Bitrix24ConsultationResult:
        lowered = query.lower()
        sections: list[str] = []
        methods: list[str] = []
        notes: list[str] = []

        if "oauth" in lowered or "webhook" in lowered or "auth" in lowered:
            sections.append("knowledge/auth.md")
            notes.append("Choose webhook for simple internal integrations, OAuth for multi-tenant or distributable apps.")
        if any(token in lowered for token in ["crm", "deal", "lead", "contact", "company", "smart process"]):
            sections.append("knowledge/crm.md")
            methods.extend(self.endpoint_map["crm"]["preferred_universal_methods"][:3])
        if "user" in lowered:
            sections.append("knowledge/users.md")
            methods.extend(self.endpoint_map["user"]["methods"][:3])
        if "task" in lowered:
            sections.append("knowledge/tasks.md")
            methods.extend(self.endpoint_map["tasks"]["core_methods"][:3])
        if any(token in lowered for token in ["chat", "message", "im."]):
            sections.append("knowledge/chats.md")
            methods.extend(self.endpoint_map["chats"]["core_methods"][:3])
        if any(token in lowered for token in ["call", "telephony", "sip"]):
            sections.append("knowledge/telephony.md")
            methods.extend(self.endpoint_map["telephony"]["external"][:3])
        if any(token in lowered for token in ["file", "disk", "upload"]):
            sections.append("knowledge/disk.md")
            methods.extend(self.endpoint_map["disk"]["storage"][:2])

        if not sections:
            sections.append("knowledge/overview.md")
            notes.append("Start with overview, then narrow down to a product area and scope.")

        return Bitrix24ConsultationResult(
            query=query,
            recommended_sections=sorted(set(sections)),
            recommended_methods=list(dict.fromkeys(methods)),
            notes=notes,
        )

    def generate(self, request: Bitrix24MethodRequest):
        return self.planner.plan(request, mode="generate")

    def debug(self, problem: str) -> Bitrix24DebugResult:
        lowered = problem.lower()
        likely_causes: list[str] = []
        checks: list[str] = []
        sections: list[str] = ["knowledge/limits-and-errors.md"]

        if "query_limit_exceeded" in lowered or "503" in lowered:
            likely_causes.append("Bitrix24 request intensity limit exceeded.")
            checks.extend([
                "Reduce request rate and add retry/backoff.",
                "Use *.list methods and batch where possible.",
            ])
        if any(token in lowered for token in ["no_auth_found", "expired_token", "invalid_credentials", "insufficient_scope"]):
            likely_causes.append("Auth mode, token, or scope is invalid for the requested method.")
            checks.extend([
                "Verify webhook or access token validity.",
                "Verify required scope for the method.",
                "Check user permissions behind the token or webhook.",
            ])
            sections.extend(["knowledge/auth.md", "knowledge/scopes.md"])
        if any(token in lowered for token in ["entitytypeid", "categoryid", "stageid"]):
            likely_causes.append("CRM object identifiers are inconsistent or wrong for the selected method.")
            checks.append("Verify entityTypeId/categoryId/stageId against CRM docs and portal configuration.")
            sections.append("knowledge/crm.md")
        if any(token in lowered for token in ["chat", "im.", "im.v2"]):
            sections.append("knowledge/chats.md")
        if any(token in lowered for token in ["telephony", "call_id", "external_call_id"]):
            sections.append("knowledge/telephony.md")

        if not likely_causes:
            likely_causes.append("Method-specific validation or unsupported scenario.")
            checks.append("Check official endpoint page and request payload against docs.")

        return Bitrix24DebugResult(
            problem=problem,
            likely_causes=likely_causes,
            checks=checks,
            relevant_sections=sorted(set(sections)),
        )

    def execute(self, request: Bitrix24MethodRequest) -> Bitrix24ExecutionResult:
        return self.client.execute(request)
