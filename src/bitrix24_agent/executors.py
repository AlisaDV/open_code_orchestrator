from __future__ import annotations

from .models import (
    Bitrix24MethodRequest,
    CreateChatAndSendMessageInput,
    CreateCrmItemInput,
    CreateTaskWithCrmLinkInput,
    ExecutorOutcome,
    RegisterExternalCallInput,
)


class Bitrix24Executors:
    def __init__(self, runtime):
        self.runtime = runtime

    def create_crm_item(self, payload: CreateCrmItemInput, *, mode: str = "generate") -> ExecutorOutcome:
        if payload.use_specialized_family:
            method = f"crm.{payload.use_specialized_family}.add"
            params = {"fields": dict(payload.fields)}
        else:
            method = "crm.item.add"
            params = {
                "entityTypeId": payload.entity_type_id,
                "fields": dict(payload.fields),
            }
            if payload.category_id is not None:
                params["categoryId"] = payload.category_id
            if payload.stage_id is not None:
                params["fields"]["stageId"] = payload.stage_id

        request = Bitrix24MethodRequest(method=method, params=params, scope_hint="crm")
        if mode == "execute":
            return ExecutorOutcome(action="create_crm_item", mode=mode, execution=[self.runtime.execute(request)])
        return ExecutorOutcome(action="create_crm_item", mode=mode, plan=[self.runtime.generate(request)])

    def create_task_with_crm_link(self, payload: CreateTaskWithCrmLinkInput, *, mode: str = "generate") -> ExecutorOutcome:
        fields = {
            "TITLE": payload.title,
            "DESCRIPTION": payload.description,
            "RESPONSIBLE_ID": payload.responsible_id,
            "UF_CRM_TASK": [payload.crm_binding],
        }
        if payload.accomplices:
            fields["ACCOMPLICES"] = payload.accomplices
        if payload.auditors:
            fields["AUDITORS"] = payload.auditors
        if payload.deadline:
            fields["DEADLINE"] = payload.deadline
        if payload.disk_file_ids:
            fields["UF_TASK_WEBDAV_FILES"] = [f"n{file_id}" for file_id in payload.disk_file_ids]

        request = Bitrix24MethodRequest(
            method="tasks.task.add",
            params={"fields": fields},
            scope_hint="task",
        )
        notes = ["If CRM object id is not yet known, resolve it with crm.item.get/list before task creation."]
        if mode == "execute":
            return ExecutorOutcome(action="create_task_with_crm_link", mode=mode, execution=[self.runtime.execute(request)], notes=notes)
        return ExecutorOutcome(action="create_task_with_crm_link", mode=mode, plan=[self.runtime.generate(request)], notes=notes)

    def create_chat_and_send_message(self, payload: CreateChatAndSendMessageInput, *, mode: str = "generate") -> ExecutorOutcome:
        create_request = Bitrix24MethodRequest(
            method="im.chat.add",
            params={
                "TITLE": payload.title,
                "TYPE": payload.type,
                "USERS": payload.users,
                **({"ENTITY_TYPE": payload.entity_type} if payload.entity_type else {}),
                **({"ENTITY_ID": payload.entity_id} if payload.entity_id else {}),
            },
            scope_hint="im",
        )
        message_request = Bitrix24MethodRequest(
            method="im.message.add",
            params={
                "DIALOG_ID": "<chat_id_or_dialog_id>",
                "MESSAGE": payload.message,
            },
            scope_hint="im",
        )

        notes = [
            "Second request depends on chat identifier returned by im.chat.add or resolved by im.chat.get.",
            "For file attachments in new flows, prefer im.v2 file methods.",
        ]
        if mode == "execute":
            create_result = self.runtime.execute(create_request)
            return ExecutorOutcome(action="create_chat_and_send_message", mode=mode, execution=[create_result], notes=notes)
        return ExecutorOutcome(
            action="create_chat_and_send_message",
            mode=mode,
            plan=[self.runtime.generate(create_request), self.runtime.generate(message_request)],
            notes=notes,
        )

    def register_external_call(self, payload: RegisterExternalCallInput, *, mode: str = "generate") -> ExecutorOutcome:
        plan_requests = []
        if payload.external_line_id:
            plan_requests.append(
                Bitrix24MethodRequest(
                    method="telephony.externalLine.get",
                    params={},
                    scope_hint="telephony",
                )
            )
        plan_requests.extend([
            Bitrix24MethodRequest(
                method="telephony.externalCall.searchCrmEntities",
                params={"PHONE_NUMBER": payload.phone_number},
                scope_hint="telephony",
            ),
            Bitrix24MethodRequest(
                method="telephony.externalCall.register",
                params={
                    "USER_ID": payload.user_id,
                    "PHONE_NUMBER": payload.phone_number,
                    "TYPE": payload.call_type,
                    "CRM_CREATE": 1 if payload.crm_create else 0,
                    "EXTERNAL_CALL_ID": payload.external_call_id,
                    **({"LINE_NUMBER": payload.external_line_id} if payload.external_line_id else {}),
                },
                scope_hint="telephony",
            ),
        ])
        if payload.show_call_card:
            plan_requests.append(
                Bitrix24MethodRequest(
                    method="telephony.externalCall.show",
                    params={"CALL_ID": "<call_id>", "USER_ID": payload.user_id},
                    scope_hint="telephony",
                )
            )

        notes = [
            "Use unique EXTERNAL_CALL_ID for each physical call.",
            "Some telephony methods require application context instead of webhook context.",
            "After register/show stage, finish and attachRecord should be executed when the call ends.",
        ]
        if mode == "execute":
            first = self.runtime.execute(plan_requests[0])
            return ExecutorOutcome(action="register_external_call", mode=mode, execution=[first], notes=notes)
        return ExecutorOutcome(
            action="register_external_call",
            mode=mode,
            plan=[self.runtime.generate(request) for request in plan_requests],
            notes=notes,
        )
