from pathlib import Path

from opencode_orchestrator import OrchestratorConfig, OrchestratorOutcome, OrchestratorReport
from opencode_orchestrator.reporting import PendingApproval


def test_public_imports_are_available() -> None:
    config = OrchestratorConfig(workspace=Path.cwd(), objective="smoke")
    report = OrchestratorReport(objective="smoke", summary="ok")
    outcome = OrchestratorOutcome(status="completed", objective="smoke", report=report)
    pending = PendingApproval(index=1, tool_name="run_command")

    assert config.objective == "smoke"
    assert outcome.report == report
    assert pending.tool_name == "run_command"
