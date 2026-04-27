SECURITY_AGENT_MANIFEST = {
    "name": "security_agent",
    "mode_support": ["consult", "generate", "debug"],
    "knowledge_root": "src/security_agent/knowledge",
    "playbooks_root": "src/security_agent/playbooks",
    "notes": [
        "Security agent focuses on auth/authz, secrets, permissions, unsafe inputs, and external integration risk.",
        "Primary output should prioritize exploitable or policy-breaking issues over generic style concerns.",
    ],
}
