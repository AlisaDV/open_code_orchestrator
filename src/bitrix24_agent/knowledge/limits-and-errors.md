# Bitrix24 Limits And Errors

## Request intensity limits

Cloud Bitrix24 uses a leaky bucket style limit.

### Default plans

- refill rate: about `2 requests/sec`
- block threshold: about `50`

### Enterprise

- refill rate: about `5 requests/sec`
- block threshold: about `250`

## Practical guidance

- use `*.list` methods instead of many single-item requests
- use `batch` where appropriate
- add retries and backoff for `503`
- do not assume one safe RPS value works forever on every portal

## Resource cost limits

Bitrix24 also limits expensive methods by total operating time.

- response field `time.operating` matters
- if total per-method operating time exceeds threshold, that method can be blocked temporarily

## Common system errors

- `QUERY_LIMIT_EXCEEDED` — too many requests
- `NO_AUTH_FOUND` — invalid token/webhook
- `INVALID_CREDENTIALS` — no rights for current user/token
- `insufficient_scope` — requested method needs broader scope
- `expired_token` — OAuth token expired
- `ACCESS_DENIED` — REST unavailable on current plan or access policy
- `OVERLOAD_LIMIT` — REST blocked due to overload

## Agent rule

When debugging Bitrix24 failures, first check in this order:

1. URL correctness
2. auth mode used
3. scope coverage
4. user rights
5. limits / 503
6. method-specific validation errors
