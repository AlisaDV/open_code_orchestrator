from __future__ import annotations

from pathlib import Path
import json


def load_endpoint_map(base_dir: Path) -> dict:
    return json.loads((base_dir / "endpoint_map.json").read_text(encoding="utf-8"))


def detect_family(method: str) -> str | None:
    lowered = method.lower()
    for prefix in [
        "crm.",
        "user.",
        "tasks.",
        "task.",
        "im.",
        "im.v2.",
        "telephony.",
        "voximplant.",
        "disk.",
    ]:
        if lowered.startswith(prefix):
            return prefix.rstrip(".")
    return None


def join_url(base: str, method: str) -> str:
    base = base.rstrip("/")
    return f"{base}/{method}.json"
