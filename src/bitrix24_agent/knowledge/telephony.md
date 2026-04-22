# Bitrix24 Telephony

## Two major modes

1. external telephony integration
2. built-in telephony / SIP / Voximplant management

## External telephony flow

1. `telephony.externalLine.add`
2. `telephony.externalCall.register`
3. optional `telephony.externalCall.show`
4. `telephony.externalCall.finish`
5. `telephony.externalCall.attachRecord`
6. optional `telephony.call.attachTranscription`

## Important identifiers

- `USER_ID`
- `CALL_ID`
- `EXTERNAL_CALL_ID`
- `LINE_ID`
- `CONFIG_ID`

## Constraints

- some external telephony methods work only in app context
- `EXTERNAL_CALL_ID` should be unique per physical call
- attach record only after call finish

## CRM linkage

Use `telephony.externalCall.searchCrmEntities` to find CRM entities by phone number.
