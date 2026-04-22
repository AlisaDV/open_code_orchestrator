from __future__ import annotations

from pathlib import Path

from .config import Bitrix24Config
from .models import Bitrix24DryRunPlan, Bitrix24MethodRequest
from .utils import detect_family, load_endpoint_map


class Bitrix24DryRunPlanner:
    def __init__(self, config: Bitrix24Config):
        self.config = config
        self.base_dir = Path(__file__).resolve().parent
        self.endpoint_map = load_endpoint_map(self.base_dir)

    def plan(self, request: Bitrix24MethodRequest, *, mode: str = "execute") -> Bitrix24DryRunPlan:
        family = detect_family(request.method)
        warnings: list[str] = []
        next_steps: list[str] = []

        if family is None:
            warnings.append("Unable to classify method family automatically. Check official docs before execution.")

        if self.config.auth_mode == "webhook" and request.method.startswith("telephony.externalCall"):
            warnings.append("Some telephony methods work only in application context, not in webhook context.")

        if request.scope_hint is None:
            warnings.append("No explicit scope_hint provided. Validate required scope before live execution.")

        if family == "crm" and request.method not in self.endpoint_map.get("crm", {}).get("preferred_universal_methods", []):
            next_steps.append("Check whether specialized crm.* family is clearer than universal crm.item.* for this case.")

        if family in {"im", "im.v2"} and "disk" in request.method.lower():
            next_steps.append("For new chat file flows, prefer im.v2 file methods where possible.")

        url = None
        try:
            from .client import Bitrix24Client

            url = Bitrix24Client(self.config).build_url(request.method)
        except Exception as exc:
            warnings.append(f"URL build warning: {exc}")

        return Bitrix24DryRunPlan(
            mode=mode,
            method=request.method,
            url=url,
            params=request.params,
            auth_mode=self.config.auth_mode,
            scope_hint=request.scope_hint,
            family_detected=family,
            warnings=warnings,
            next_steps=next_steps,
        )
