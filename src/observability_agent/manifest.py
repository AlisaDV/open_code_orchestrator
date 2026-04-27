OBSERVABILITY_AGENT_MANIFEST = {
    "name": "observability_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/observability_agent/knowledge",
    "playbooks_root": "src/observability_agent/playbooks",
    "notes": [
        "Observability agent focuses on logs, metrics, traces, alertability, and incident diagnosis readiness.",
        "Primary output should prioritize diagnosability and signal quality over tooling preference debates.",
    ],
}
