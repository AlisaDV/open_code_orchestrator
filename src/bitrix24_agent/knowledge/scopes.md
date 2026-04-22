# Bitrix24 Scopes

## Most common scopes

- `crm`
- `task`
- `im`
- `disk`
- `telephony`
- `user`
- `user_brief`
- `user_basic`

## Scope selection rule

Always choose the smallest scope set that satisfies the scenario.

### Examples

- read user names only: `user_brief`
- user contacts or phone/email workflows: `user_basic`
- invite or update users: `user`
- CRM item sync: `crm`
- task creation/update: `task`
- chat and messenger actions: `im`
- file upload/share on Bitrix24 disk: `disk`
- call integration: `telephony`

## Common mistake

Using a webhook or token with insufficient scope causes:

- `insufficient_scope`
- `INVALID_CREDENTIALS`
- access denied behavior depending on context
