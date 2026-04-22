# Playbook: Upload File And Link It

## Goal

Upload a file into Bitrix24 and link it to another object.

## Flow

1. choose storage or folder target
2. upload file
3. capture returned file id
4. attach that file id in target module

## Common methods

- `disk.storage.uploadfile`
- `disk.folder.uploadfile`
- `tasks.task.files.attach`
- `im.v2.File.upload`
- `im.message.add`

## Rule

Do not mix old and new chat file methods without checking scenario version.
