from __future__ import annotations

import argparse
from pathlib import Path

from .config import ApprovalMode, OrchestratorConfig
from .orchestrator import load_pending_approvals, resume_orchestrator, run_orchestrator
from .project_profile import find_project_agent_profile, load_project_agent_profile


def _parse_index_list(raw: str | None) -> set[int]:
    if not raw:
        return set()
    values: set[int] = set()
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        values.add(int(chunk))
    return values


def _prompt_for_decisions(approvals: list[object]) -> tuple[set[int], set[int]]:
    approve_indexes: set[int] = set()
    reject_indexes: set[int] = set()
    for item in approvals:
        while True:
            answer = input(
                f"Approve #{item.index} {item.tool_name} {item.arguments or ''}? [y/n]: "
            ).strip().lower()
            if answer in {"y", "yes"}:
                approve_indexes.add(item.index)
                break
            if answer in {"n", "no"}:
                reject_indexes.add(item.index)
                break
    return approve_indexes, reject_indexes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the OpenCode multi-agent orchestrator.")
    parser.add_argument("objective", nargs="?", help="Goal for the orchestrator to complete.")
    parser.add_argument(
        "--project-profile",
        type=Path,
        help="Path to project.agent.json. If omitted, the CLI will auto-discover it from --workspace.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace directory to inspect and modify.",
    )
    parser.add_argument("--model", default="gpt-5.4", help="Model name for all agents.")
    parser.add_argument("--max-turns", type=int, default=20, help="Maximum manager turns.")
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Disable write operations for all agents.",
    )
    parser.add_argument(
        "--command-timeout-seconds",
        type=int,
        default=600,
        help="Timeout for shell commands executed by agents.",
    )
    parser.add_argument(
        "--session-id",
        help="Persistent session ID for multi-run memory.",
    )
    parser.add_argument(
        "--session-db-path",
        type=Path,
        default=Path(".opencode_orchestrator/session_history.db"),
        help="SQLite file used for session-backed memory.",
    )
    parser.add_argument(
        "--session-history-limit",
        type=int,
        default=80,
        help="Maximum number of session items loaded into each run.",
    )
    parser.add_argument(
        "--approval-mode",
        choices=["none", "write", "run", "write_run"],
        default="write_run",
        help="Which tool classes require human approval.",
    )
    parser.add_argument(
        "--approval-state-path",
        type=Path,
        default=Path(".opencode_orchestrator/pending_state.json"),
        help="Path where interrupted run state is stored.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume a paused run from --approval-state-path instead of starting a new one.",
    )
    parser.add_argument(
        "--approve",
        help="Comma-separated approval indexes to approve when resuming.",
    )
    parser.add_argument(
        "--reject",
        help="Comma-separated approval indexes to reject when resuming.",
    )
    parser.add_argument(
        "--approve-all",
        action="store_true",
        help="Approve all pending tool calls when resuming.",
    )
    parser.add_argument(
        "--reject-all",
        action="store_true",
        help="Reject all pending tool calls when resuming.",
    )
    parser.add_argument(
        "--rejection-message",
        help="Custom message sent back to the model for rejected tool calls.",
    )
    return parser


def _build_config(args: argparse.Namespace) -> OrchestratorConfig:
    objective = args.objective or "Resume interrupted orchestrator run"
    profile_path = args.project_profile or find_project_agent_profile(args.workspace)
    if profile_path:
        profile = load_project_agent_profile(profile_path)
        config = OrchestratorConfig.from_project_profile(
            profile,
            objective=objective,
            model=args.model,
        )
        return config.model_copy(
            update={
                "workspace": args.workspace if args.workspace != Path.cwd() else profile.workspace,
                "allow_write": not args.read_only,
                "max_turns": args.max_turns,
                "command_timeout_seconds": args.command_timeout_seconds,
                "session_id": args.session_id or config.session_id,
                "session_db_path": args.session_db_path,
                "session_history_limit": args.session_history_limit,
                "approval_mode": args.approval_mode,
                "approval_state_path": args.approval_state_path,
            }
        )

    return OrchestratorConfig(
        workspace=args.workspace,
        objective=objective,
        model=args.model,
        allow_write=not args.read_only,
        max_turns=args.max_turns,
        command_timeout_seconds=args.command_timeout_seconds,
        session_id=args.session_id,
        session_db_path=args.session_db_path,
        session_history_limit=args.session_history_limit,
        approval_mode=args.approval_mode,
        approval_state_path=args.approval_state_path,
    )


def main() -> None:
    args = build_parser().parse_args()
    config = _build_config(args)

    if args.resume:
        state, approvals = load_pending_approvals(config)
        approve_indexes = _parse_index_list(args.approve)
        reject_indexes = _parse_index_list(args.reject)

        if args.approve_all:
            approve_indexes = {item.index for item in approvals}
        if args.reject_all:
            reject_indexes = {item.index for item in approvals}

        if not approve_indexes and not reject_indexes:
            approve_indexes, reject_indexes = _prompt_for_decisions(approvals)

        overlap = approve_indexes & reject_indexes
        if overlap:
            raise SystemExit(f"Same approvals cannot be both approved and rejected: {sorted(overlap)}")

        unresolved = {item.index for item in approvals} - approve_indexes - reject_indexes
        if unresolved:
            raise SystemExit(
                f"All pending approvals must be resolved before resume. Missing: {sorted(unresolved)}"
            )

        outcome = resume_orchestrator(
            config,
            approve_indexes=approve_indexes,
            reject_indexes=reject_indexes,
            rejection_message=args.rejection_message,
        )
        print(outcome.model_dump_json(indent=2, exclude_none=True))
        return

    if not args.objective:
        raise SystemExit("objective is required unless --resume is used")

    outcome = run_orchestrator(config)
    print(outcome.model_dump_json(indent=2, exclude_none=True))


if __name__ == "__main__":
    main()
