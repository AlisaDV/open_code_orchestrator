DATA_SYNC_AGENT_MANIFEST = {
    "name": "data_sync_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/data_sync_agent/knowledge",
    "playbooks_root": "src/data_sync_agent/playbooks",
    "notes": [
        "Data sync agent focuses on import/export, checkpoints, deduplication, reconciliation, and partial failure recovery.",
        "Primary output should prioritize correctness, restartability, and drift detection over raw throughput claims.",
    ],
}
