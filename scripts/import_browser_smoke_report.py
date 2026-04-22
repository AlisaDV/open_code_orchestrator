from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    workspace = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(workspace / "src"))

    from orchestrator_visualizer import VisualizerConfig, VisualizerRepository

    parser = argparse.ArgumentParser(description="Import browser smoke report into visualizer storage.")
    parser.add_argument("report_path", help="Path to browser smoke report.json")
    args = parser.parse_args()

    report_path = Path(args.report_path).expanduser().resolve()
    config = VisualizerConfig(workspace=workspace)
    repo = VisualizerRepository(config)
    report = repo.import_browser_smoke_report_file(report_path)
    print(f"Imported browser smoke report: {report.report_id}")
    print(f"target_url={report.target_url}")
    print(f"passed={report.passed} failed={report.failed} scenarios={len(report.scenarios)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
