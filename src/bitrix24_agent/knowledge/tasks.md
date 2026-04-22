# Bitrix24 Tasks

## Core methods

- `tasks.task.add`
- `tasks.task.update`
- `tasks.task.get`
- `tasks.task.list`
- `tasks.task.delete`
- `tasks.task.files.attach`
- `tasks.task.delegate`
- `tasks.task.complete`

## Important notes

- task methods are sensitive to parameter order in some scenarios
- new task card moved discussion into task chat
- old comment APIs exist but are not preferred for new task card behavior

## Common linked fields

- `UF_CRM_TASK` — link task to CRM object
- `UF_TASK_WEBDAV_FILES` — attach Disk files to task
- `PARENT_ID` — link subtask to parent

## Related method groups

- `task.checklistitem.*`
- `task.elapseditem.*`
- `task.dependence.*`
- `task.item.userfield.*`
- `tasks.flow.Flow.*`

## Agent rule

If task scenario includes file upload, do not stop at `tasks.task.add`; check Disk upload first, then attach file ids.
