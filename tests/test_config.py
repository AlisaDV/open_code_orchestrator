from pathlib import Path

from opencode_orchestrator.config import OrchestratorConfig


def test_config_normalizes_workspace_relative_paths(tmp_path: Path) -> None:
    config = OrchestratorConfig(
        workspace=tmp_path,
        objective="check",
        session_db_path=Path("state/session.db"),
        approval_state_path=Path("state/pending.json"),
    )

    assert config.workspace == tmp_path.resolve()
    assert config.session_db_path == (tmp_path / "state/session.db").resolve()
    assert config.approval_state_path == (tmp_path / "state/pending.json").resolve()


def test_config_approval_mode_flags(tmp_path: Path) -> None:
    write_only = OrchestratorConfig(workspace=tmp_path, objective="x", approval_mode="write")
    run_only = OrchestratorConfig(workspace=tmp_path, objective="x", approval_mode="run")
    none_mode = OrchestratorConfig(workspace=tmp_path, objective="x", approval_mode="none")

    assert write_only.requires_write_approval is True
    assert write_only.requires_run_approval is False
    assert run_only.requires_write_approval is False
    assert run_only.requires_run_approval is True
    assert none_mode.requires_write_approval is False
    assert none_mode.requires_run_approval is False


def test_command_and_path_policies_match_expected_patterns(tmp_path: Path) -> None:
    config = OrchestratorConfig(workspace=tmp_path, objective="x")

    assert config.is_command_blocked("git reset --hard HEAD")
    assert config.is_command_blocked("pytest > out.txt")
    assert config.is_path_protected(".env")
    assert config.is_path_protected("foo/secrets/data.txt")
    assert config.is_path_protected(".git/config")
