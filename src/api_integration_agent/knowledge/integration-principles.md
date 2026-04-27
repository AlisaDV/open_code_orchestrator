# Integration Principles

1. External APIs are distributed systems, not local function calls.
2. Auth success does not guarantee scope correctness.
3. Retries without idempotency can be worse than no retries.
4. Pagination and event delivery are common silent data-loss points.
5. Webhooks must be treated as untrusted until verified.
