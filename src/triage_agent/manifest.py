TRIAGE_AGENT_MANIFEST = {
    "name": "triage_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/triage_agent/knowledge",
    "playbooks_root": "src/triage_agent/playbooks",
    "notes": [
        "Triage agent focuses on intake, classification, reproducibility, likely ownership, and routing to the right specialist.",
        "Primary output should reduce ambiguity and shorten time-to-action on incoming issues.",
    ],
}
