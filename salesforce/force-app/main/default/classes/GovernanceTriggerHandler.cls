/**
 * GovernanceTriggerHandler
 *
 * Central handler for Account and Contact trigger events.
 * Follows the Trigger Handler framework pattern — thin triggers
 * delegate all logic here, keeping triggers code-free.
 *
 * On insert or update it enqueues DataValidationQueueable for async
 * validation, keeping trigger execution well within governor limits.
 */
public with sharing class GovernanceTriggerHandler {

    // ─── Account Trigger Entrypoints ────────────────────────────────────────

    public static void onAccountBeforeInsert(List<Account> newAccounts) {
        // Reserved for synchronous before-insert logic (e.g. default field stamping)
    }

    public static void onAccountAfterInsert(List<Account> newAccounts) {
        Set<Id> ids = new Map<Id, Account>(newAccounts).keySet();
        enqueueValidation(ids, 'Account');
    }

    public static void onAccountAfterUpdate(
        List<Account> newAccounts,
        Map<Id, Account> oldMap
    ) {
        Set<Id> changedIds = new Set<Id>();
        for (Account acc : newAccounts) {
            Account old = oldMap.get(acc.Id);
            if (
                acc.Name        != old.Name        ||
                acc.Phone       != old.Phone       ||
                acc.Industry    != old.Industry    ||
                acc.BillingCity != old.BillingCity
            ) {
                changedIds.add(acc.Id);
            }
        }
        if (!changedIds.isEmpty()) {
            enqueueValidation(changedIds, 'Account');
        }
    }

    // ─── Contact Trigger Entrypoints ────────────────────────────────────────

    public static void onContactBeforeInsert(List<Contact> newContacts) {
        // Reserved for synchronous before-insert logic
    }

    public static void onContactAfterInsert(List<Contact> newContacts) {
        Set<Id> ids = new Map<Id, Contact>(newContacts).keySet();
        enqueueValidation(ids, 'Contact');
    }

    public static void onContactAfterUpdate(
        List<Contact> newContacts,
        Map<Id, Contact> oldMap
    ) {
        Set<Id> changedIds = new Set<Id>();
        for (Contact con : newContacts) {
            Contact old = oldMap.get(con.Id);
            if (
                con.Email != old.Email ||
                con.Phone != old.Phone ||
                con.AccountId != old.AccountId
            ) {
                changedIds.add(con.Id);
            }
        }
        if (!changedIds.isEmpty()) {
            enqueueValidation(changedIds, 'Contact');
        }
    }

    // ─── Private Helpers ────────────────────────────────────────────────────

    private static void enqueueValidation(Set<Id> recordIds, String objectType) {
        if (!System.isFuture() && !System.isBatch()) {
            System.enqueueJob(new DataValidationQueueable(recordIds, objectType));
        }
    }
}
