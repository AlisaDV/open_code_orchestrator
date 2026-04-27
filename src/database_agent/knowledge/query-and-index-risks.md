# Query And Index Risks

- missing index on new filter/sort path
- N+1 query behavior after entity relation changes
- accidental wide loads
- join fan-out causing duplicates or cost spikes
- cleanup order or FK issues during deletes
- schema drift between application assumptions and actual DB
