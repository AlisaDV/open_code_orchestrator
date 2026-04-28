BUSINESS_RULES_AGENT_MANIFEST = {
    "name": "business_rules_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/business_rules_agent/knowledge",
    "playbooks_root": "src/business_rules_agent/playbooks",
    "notes": [
        "Business rules agent focuses on domain invariants, lifecycle transitions, policy assumptions, and process correctness.",
        "Primary output should prioritize broken business semantics and hidden rule drift over technical neatness.",
    ],
}
