# Playbook: Register External Call

## Goal

Integrate external telephony with Bitrix24 CRM.

## Methods

- `telephony.externalLine.add`
- `telephony.externalCall.searchCrmEntities`
- `telephony.externalCall.register`
- `telephony.externalCall.show`
- `telephony.externalCall.finish`
- `telephony.externalCall.attachRecord`

## Flow

1. register external line if not registered yet
2. search CRM entities by phone number
3. register call start with unique `EXTERNAL_CALL_ID`
4. optionally show call card to user
5. finish call
6. attach record
7. optionally attach transcription

## Constraints

- keep `EXTERNAL_CALL_ID` unique
- do not attach record before finish
- some calls work only in application context
