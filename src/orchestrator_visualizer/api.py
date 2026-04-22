from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import VisualizerConfig
from .repository import VisualizerRepository


def create_app(config: VisualizerConfig | None = None) -> FastAPI:
    app = FastAPI(title="Orchestrator Visualizer API", version="0.1.0")
    cfg = config or VisualizerConfig()
    repo = VisualizerRepository(cfg)
    static_dir = Path(__file__).resolve().parent / "static"

    app.mount("/visualizer-assets", StaticFiles(directory=static_dir), name="visualizer-assets")

    @app.get("/dashboard", include_in_schema=False)
    def dashboard() -> FileResponse:
        return FileResponse(static_dir / "dashboard.html")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/runs")
    def list_runs() -> list[dict]:
        return [item.model_dump(mode="json") for item in repo.list_runs()]

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict:
        run = repo.get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return run.model_dump(mode="json")

    @app.get("/runs/{run_id}/events")
    def list_events(run_id: str) -> list[dict]:
        if repo.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return [item.model_dump(mode="json") for item in repo.list_events(run_id)]

    @app.get("/runs/{run_id}/files")
    def list_files(run_id: str) -> list[dict]:
        if repo.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return [item.model_dump(mode="json") for item in repo.aggregate_file_impacts(run_id)]

    @app.get("/runs/{run_id}/approvals")
    def list_approvals(run_id: str) -> list[dict]:
        if repo.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return [item.model_dump(mode="json") for item in repo.list_approvals(run_id)]

    @app.get("/runs/{run_id}/verification")
    def list_verification(run_id: str) -> list[dict]:
        if repo.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return [item.model_dump(mode="json") for item in repo.list_verification_results(run_id)]

    @app.get("/browser-smoke")
    def list_browser_smoke_reports() -> list[dict]:
        return [item.model_dump(mode="json") for item in repo.list_browser_smoke_reports()]

    @app.get("/browser-smoke/latest")
    def latest_browser_smoke_report() -> dict:
        report = repo.latest_browser_smoke_report()
        if report is None:
            raise HTTPException(status_code=404, detail="Browser smoke report not found")
        return report.model_dump(mode="json")

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("orchestrator_visualizer.api:app", host="127.0.0.1", port=8787, reload=False)
