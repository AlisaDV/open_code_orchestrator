from __future__ import annotations

import asyncio
from pathlib import Path

from agents import RunState

from .reporting import PendingApproval


def serialize_interruptions(interruptions: list[object]) -> list[PendingApproval]:
    rendered: list[PendingApproval] = []
    for index, item in enumerate(interruptions, start=1):
        rendered.append(
            PendingApproval(
                index=index,
                tool_name=str(
                    getattr(item, "tool_name", None)
                    or getattr(item, "name", None)
                    or "unknown_tool"
                ),
                arguments=getattr(item, "arguments", None),
                agent_name=str(getattr(getattr(item, "agent", None), "name", None) or "") or None,
                call_id=getattr(item, "call_id", None),
            )
        )
    return rendered


def save_run_state(path: Path, state: RunState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(state.to_string(), encoding="utf-8")


async def load_run_state(agent: object, path: Path) -> RunState:
    return await RunState.from_string(agent, path.read_text(encoding="utf-8"))


def load_run_state_sync(agent: object, path: Path) -> RunState:
    return asyncio.run(load_run_state(agent, path))


def apply_approval_decisions(
    state: RunState,
    *,
    approve_indexes: set[int],
    reject_indexes: set[int],
    rejection_message: str | None = None,
) -> None:
    interruptions = state.get_interruptions()
    for index, item in enumerate(interruptions, start=1):
        if index in approve_indexes:
            state.approve(item)
        elif index in reject_indexes:
            state.reject(item, rejection_message=rejection_message)
