from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Annotated, Any

from agents import RunContextWrapper, function_tool
from pydantic import Field

from .config import OrchestratorConfig


def build_tools(config: OrchestratorConfig):
    workspace = config.workspace
    timeout = config.command_timeout_seconds

    observer = None
    if config.visualizer_enabled and config.current_run_id:
        from orchestrator_visualizer import VisualizerConfig, VisualizerObserver

        observer = VisualizerObserver(VisualizerConfig(workspace=workspace))

    def _log_tool_called(tool_name: str, payload: dict[str, Any]) -> None:
        if observer is None:
            return
        from orchestrator_visualizer.models import EventRecord, EventType

        observer.event(
            EventRecord(
                run_id=config.current_run_id,
                session_id=config.session_id,
                event_type=EventType.TOOL_CALLED,
                title=f"{tool_name} called",
                payload={"tool_name": tool_name, **payload},
            )
        )

    def _log_tool_finished(tool_name: str, status: str, payload: dict[str, Any]) -> None:
        if observer is None:
            return
        from orchestrator_visualizer.models import EventRecord, EventType

        observer.event(
            EventRecord(
                run_id=config.current_run_id,
                session_id=config.session_id,
                event_type=EventType.TOOL_FINISHED,
                status=status,
                title=f"{tool_name} finished",
                payload={"tool_name": tool_name, **payload},
            )
        )

    def _classify_verification_kind(command: str):
        normalized = command.lower()
        if any(token in normalized for token in ["pytest", "gradlew.bat test", "./gradlew.bat test", "mvn test", "npm test"]):
            from orchestrator_visualizer.models import VerificationKind

            return VerificationKind.TEST
        if any(token in normalized for token in ["bootjar", "gradle build", "./gradlew.bat build", "mvn package", "npm run build", "compileall"]):
            from orchestrator_visualizer.models import VerificationKind

            return VerificationKind.BUILD
        if any(token in normalized for token in ["bootrun", "uvicorn", "npm run dev", "npm start", "python -m", "py -3 -m"]):
            from orchestrator_visualizer.models import VerificationKind

            return VerificationKind.RUN
        if any(token in normalized for token in ["lint", "ruff", "eslint", "ktlint"]):
            from orchestrator_visualizer.models import VerificationKind

            return VerificationKind.LINT
        if any(token in normalized for token in ["mkdocs", "sphinx", "docs"]):
            from orchestrator_visualizer.models import VerificationKind

            return VerificationKind.DOCS
        return None

    def _log_verification(command: str, exit_code: int, duration_ms: int) -> None:
        if observer is None:
            return
        kind = _classify_verification_kind(command)
        if kind is None:
            return
        from orchestrator_visualizer.models import VerificationRecord, VerificationStatus

        observer.verification_result(
            VerificationRecord(
                run_id=config.current_run_id,
                kind=kind,
                status=VerificationStatus.PASSED if exit_code == 0 else VerificationStatus.FAILED,
                command=command,
                duration_ms=duration_ms,
                details={"exit_code": exit_code},
            )
        )

    def _render_guardrail(message: str) -> str:
        return f"Guardrail blocked operation: {message}"

    def _resolve_path(raw_path: str) -> Path:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = workspace / candidate
        resolved = candidate.resolve()
        try:
            relative = resolved.relative_to(workspace)
        except ValueError as exc:
            raise ValueError(f"Path escapes workspace: {raw_path}") from exc

        if protected_pattern := config.is_path_protected(relative.as_posix()):
            raise ValueError(
                f"Path '{relative.as_posix()}' matches protected pattern '{protected_pattern}'"
            )
        return resolved

    def _safe_resolve_for_read(raw_path: str) -> Path:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = workspace / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(workspace)
        except ValueError as exc:
            raise ValueError(f"Path escapes workspace: {raw_path}") from exc
        return resolved

    async def _write_needs_approval(
        _ctx: RunContextWrapper[Any], _params: dict[str, Any], _call_id: str
    ) -> bool:
        return config.requires_write_approval

    async def _run_needs_approval(
        _ctx: RunContextWrapper[Any], _params: dict[str, Any], _call_id: str
    ) -> bool:
        return config.requires_run_approval

    @function_tool
    def list_files(
        relative_path: Annotated[
            str,
            Field(default=".", description="Directory path relative to workspace."),
        ] = ".",
    ) -> str:
        """List files and directories inside the workspace."""
        try:
            target = _safe_resolve_for_read(relative_path)
        except ValueError as exc:
            return _render_guardrail(str(exc))

        if not target.exists():
            return f"Path does not exist: {target}"
        if target.is_file():
            return str(target.relative_to(workspace))

        entries = sorted(target.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        rendered = []
        for entry in entries[:200]:
            suffix = "/" if entry.is_dir() else ""
            rendered.append(f"{entry.relative_to(workspace)}{suffix}")
        if len(entries) > 200:
            rendered.append("... output truncated ...")
        return "\n".join(rendered) if rendered else "<empty directory>"

    @function_tool
    def read_text_file(
        path: Annotated[str, Field(description="File path relative to workspace.")],
        start_line: Annotated[int, Field(default=1, ge=1, description="1-based start line.")] = 1,
        max_lines: Annotated[int, Field(default=200, ge=1, le=1000, description="Maximum lines to read.")] = 200,
    ) -> str:
        """Read a UTF-8 text file from the workspace."""
        try:
            target = _safe_resolve_for_read(path)
        except ValueError as exc:
            return _render_guardrail(str(exc))

        if not target.exists() or not target.is_file():
            return f"File not found: {target}"

        if target.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".exe", ".dll"}:
            return _render_guardrail(f"Refusing to read likely binary file: {target.name}")

        try:
            lines = target.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            return _render_guardrail(f"Refusing to decode non-UTF-8 file: {target.name}")

        slice_start = start_line - 1
        slice_end = slice_start + max_lines
        rendered = []
        for line_number, line in enumerate(lines[slice_start:slice_end], start=start_line):
            rendered.append(f"{line_number}: {line}")
        return "\n".join(rendered) if rendered else "<no content in requested range>"

    @function_tool(needs_approval=_write_needs_approval)
    def write_text_file(
        path: Annotated[str, Field(description="File path relative to workspace.")],
        content: Annotated[str, Field(description="Full file contents to write.")],
    ) -> str:
        """Write a text file inside the workspace."""
        _log_tool_called("write_text_file", {"path": path, "content_length": len(content)})
        if not config.allow_write:
            _log_tool_finished("write_text_file", "blocked", {"reason": "writes_disabled"})
            return "Write operations are disabled by configuration."

        try:
            target = _resolve_path(path)
        except ValueError as exc:
            _log_tool_finished("write_text_file", "blocked", {"reason": str(exc)})
            return _render_guardrail(str(exc))

        existed_before = target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if observer is not None:
            from orchestrator_visualizer.models import ChangeType, FileImpactRecord

            observer.file_changed(
                FileImpactRecord(
                    run_id=config.current_run_id,
                    path=str(target.relative_to(workspace)),
                    change_type=ChangeType.MODIFIED if existed_before else ChangeType.ADDED,
                    summary=f"Wrote {len(content)} chars",
                    agent="tool:write_text_file",
                )
            )
        _log_tool_finished("write_text_file", "ok", {"path": str(target.relative_to(workspace))})
        return f"Wrote {target.relative_to(workspace)} ({len(content)} chars)"

    @function_tool(needs_approval=_run_needs_approval)
    def run_command(
        command: Annotated[str, Field(description="Shell command to execute in the workspace.")],
    ) -> str:
        """Run a shell command inside the workspace and return stdout and stderr."""
        _log_tool_called("run_command", {"command": command})
        if blocked_pattern := config.is_command_blocked(command):
            _log_tool_finished("run_command", "blocked", {"command": command, "pattern": blocked_pattern})
            return _render_guardrail(
                f"Command '{command}' matches blocked pattern '{blocked_pattern}'"
            )

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            _log_tool_finished("run_command", "timeout", {"command": command, "timeout_seconds": timeout})
            return f"Command timed out after {timeout} seconds: {command}"

        duration_ms = int((time.perf_counter() - started) * 1000)
        stdout = completed.stdout.strip() or "<empty stdout>"
        stderr = completed.stderr.strip() or "<empty stderr>"
        _log_verification(command, completed.returncode, duration_ms)
        _log_tool_finished(
            "run_command",
            "ok" if completed.returncode == 0 else "failed",
            {"command": command, "exit_code": completed.returncode, "duration_ms": duration_ms},
        )
        return (
            f"exit_code: {completed.returncode}\n"
            f"stdout:\n{stdout}\n\n"
            f"stderr:\n{stderr}"
        )

    @function_tool
    def workspace_summary() -> str:
        """Return a compact summary of the current orchestration context."""
        return (
            f"workspace={workspace}\n"
            f"allow_write={config.allow_write}\n"
            f"command_timeout_seconds={timeout}\n"
            f"session_id={config.session_id}\n"
            f"session_db_path={config.session_db_path}\n"
            f"approval_mode={config.approval_mode}\n"
            f"approval_state_path={config.approval_state_path}\n"
            f"objective={config.objective}"
        )

    return [workspace_summary, list_files, read_text_file, write_text_file, run_command]
