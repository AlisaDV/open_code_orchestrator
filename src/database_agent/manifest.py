DATABASE_AGENT_MANIFEST = {
    "name": "database_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/database_agent/knowledge",
    "playbooks_root": "src/database_agent/playbooks",
    "notes": [
        "Database agent focuses on schema quality, migrations, indexes, query behavior, and data consistency risks.",
        "Primary output should prioritize correctness and operational safety before style or abstraction issues.",
    ],
}
