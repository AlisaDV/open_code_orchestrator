# Migration Principles

1. An upgrade is safe only if compatibility boundaries are understood.
2. Config migration is part of application migration.
3. Deprecation removal must account for hidden or delayed consumers.
4. Mixed-version rollout windows are often the real failure point.
5. Rollback must be considered before removing old paths.
