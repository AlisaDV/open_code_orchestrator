# Sync Principles

1. Every sync has a source-of-truth, even if implicit.
2. Restartability matters as much as raw throughput.
3. Retries without deduplication create silent corruption.
4. Partial success must be representable in persisted state.
5. Reconciliation is what proves that sync actually worked.
