DEVOPS_AGENT_MANIFEST = {
    "name": "devops_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/devops_agent/knowledge",
    "playbooks_root": "src/devops_agent/playbooks",
    "notes": [
        "DevOps agent focuses on deployment readiness, service wiring, environment configuration, Docker, and CI/CD risks.",
        "Primary output should prioritize release safety and operability over stylistic infrastructure changes.",
    ],
}
