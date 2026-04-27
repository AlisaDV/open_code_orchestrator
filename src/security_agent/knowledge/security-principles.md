# Security Principles

1. Trust boundaries must be explicit.
2. AuthN and AuthZ must be checked separately.
3. Secrets must never be embedded in source, docs, or client code.
4. Inputs that reach shell, filesystem, SQL, or external side effects deserve special scrutiny.
5. External integrations should default to least privilege and verifiable origin.
