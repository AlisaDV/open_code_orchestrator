from __future__ import annotations

import asyncio
import json
import sys

sys.path.insert(0, "src")

from opencode_orchestrator.config import OrchestratorConfig
from opencode_orchestrator.tools import build_tools
from orchestrator_visualizer import VisualizerConfig, VisualizerObserver, VisualizerRepository
from orchestrator_visualizer.models import RunStatus


async def main() -> None:
    workspace = r"C:\work\open_code_orchestrator"
    run_id = "integrated-demo-run"

    visualizer_config = VisualizerConfig(workspace=workspace)
    observer = VisualizerObserver(visualizer_config)
    run = observer.run_started(
        objective="Integrated tool demo",
        run_id=run_id,
        workspace=workspace,
        model="gpt-5.4",
    )

    orchestrator_config = OrchestratorConfig(
        objective="Integrated tool demo",
        workspace=workspace,
        current_run_id=run_id,
        visualizer_enabled=True,
        approval_mode="none",
    )
    tools = {tool.name: tool for tool in build_tools(orchestrator_config)}
    tool_ctx = type("ToolCtx", (), {"tool_name": "demo"})()

    print(await tools["run_command"].on_invoke_tool(tool_ctx, json.dumps({"command": "py -3 -V"})))
    print(
        await tools["write_text_file"].on_invoke_tool(
            tool_ctx,
            json.dumps({"path": "tmp_visualizer_demo.txt", "content": "hello visualizer"}),
        )
    )
    print(
        await tools["run_command"].on_invoke_tool(
            tool_ctx,
            json.dumps({"command": "py -3 -m compileall src/orchestrator_visualizer"}),
        )
    )

    observer.run_finished(run, status=RunStatus.COMPLETED, summary="Integrated tool demo completed")

    repo = VisualizerRepository(visualizer_config)
    print("RUNS")
    print(json.dumps([r.model_dump() for r in repo.list_runs() if r.run_id == run_id], indent=2))
    print("EVENTS")
    print(
        json.dumps(
            [
                {
                    "type": e.event_type,
                    "title": e.title,
                    "status": e.status,
                    "payload": e.payload,
                }
                for e in repo.list_events(run_id)
            ],
            indent=2,
            default=str,
        )
    )
    print("FILES")
    print(json.dumps([f.model_dump() for f in repo.aggregate_file_impacts(run_id)], indent=2))
    print("VERIFICATION")
    print(json.dumps([v.model_dump(mode="json") for v in repo.list_verification_results(run_id)], indent=2))


if __name__ == "__main__":
    asyncio.run(main())
