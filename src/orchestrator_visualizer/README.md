# Orchestrator Visualizer Skeleton

Minimal backend-side skeleton for process visualization.

## Included

- `config.py` - storage paths and initialization
- `models.py` - Pydantic models for runs, events, approvals, file impacts, verification
- `db.py` - SQLite schema and init helpers
- `repository.py` - SQLite persistence and aggregate reads
- `observer.py` - event writer for SQLite and JSONL
- `api.py` - read-only FastAPI endpoints for runs, events, files, approvals, verification
- `repository_types.py` - aggregate view models for read APIs

## Intended Next Steps

1. Emit `EventRecord` and `RunRecord` from the orchestrator runtime
2. Run the API with:

```bash
orchestrator-visualizer-api
```

3. Read endpoints like:
    - `/runs`
    - `/runs/{run_id}`
    - `/runs/{run_id}/events`
    - `/runs/{run_id}/files`
    - `/runs/{run_id}/approvals`
    - `/runs/{run_id}/verification`

4. Open the built-in dashboard:

```text
http://127.0.0.1:8787/dashboard
```

The dashboard is zero-build HTML/CSS/JS served by the same FastAPI app.

## Example Usage

```python
from orchestrator_visualizer import VisualizerConfig, VisualizerObserver
from orchestrator_visualizer.models import ChangeType, FileImpactRecord, VerificationKind, VerificationRecord, VerificationStatus

config = VisualizerConfig()
observer = VisualizerObserver(config)

run = observer.run_started(objective="Build project 01")
observer.file_changed(
    FileImpactRecord(
        run_id=run.run_id,
        path="projects/01-task-support-app/src/main/kotlin/.../TaskService.kt",
        change_type=ChangeType.MODIFIED,
        summary="Added task CRUD",
    )
)
observer.verification_result(
    VerificationRecord(
        run_id=run.run_id,
        kind=VerificationKind.TEST,
        status=VerificationStatus.PASSED,
        command="./gradlew.bat test",
    )
)
```
