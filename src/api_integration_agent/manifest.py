API_INTEGRATION_AGENT_MANIFEST = {
    "name": "api_integration_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/api_integration_agent/knowledge",
    "playbooks_root": "src/api_integration_agent/playbooks",
    "notes": [
        "API integration agent focuses on external API contract usage, auth, retries, idempotency, pagination, callbacks, and failure handling.",
        "Primary output should prioritize resilient integration behavior over transport or SDK preferences.",
    ],
}
