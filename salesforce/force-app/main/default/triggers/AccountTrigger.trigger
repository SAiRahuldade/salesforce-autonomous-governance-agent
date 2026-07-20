trigger AccountTrigger on Account (before insert, after insert, after update) {
    if (Trigger.isBefore && Trigger.isInsert) {
        GovernanceTriggerHandler.onAccountBeforeInsert(Trigger.new);
    }
    if (Trigger.isAfter && Trigger.isInsert) {
        GovernanceTriggerHandler.onAccountAfterInsert(Trigger.new);
    }
    if (Trigger.isAfter && Trigger.isUpdate) {
        GovernanceTriggerHandler.onAccountAfterUpdate(Trigger.new, Trigger.oldMap);
    }
}
