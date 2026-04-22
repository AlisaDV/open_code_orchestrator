# Playbook: Create Chat And Send Message

## Goal

Open or create a chat and send a message.

## Methods

- `im.chat.add`
- `im.chat.get`
- `im.chat.user.add`
- `im.message.add`
- `im.dialog.messages.get`

## Flow

1. decide chat type
2. create or resolve chat id
3. add participants if needed
4. send message
5. read history if confirmation is needed

## For files

Prefer `im.v2.File.upload` / `im.v2.File.download` for new integrations.
