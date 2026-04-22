# Bitrix24 Chats

## Core methods

- `im.chat.add`
- `im.chat.get`
- `im.dialog.get`
- `im.chat.user.add`
- `im.chat.user.delete`
- `im.message.add`
- `im.dialog.messages.get`
- `im.dialog.read`

## Key identifiers

- `DIALOG_ID = XXX` for personal dialog with user id `XXX`
- `DIALOG_ID = chatXXX` for group chat
- `DIALOG_ID = sgXXX` for group/project chat

## Recommended flow

1. create or resolve chat id
2. inspect dialog metadata
3. add participants if needed
4. send messages
5. mark read / fetch history

## Files in chat

For new integrations prefer:

- `im.v2.File.upload`
- `im.v2.File.download`

Legacy `im.disk.*` is for older scenarios.

## Common mistake

Using outdated chat file methods in a new integration without checking whether the scenario is already on `im.v2`.
