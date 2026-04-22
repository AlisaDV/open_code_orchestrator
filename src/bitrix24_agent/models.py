from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


RuntimeMode = Literal["consult", "generate", "execute", "debug"]


class Bitrix24MethodRequest(BaseModel):
    method: str = Field(min_length=1)
    params: dict[str, Any] = Field(default_factory=dict)
    scope_hint: str | None = None
    expected_family: str | None = None


class Bitrix24DryRunPlan(BaseModel):
    mode: RuntimeMode
    method: str
    url: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    auth_mode: str
    scope_hint: str | None = None
    family_detected: str | None = None
    warnings: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class Bitrix24ExecutionResult(BaseModel):
    ok: bool
    status_code: int | None = None
    method: str
    url: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    response_json: dict[str, Any] | list[Any] | None = None
    response_text: str | None = None
    error: str | None = None


class Bitrix24ConsultationResult(BaseModel):
    query: str
    recommended_sections: list[str] = Field(default_factory=list)
    recommended_methods: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class Bitrix24DebugResult(BaseModel):
    problem: str
    likely_causes: list[str] = Field(default_factory=list)
    checks: list[str] = Field(default_factory=list)
    relevant_sections: list[str] = Field(default_factory=list)


class CreateCrmItemInput(BaseModel):
    entity_type_id: int
    fields: dict[str, Any] = Field(default_factory=dict)
    category_id: int | None = None
    stage_id: str | None = None
    use_specialized_family: str | None = None


class CreateTaskWithCrmLinkInput(BaseModel):
    title: str
    description: str
    responsible_id: int
    crm_binding: str
    accomplices: list[int] = Field(default_factory=list)
    auditors: list[int] = Field(default_factory=list)
    deadline: str | None = None
    disk_file_ids: list[int] = Field(default_factory=list)


class CreateChatAndSendMessageInput(BaseModel):
    title: str
    type: Literal["CHAT", "OPEN"] = "CHAT"
    users: list[int] = Field(default_factory=list)
    message: str
    entity_type: str | None = None
    entity_id: str | None = None


class RegisterExternalCallInput(BaseModel):
    external_line_id: str | None = None
    phone_number: str
    user_id: int
    external_call_id: str
    call_type: int = 1
    crm_create: bool = True
    show_call_card: bool = True


class ExecutorOutcome(BaseModel):
    action: str
    mode: RuntimeMode
    plan: list[Bitrix24DryRunPlan] = Field(default_factory=list)
    execution: list[Bitrix24ExecutionResult] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
