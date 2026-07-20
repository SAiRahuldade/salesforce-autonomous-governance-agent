trigger ContactTrigger on Contact (before insert, after insert, after update) {
    if (Trigger.isBefore && Trigger.isInsert) {
        GovernanceTriggerHandler.onContactBeforeInsert(Trigger.new);
    }
    if (Trigger.isAfter && Trigger.isInsert) {
        GovernanceTriggerHandler.onContactAfterInsert(Trigger.new);
    }
    if (Trigger.isAfter && Trigger.isUpdate) {
        GovernanceTriggerHandler.onContactAfterUpdate(Trigger.new, Trigger.oldMap);
    }
}
