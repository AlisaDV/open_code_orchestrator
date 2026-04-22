# Bitrix24 Users

## Core methods

- `user.add`
- `user.update`
- `user.current`
- `user.get`
- `user.search`
- `user.fields`

## Use cases

- invite employees
- update existing profiles
- search by personal data
- resolve Bitrix24 user ids for ownership fields in other modules

## Scope nuance

- `user_brief` — minimal user data
- `user_basic` — includes contact data
- `user` — full access, including add/update

## Common cross-links

- CRM responsibility fields use user ids
- tasks use `CREATED_BY`, `RESPONSIBLE_ID`, `ACCOMPLICES`, `AUDITORS`
- telephony and chats often require `USER_ID`

## Extra note

Bitrix24 supports extranet users. They are invited through `user.add` with extranet-related parameters.
