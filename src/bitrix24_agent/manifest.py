BITRIX24_AGENT_MANIFEST = {
    "name": "bitrix24_agent",
    "mode_support": ["consult", "generate", "execute", "debug"],
    "knowledge_root": "src/bitrix24_agent/knowledge",
    "playbooks_root": "src/bitrix24_agent/playbooks",
    "endpoint_map": "src/bitrix24_agent/endpoint_map.json",
    "notes": [
        "Knowledge pack is based on official Bitrix24 API docs at https://apidocs.bitrix24.ru",
        "This is a curated local pack, not a full offline mirror of all Bitrix24 pages.",
    ],
}
