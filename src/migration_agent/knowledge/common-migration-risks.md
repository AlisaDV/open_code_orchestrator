# Common Migration Risks

- dependency upgraded but transitive runtime changed unexpectedly
- config keys renamed or defaults changed
- deprecated behavior removed while consumers still rely on it
- API contract changed before all consumers upgraded
- mixed-version rollout causing temporary incompatibility
- rollback impossible after one-way migration step
