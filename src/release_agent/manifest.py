RELEASE_AGENT_MANIFEST = {
    "name": "release_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/release_agent/knowledge",
    "playbooks_root": "src/release_agent/playbooks",
    "notes": [
        "Release agent focuses on release readiness, rollout safety, release notes, and rollback preparedness.",
        "Primary output should answer whether a release is actually ready, not just whether code compiles.",
    ],
}
