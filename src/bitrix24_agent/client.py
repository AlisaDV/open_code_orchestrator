from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .config import Bitrix24Config
from .models import Bitrix24ExecutionResult, Bitrix24MethodRequest
from .utils import join_url


class Bitrix24Client:
    def __init__(self, config: Bitrix24Config):
        self.config = config

    def build_url(self, method: str) -> str:
        if self.config.auth_mode == "webhook":
            webhook = self.config.webhook_url.get_secret_value() if self.config.webhook_url else None
            if not webhook:
                raise ValueError("webhook_url is required for webhook mode")
            return join_url(webhook, method)

        if not self.config.portal_base_url:
            raise ValueError("portal_base_url is required for oauth mode")
        return join_url(f"{self.config.portal_base_url.rstrip('/')}/rest", method)

    def execute(self, request: Bitrix24MethodRequest) -> Bitrix24ExecutionResult:
        if not self.config.allow_live_requests:
            raise RuntimeError("Live Bitrix24 requests are disabled by configuration")

        url = self.build_url(request.method)
        params = dict(request.params)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        if self.config.auth_mode == "oauth":
            access_token = self.config.access_token.get_secret_value() if self.config.access_token else None
            if not access_token:
                raise ValueError("access_token is required for oauth mode")
            params["auth"] = access_token

        data = urlencode(params, doseq=True).encode("utf-8")
        req = Request(url, data=data, headers=headers, method="POST")

        try:
            with urlopen(req, timeout=self.config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                parsed = json.loads(raw) if raw else None
                return Bitrix24ExecutionResult(
                    ok=True,
                    status_code=response.status,
                    method=request.method,
                    url=url,
                    payload=params,
                    response_json=parsed,
                    response_text=raw,
                )
        except HTTPError as error:
            raw = error.read().decode("utf-8", errors="replace")
            parsed = None
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = None
            return Bitrix24ExecutionResult(
                ok=False,
                status_code=error.code,
                method=request.method,
                url=url,
                payload=params,
                response_json=parsed,
                response_text=raw,
                error=f"HTTPError {error.code}",
            )
        except URLError as error:
            return Bitrix24ExecutionResult(
                ok=False,
                method=request.method,
                url=url,
                payload=params,
                error=f"URLError: {error.reason}",
            )
