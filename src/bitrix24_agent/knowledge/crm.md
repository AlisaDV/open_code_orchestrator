# Bitrix24 CRM

## Primary model

CRM supports both specialized endpoint families and universal `crm.item.*` methods.

## Prefer universal methods when

- working with smart processes
- working through `entityTypeId`
- building generic CRM sync code

Core methods:

- `crm.item.add`
- `crm.item.update`
- `crm.item.get`
- `crm.item.list`
- `crm.item.fields`

## Prefer specialized families when

- the scenario is object-specific
- docs or business logic clearly target deals, leads, contacts, companies, quotes

Examples:

- `crm.deal.*`
- `crm.lead.*`
- `crm.contact.*`
- `crm.company.*`
- `crm.quote.*`

## Important identifiers

- `entityTypeId` — object type
- `id` — item id
- `categoryId` — funnel/pipeline
- `stageId` — stage

## Useful related methods

- `crm.category.list`
- `crm.status.list`
- `crm.timeline.comment.add`
- `crm.activity.add`
- `crm.automation.trigger.add`
- `crm.automation.trigger.execute`

## Agent guidance

If the request says “lead/deal/contact/company”, do not blindly default to `crm.item.*`; choose the clearer method family unless dynamic object support is needed.
