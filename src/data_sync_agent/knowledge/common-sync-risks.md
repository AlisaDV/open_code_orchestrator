# Common Sync Risks

- no persisted checkpoint or resume marker
- duplicate writes on retry
- pagination cursor misuse
- partial batch success with no recovery path
- source and destination drift with no comparison signal
- backfills overwriting newer target state unintentionally
