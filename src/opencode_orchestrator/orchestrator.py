from __future__ import annotations

from agents import RunConfig, Runner, SessionSettings, SQLiteSession, ToolErrorFormatterArgs

from .agents import build_orchestrator
from .approval import apply_approval_decisions, load_run_state_sync, save_run_state, serialize_interruptions
from .browser_smoke import run_browser_smoke
from .config import OrchestratorConfig
from .reporting import OrchestratorOutcome, OrchestratorReport


def _build_visualizer(config: OrchestratorConfig):
    if not config.visualizer_enabled:
        return None
    from orchestrator_visualizer import VisualizerConfig, VisualizerObserver

    return VisualizerObserver(VisualizerConfig(workspace=config.workspace))


def build_session(config: OrchestratorConfig) -> SQLiteSession | None:
    if not config.session_id:
        return None

    config.session_db_path.parent.mkdir(parents=True, exist_ok=True)
    return SQLiteSession(config.session_id, str(config.session_db_path))


def _tool_error_formatter(args: ToolErrorFormatterArgs[None]) -> str | None:
    if args.kind != "approval_rejected":
        return None
    return (
        f"Tool '{args.tool_name}' was rejected by a human reviewer. "
        "Do not retry the same action blindly; adjust the plan or propose a safer alternative."
    )


def build_run_config(config: OrchestratorConfig) -> RunConfig:
    session_settings = None
    if config.session_history_limit is not None:
        session_settings = SessionSettings(limit=config.session_history_limit)

    return RunConfig(
        workflow_name="OpenCode Orchestrator",
        trace_metadata={
            "workspace": str(config.workspace),
            "session_id": config.session_id,
        },
        session_settings=session_settings,
        tool_error_formatter=_tool_error_formatter,
    )


def _normalize_final_output(config: OrchestratorConfig, final_output: object) -> OrchestratorReport:
    if isinstance(final_output, OrchestratorReport):
        return final_output
    return OrchestratorReport(
        objective=config.objective,
        summary=str(final_output),
        evidence=["Final output was not returned as structured data; wrapped as fallback text."],
    )


def _attach_browser_smoke_result(config: OrchestratorConfig, outcome: OrchestratorOutcome) -> OrchestratorOutcome:
    if outcome.status != "completed" or outcome.report is None:
        return outcome
    if not config.project_profile or not config.project_profile.browser_smoke:
        return outcome

    smoke = run_browser_smoke(config, dry_run=False)
    report = outcome.report.model_copy(deep=True)

    if not smoke.get("enabled"):
        report.next_steps.append("Browser smoke profile is present but no executable smoke script was available.")
        return outcome.model_copy(update={"report": report})

    command = smoke.get("command")
    workdir = smoke.get("workdir")
    exit_code = smoke.get("exit_code")
    report.evidence.append(
        f"Browser smoke invoked: command={command!r}, workdir={workdir!r}, exit_code={exit_code!r}"
    )
    if exit_code == 0:
        report.completed.append("Browser smoke scenarios completed successfully after orchestrator run.")
    else:
        report.risks.append("Browser smoke scenarios failed after orchestrator run.")
        stderr = (smoke.get("stderr") or "").strip()
        stdout = (smoke.get("stdout") or "").strip()
        if stderr:
            report.risks.append(f"Browser smoke stderr: {stderr[:500]}")
        elif stdout:
            report.risks.append(f"Browser smoke output: {stdout[:500]}")
    return outcome.model_copy(update={"report": report})


def _result_to_outcome(config: OrchestratorConfig, result: object) -> OrchestratorOutcome:
    interruptions = getattr(result, "interruptions", [])
    observer = _build_visualizer(config)
    if interruptions:
        state = result.to_state()
        save_run_state(config.approval_state_path, state)
        if observer is not None and config.current_run_id:
            from orchestrator_visualizer.models import ApprovalRecord

            for item in interruptions:
                observer.approval_requested(
                    ApprovalRecord(
                        approval_id=str(getattr(item, "call_id", None) or f"approval-{getattr(item, 'tool_name', 'unknown_tool')}"),
                        run_id=config.current_run_id,
                        tool_name=str(getattr(item, "tool_name", None) or getattr(item, "name", None) or "unknown_tool"),
                        arguments={"arguments": getattr(item, "arguments", None), "call_id": getattr(item, "call_id", None)},
                    )
                )
        return OrchestratorOutcome(
            status="awaiting_approval",
            objective=config.objective,
            state_path=str(config.approval_state_path),
            approvals=serialize_interruptions(interruptions),
        )

    if config.approval_state_path.exists():
        config.approval_state_path.unlink()

    outcome = OrchestratorOutcome(
        status="completed",
        objective=config.objective,
        report=_normalize_final_output(config, result.final_output),
    )
    if observer is not None and config.current_run_id:
        from orchestrator_visualizer.models import RunRecord, RunStatus

        existing_run = observer.repository.get_run(config.current_run_id)
        observer.run_finished(
            existing_run or RunRecord(
                run_id=config.current_run_id,
                session_id=config.session_id,
                objective=config.objective,
                status=RunStatus.RUNNING,
                model=config.model,
                workspace=str(config.workspace),
            ),
            status=RunStatus.COMPLETED,
            summary=outcome.report.summary if outcome.report else None,
        )
    return outcome


def run_orchestrator(config: OrchestratorConfig) -> OrchestratorOutcome:
    observer = _build_visualizer(config)
    if observer is not None:
        run = observer.run_started(
            objective=config.objective,
            run_id=config.current_run_id,
            session_id=config.session_id,
            model=config.model,
            workspace=str(config.workspace),
        )
        config = config.model_copy(update={"current_run_id": run.run_id})
    result = Runner.run_sync(
        build_orchestrator(config),
        input=config.objective,
        max_turns=config.max_turns,
        session=build_session(config),
        run_config=build_run_config(config),
    )
    outcome = _result_to_outcome(config, result)
    return _attach_browser_smoke_result(config, outcome)


def resume_orchestrator(
    config: OrchestratorConfig,
    *,
    approve_indexes: set[int],
    reject_indexes: set[int],
    rejection_message: str | None = None,
) -> OrchestratorOutcome:
    observer = _build_visualizer(config)
    if observer is not None and not config.current_run_id:
        run = observer.run_started(
            objective=config.objective,
            session_id=config.session_id,
            model=config.model,
            workspace=str(config.workspace),
        )
        config = config.model_copy(update={"current_run_id": run.run_id})
    orchestrator = build_orchestrator(config)
    state = load_run_state_sync(orchestrator, config.approval_state_path)
    if observer is not None and config.current_run_id:
        interruptions = serialize_interruptions(state.get_interruptions())
        for item in interruptions:
            if item.index in approve_indexes:
                from orchestrator_visualizer.models import ApprovalStatus

                observer.approval_resolved(
                    item.call_id or f"approval-{item.index}",
                    run_id=config.current_run_id,
                    tool_name=item.tool_name,
                    status=ApprovalStatus.APPROVED,
                    arguments={"arguments": item.arguments, "agent_name": item.agent_name},
                    resolution_note="Approved during resume",
                )
            elif item.index in reject_indexes:
                from orchestrator_visualizer.models import ApprovalStatus

                observer.approval_resolved(
                    item.call_id or f"approval-{item.index}",
                    run_id=config.current_run_id,
                    tool_name=item.tool_name,
                    status=ApprovalStatus.REJECTED,
                    arguments={"arguments": item.arguments, "agent_name": item.agent_name},
                    resolution_note=rejection_message,
                )
    apply_approval_decisions(
        state,
        approve_indexes=approve_indexes,
        reject_indexes=reject_indexes,
        rejection_message=rejection_message,
    )
    result = Runner.run_sync(
        orchestrator,
        state,
        max_turns=config.max_turns,
        session=build_session(config),
        run_config=build_run_config(config),
    )
    outcome = _result_to_outcome(config, result)
    return _attach_browser_smoke_result(config, outcome)


def load_pending_approvals(config: OrchestratorConfig):
    orchestrator = build_orchestrator(config)
    state = load_run_state_sync(orchestrator, config.approval_state_path)
    return state, serialize_interruptions(state.get_interruptions())
