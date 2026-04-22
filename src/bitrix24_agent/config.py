from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr, model_validator


AuthMode = Literal["webhook", "oauth"]


class Bitrix24Config(BaseModel):
    workspace: Path = Field(default_factory=lambda: Path.cwd())
    auth_mode: AuthMode = Field(default="webhook")
    portal_base_url: str | None = Field(default=None)
    webhook_url: SecretStr | None = Field(default=None)
    access_token: SecretStr | None = Field(default=None)
    refresh_token: SecretStr | None = Field(default=None)
    client_id: SecretStr | None = Field(default=None)
    client_secret: SecretStr | None = Field(default=None)
    timeout_seconds: int = Field(default=60, ge=1, le=300)
    allow_live_requests: bool = Field(default=False)

    @model_validator(mode="after")
    def normalize_workspace(self) -> "Bitrix24Config":
        self.workspace = self.workspace.expanduser().resolve()
        return self

    def auth_summary(self) -> dict[str, str | bool | None]:
        return {
            "auth_mode": self.auth_mode,
            "portal_base_url": self.portal_base_url,
            "has_webhook_url": self.webhook_url is not None,
            "has_access_token": self.access_token is not None,
            "has_refresh_token": self.refresh_token is not None,
            "has_client_id": self.client_id is not None,
            "has_client_secret": self.client_secret is not None,
            "allow_live_requests": self.allow_live_requests,
        }
