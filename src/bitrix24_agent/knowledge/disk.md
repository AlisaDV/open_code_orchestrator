# Bitrix24 Disk

## Main object families

- `disk.storage.*`
- `disk.folder.*`
- `disk.file.*`
- `disk.version.*`
- `disk.attachedObject.*`

## Common scenarios

- get application storage
- upload file to storage or folder
- create subfolder
- rename/copy/move file
- generate external link
- attach file to another Bitrix24 object

## Cross-links

- tasks can reference disk files through `UF_TASK_WEBDAV_FILES`
- chats exchange files and can use `im.message.add` or newer chat file methods
- CRM activities and other modules can reference disk-backed files

## Agent rule

When asked to upload a file into Bitrix24 and link it somewhere else, split the scenario into two steps:

1. upload into Disk
2. attach/link resulting identifier in the target module
