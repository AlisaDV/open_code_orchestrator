from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field, model_validator


class ProjectProfileOrchestrator(BaseModel):
    session_id: str | None = Field(default=None, validation_alias="sessionId")
    approval_mode: str = Field(default="write_run", validation_alias="approvalMode")
    max_turns: int = Field(default=20, validation_alias="maxTurns")
    read_only: bool = Field(default=False, validation_alias="readOnly")


class ProjectProfileBrowser(BaseModel):
    operator_url: str | None = Field(default=None, validation_alias="operatorUrl")
    headless: bool = True
    smoke_script: str | None = Field(default=None, validation_alias="smokeScript")


class ProjectProfileIntegrationConfig(BaseModel):
    mode: str | None = None
    allow_live_requests: bool = Field(default=False, validation_alias="allowLiveRequests")
    auth_mode: str | None = Field(default=None, validation_alias="authMode")


class ProjectAgentProfile(BaseModel):
    name: str
    workspace: Path
    base_url: str | None = Field(default=None, validation_alias="baseUrl")
    run_command: str | None = Field(default=None, validation_alias="runCommand")
    api: bool = True
    ui: bool = False
    database_required: bool = Field(default=False, validation_alias="databaseRequired")
    browser_smoke: bool = Field(default=False, validation_alias="browserSmoke")
    visualizer: bool = True
    orchestrator: ProjectProfileOrchestrator = Field(default_factory=ProjectProfileOrchestrator)
    browser: ProjectProfileBrowser = Field(default_factory=ProjectProfileBrowser)
    specialists: list[str] = Field(default_factory=list)
    integrations: dict[str, ProjectProfileIntegrationConfig] = Field(default_factory=dict)
    critical_scenarios: list[str] = Field(default_factory=list, validation_alias="criticalScenarios")
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_workspace(self) -> "ProjectAgentProfile":
        self.workspace = self.workspace.expanduser().resolve()
        return self


def load_project_agent_profile(path: str | Path) -> ProjectAgentProfile:
    profile_path = Path(path).expanduser().resolve()
    payload = json.loads(profile_path.read_text(encoding="utf-8"))
    if "workspace" not in payload:
        payload["workspace"] = str(profile_path.parent)
    return ProjectAgentProfile.model_validate(payload)


def find_project_agent_profile(start_path: str | Path) -> Path | None:
    current = Path(start_path).expanduser().resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        profile = candidate / "project.agent.json"
        if profile.exists():
            return profile
    return None
