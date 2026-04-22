# Playbook: Create CRM Item

## Use when

- creating a lead, deal, contact, company, or smart-process item

## Decision

- standard CRM object with obvious family: use specialized family if it makes code clearer
- dynamic/smart-process or generic pipeline code: use `crm.item.add`

## Inputs to gather

- auth mode
- scope `crm`
- object type or `entityTypeId`
- required fields
- optional `categoryId`
- optional `stageId`

## Minimal path

1. identify object family
2. get available fields if field set is unclear
3. build `fields`
4. call add method
5. store returned `id`

## Common mistakes

- missing `entityTypeId`
- invalid stage/category combination
- using wrong scope
