# Bitrix24 Auth

## Webhook

Use incoming webhook for simple server-side integrations and personal/internal tooling.

### Notes

- webhook acts with the permissions of the user who created it
- webhook code is secret and must never be embedded into public frontend code
- format:

```text
https://<portal>/rest/<user_id>/<webhook_code>/<method>.json
```

## OAuth 2.0

Use OAuth for local apps, marketplace apps, and integrations that must work across different user portals.

### Full flow

1. redirect user to portal authorize URL
2. receive short-lived `code`
3. exchange `code` at `https://oauth.bitrix24.tech/oauth/token/`
4. receive `access_token` and `refresh_token`

### Important constraints

- `code` lifetime is about 30 seconds
- all `client_secret` exchange must happen server-to-server
- OAuth is not used for incoming local webhooks

### Key values returned after auth

- `access_token`
- `refresh_token`
- `client_endpoint`
- `member_id`
- `scope`

## Decision Rule

- personal/internal automation: start with webhook
- multi-tenant app or distributable integration: OAuth
