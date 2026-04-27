# Schema And Migration Principles

1. Every schema change must be evaluated against rollout order.
2. Migration safety matters more than elegance.
3. Nullability, defaults, and backfill strategy must be explicit.
4. Runtime schema generation is not a substitute for intentional migration planning in serious systems.
