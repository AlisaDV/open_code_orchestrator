# Playbook: Create Task With CRM Link

## Goal

Create a task and bind it to a CRM entity.

## Needed

- scope `task`
- scope `crm` if CRM lookup is required before task creation
- CRM object identifier with prefix, for example `C_3`

## Flow

1. resolve CRM object id and prefix
2. call `tasks.task.add`
3. send `UF_CRM_TASK` with CRM object reference
4. optionally attach files through Disk and `UF_TASK_WEBDAV_FILES`

## Methods

- `tasks.task.add`
- `crm.item.get` or specialized `crm.*.get`
- `disk.storage.uploadfile` or `disk.folder.uploadfile`
