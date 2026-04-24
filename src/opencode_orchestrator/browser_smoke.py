from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import OrchestratorConfig


@dataclass
class BrowserSmokeInvocation:
    enabled: bool
    command: str | None
    workdir: Path | None
    operator_url: str | None
    base_url: str | None


def build_browser_smoke_invocation(config: OrchestratorConfig) -> BrowserSmokeInvocation:
    profile = config.project_profile
    if not profile or not profile.browser_smoke:
        return BrowserSmokeInvocation(False, None, None, None, None)

    script = profile.browser.smoke_script
    if not script:
        return BrowserSmokeInvocation(False, None, None, profile.browser.operator_url, profile.base_url)

    browser_operator_dir = config.workspace / "browser_operator"
    if not browser_operator_dir.exists():
        browser_operator_dir = config.workspace.parent / "browser_operator"

    return BrowserSmokeInvocation(
        enabled=True,
        command=script,
        workdir=browser_operator_dir if browser_operator_dir.exists() else config.workspace,
        operator_url=profile.browser.operator_url,
        base_url=profile.base_url,
    )


def run_browser_smoke(config: OrchestratorConfig, *, dry_run: bool = False) -> dict:
    invocation = build_browser_smoke_invocation(config)
    if not invocation.enabled:
        return {
            "enabled": False,
            "reason": "browser_smoke_disabled_or_missing_script",
        }

    payload = {
        "enabled": True,
        "command": invocation.command,
        "workdir": str(invocation.workdir) if invocation.workdir else None,
        "operator_url": invocation.operator_url,
        "base_url": invocation.base_url,
        "dry_run": dry_run,
    }
    if dry_run:
        return payload

    env = None
    if invocation.base_url or invocation.operator_url:
        env = dict(os.environ)
        if invocation.base_url:
            env["PROJECT01_URL"] = invocation.base_url
        if invocation.operator_url:
            env["BROWSER_OPERATOR_URL"] = invocation.operator_url

    completed = subprocess.run(
        invocation.command,
        cwd=invocation.workdir,
        shell=True,
        capture_output=True,
        text=True,
        env=env,
    )
    payload.update(
        {
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    )
    return payload
