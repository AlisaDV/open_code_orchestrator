from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, model_validator


class VisualizerConfig(BaseModel):
    workspace: Path = Field(default_factory=lambda: Path.cwd())
    storage_dir: Path = Field(default=Path(".opencode_observer"))
    sqlite_path: Path = Field(default=Path(".opencode_observer/runs.db"))
    events_dir: Path = Field(default=Path(".opencode_observer/events"))
    snapshots_dir: Path = Field(default=Path(".opencode_observer/snapshots"))

    @model_validator(mode="after")
    def normalize_paths(self) -> "VisualizerConfig":
        self.workspace = self.workspace.expanduser().resolve()
        self.storage_dir = self._resolve(self.storage_dir)
        self.sqlite_path = self._resolve(self.sqlite_path)
        self.events_dir = self._resolve(self.events_dir)
        self.snapshots_dir = self._resolve(self.snapshots_dir)
        return self

    def ensure_directories(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    def _resolve(self, value: Path) -> Path:
        candidate = value.expanduser()
        if not candidate.is_absolute():
            candidate = self.workspace / candidate
        return candidate.resolve()
