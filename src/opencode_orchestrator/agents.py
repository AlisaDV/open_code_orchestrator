from __future__ import annotations

from agents import Agent

from .config import OrchestratorConfig
from .reporting import OrchestratorReport
from .specialists import build_specialist_tools
from .tools import build_tools


def build_specialists(config: OrchestratorConfig) -> dict[str, Agent]:
    shared_tools = build_tools(config)

    coder = Agent(
        name="Coder",
        model=config.model,
        instructions=(
            "You implement the user's requested code changes inside the workspace. "
            "Inspect files before changing them, keep edits minimal, and use available tools to read, write, and run commands. "
            "Respect guardrail responses and do not retry blocked actions with small variations."
        ),
        tools=shared_tools,
    )

    tester = Agent(
        name="Tester",
        model=config.model,
        instructions=(
            "You validate the project by selecting and running the smallest useful checks. "
            "Prefer existing test, lint, and build commands. Report failures with concrete reproduction details. "
            "Respect guardrail responses and propose safer alternatives when commands are blocked."
        ),
        tools=shared_tools,
    )

    documenter = Agent(
        name="Documenter",
        model=config.model,
        instructions=(
            "You update documentation for the current objective. "
            "Prefer README or focused docs changes, keep them accurate, and do not describe behavior that was not implemented or verified."
        ),
        tools=shared_tools,
    )

    runner = Agent(
        name="Runner",
        model=config.model,
        instructions=(
            "You discover how to start the project and capture the outcome. "
            "Run only the commands needed to boot the app or reproduce runtime behavior, then summarize logs and blockers. "
            "Respect guardrail responses and do not attempt destructive workarounds."
        ),
        tools=shared_tools,
    )

    return {
        "coder": coder,
        "tester": tester,
        "documenter": documenter,
        "runner": runner,
    }


def build_orchestrator(config: OrchestratorConfig) -> Agent:
    specialists = build_specialists(config)
    specialist_tools = build_specialist_tools(config)
    return Agent(
        name="OpenCode Orchestrator",
        model=config.model,
        output_type=OrchestratorReport,
        instructions=(
            "You are the manager agent for a software workspace. "
            "Break the objective into implementation, validation, documentation, and runtime checks as needed. "
            "Use specialist agents as tools for bounded subtasks, respect tool guardrails, and finish with a structured report. "
            "The report must be factual, concise, and grounded in concrete evidence from tool outputs."
        ),
        tools=[
            specialists["coder"].as_tool(
                tool_name="delegate_to_coder",
                tool_description="Implement or modify code for the current objective.",
            ),
            specialists["tester"].as_tool(
                tool_name="delegate_to_tester",
                tool_description="Run tests, lint, or build checks and report results.",
            ),
            specialists["documenter"].as_tool(
                tool_name="delegate_to_documenter",
                tool_description="Update project documentation to match implemented behavior.",
            ),
            specialists["runner"].as_tool(
                tool_name="delegate_to_runner",
                tool_description="Run the project or reproduction command and summarize runtime behavior.",
            ),
            *specialist_tools,
            *build_tools(config),
        ],
    )
