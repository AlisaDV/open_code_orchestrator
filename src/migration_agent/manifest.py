MIGRATION_AGENT_MANIFEST = {
    "name": "migration_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/migration_agent/knowledge",
    "playbooks_root": "src/migration_agent/playbooks",
    "notes": [
        "Migration agent focuses on framework/library/config upgrades, deprecations, compatibility windows, and phased rollout strategy.",
        "Primary output should prioritize breakage risk, upgrade ordering, and rollback safety over package freshness alone.",
    ],
}
