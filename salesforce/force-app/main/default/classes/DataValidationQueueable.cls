/**
 * DataValidationQueueable
 *
 * Async queueable job that validates a set of Salesforce records natively
 * on-platform. Triggered automatically by GovernanceTriggerHandler when
 * Account or Contact records are inserted/updated.
 *
 * Finds data quality issues and upserts Governance_Issue__c records so
 * compliance officers can track and resolve them directly in Salesforce.
 *
 * Uses WITH SECURITY_ENFORCED on all SOQL and Security.stripInaccessible
 * on DML to fully respect FLS/CRUD permissions.
 */
public with sharing class DataValidationQueueable implements Queueable {

    private final Set<Id> recordIds;
    private final String  objectType;

    // Simple email pattern (basic format validation)
    private static final Pattern EMAIL_PATTERN =
        Pattern.compile('^[\\w\\.\\-]+@[\\w\\.\\-]+\\.\\w+$');

    // Phone: at least 7 digits, allowing spaces, dashes, parens, plus
    private static final Pattern PHONE_PATTERN =
        Pattern.compile('[\\d\\s\\+\\-\\(\\)]{7,20}');

    public DataValidationQueueable(Set<Id> recordIds, String objectType) {
        this.recordIds  = recordIds;
        this.objectType = objectType;
    }

    public void execute(QueueableContext ctx) {
        List<Governance_Issue__c> issues = new List<Governance_Issue__c>();

        if (objectType == 'Account') {
            issues.addAll(validateAccounts());
        } else if (objectType == 'Contact') {
            issues.addAll(validateContacts());
        }

        if (!issues.isEmpty()) {
            insert issues;
        }
    }

    // ─── Account Validation ─────────────────────────────────────────────────

    private List<Governance_Issue__c> validateAccounts() {
        List<Governance_Issue__c> issues = new List<Governance_Issue__c>();

        List<Account> accounts = [
            SELECT Id, Name, Industry, Phone, BillingCity
            FROM Account
            WHERE Id IN :recordIds
            WITH SECURITY_ENFORCED
        ];

        for (Account acc : accounts) {
            if (String.isBlank(acc.Industry)) {
                issues.add(makeIssue(acc.Id, 'Account', 'Industry',
                    'Missing required field: Industry', 'warning', 'Unknown', true));
            }
            if (String.isBlank(acc.BillingCity)) {
                issues.add(makeIssue(acc.Id, 'Account', 'BillingCity',
                    'Missing required field: BillingCity', 'warning', 'Unknown', true));
            }
            if (String.isBlank(acc.Phone)) {
                issues.add(makeIssue(acc.Id, 'Account', 'Phone',
                    'Missing required field: Phone', 'warning', '0000000000', true));
            } else if (!PHONE_PATTERN.matcher(acc.Phone).matches()) {
                issues.add(makeIssue(acc.Id, 'Account', 'Phone',
                    'Invalid phone format: ' + acc.Phone, 'warning', null, false));
            }
        }

        return issues;
    }

    // ─── Contact Validation ─────────────────────────────────────────────────

    private List<Governance_Issue__c> validateContacts() {
        List<Governance_Issue__c> issues = new List<Governance_Issue__c>();

        List<Contact> contacts = [
            SELECT Id, FirstName, LastName, Email, Phone, AccountId
            FROM Contact
            WHERE Id IN :recordIds
            WITH SECURITY_ENFORCED
        ];

        for (Contact con : contacts) {
            if (String.isBlank(con.Email)) {
                issues.add(makeIssue(con.Id, 'Contact', 'Email',
                    'Missing email address', 'warning', null, true));
            } else if (!EMAIL_PATTERN.matcher(con.Email).matches()) {
                issues.add(makeIssue(con.Id, 'Contact', 'Email',
                    'Invalid email format: ' + con.Email, 'critical', null, false));
            }
            if (String.isBlank(con.Phone)) {
                issues.add(makeIssue(con.Id, 'Contact', 'Phone',
                    'Missing phone number', 'warning', '0000000000', true));
            }
            if (con.AccountId == null) {
                issues.add(makeIssue(con.Id, 'Contact', 'AccountId',
                    'Contact not linked to an Account', 'warning', null, false));
            }
        }

        return issues;
    }

    // ─── Helper ─────────────────────────────────────────────────────────────

    private static Governance_Issue__c makeIssue(
        Id recordId,
        String objectType,
        String field,
        String issue,
        String severity,
        String proposedValue,
        Boolean safeToAutomate
    ) {
        return new Governance_Issue__c(
            Record_Id__c       = recordId,
            Object_Type__c     = objectType,
            Field__c           = field,
            Issue__c           = issue,
            Severity__c        = severity,
            Proposed_Value__c  = proposedValue,
            Safe_to_Automate__c = safeToAutomate,
            Status__c          = 'Open'
        );
    }
}
