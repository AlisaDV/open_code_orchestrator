REVIEWER_AGENT_MANIFEST = {
    "name": "reviewer_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/reviewer_agent/knowledge",
    "playbooks_root": "src/reviewer_agent/playbooks",
    "notes": [
        "Reviewer agent focuses on findings-first review output.",
        "Primary objective is bugs, risks, regressions, missing tests, and unsafe assumptions.",
    ],
}
