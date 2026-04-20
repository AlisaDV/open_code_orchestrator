from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


DEFAULT_BLOCKED_COMMAND_PATTERNS = [
    r"\brm\b",
    r"\brmdir\b",
    r"\bdel\b",
    r"\berase\b",
    r"\bformat\b",
    r"\bmkfs\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\btaskkill\b",
    r"\bsc\s+delete\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\b",
    r">",
    r"\|",
]

DEFAULT_PROTECTED_PATH_PATTERNS = [
    r"(^|[\\/])\.env($|\.)",
    r"(^|[\\/])id_rsa($|\.)",
    r"(^|[\\/])id_ed25519($|\.)",
    r"(^|[\\/])credentials\.json$",
    r"(^|[\\/])secrets?($|[\\/\.])",
    r"(^|[\\/])\.git($|[\\/])",
]


ApprovalMode = Literal["none", "write", "run", "write_run"]


class OrchestratorConfig(BaseModel):
    workspace: Path = Field(default_factory=lambda: Path.cwd())
    objective: str = Field(min_length=1)
    model: str = Field(default="gpt-5.4")
    allow_write: bool = Field(default=True)
    max_turns: int = Field(default=20, ge=1, le=100)
    command_timeout_seconds: int = Field(default=600, ge=1, le=3600)
    session_id: str | None = Field(default=None)
    session_db_path: Path = Field(default=Path(".opencode_orchestrator/session_history.db"))
    session_history_limit: int | None = Field(default=80, ge=1)
    current_run_id: str | None = Field(default=None)
    visualizer_enabled: bool = Field(default=True)
    approval_mode: ApprovalMode = Field(default="write_run")
    approval_state_path: Path = Field(default=Path(".opencode_orchestrator/pending_state.json"))
    blocked_command_patterns: list[str] = Field(default_factory=lambda: list(DEFAULT_BLOCKED_COMMAND_PATTERNS))
    protected_path_patterns: list[str] = Field(default_factory=lambda: list(DEFAULT_PROTECTED_PATH_PATTERNS))

    @model_validator(mode="after")
    def normalize_paths(self) -> "OrchestratorConfig":
        self.workspace = self.workspace.expanduser().resolve()
        self.session_db_path = self._resolve_path(self.session_db_path)
        self.approval_state_path = self._resolve_path(self.approval_state_path)
        return self

    def _resolve_path(self, value: Path) -> Path:
        candidate = value.expanduser()
        if not candidate.is_absolute():
            candidate = self.workspace / candidate
        return candidate.resolve()

    def is_command_blocked(self, command: str) -> str | None:
        for pattern in self.blocked_command_patterns:
            if re.search(pattern, command, flags=re.IGNORECASE):
                return pattern
        return None

    def is_path_protected(self, relative_path: str) -> str | None:
        normalized = relative_path.replace("\\", "/")
        for pattern in self.protected_path_patterns:
            if re.search(pattern, normalized, flags=re.IGNORECASE):
                return pattern
        return None

    @property
    def requires_write_approval(self) -> bool:
        return self.approval_mode in {"write", "write_run"}

    @property
    def requires_run_approval(self) -> bool:
        return self.approval_mode in {"run", "write_run"}
