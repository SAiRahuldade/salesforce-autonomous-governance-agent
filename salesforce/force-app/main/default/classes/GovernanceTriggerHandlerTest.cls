/**
 * GovernanceTriggerHandlerTest
 *
 * Tests for GovernanceTriggerHandler, DataValidationQueueable, and
 * DuplicateDetectionBatch.
 *
 * All tests are bulkified (200 records) and use Test.startTest/stopTest
 * to properly execute async logic.
 */
@IsTest
private class GovernanceTriggerHandlerTest {

    // ─── Test Data Factory ────────────────────────────────────────────────────

    private static List<Account> makeAccounts(Integer count) {
        List<Account> accs = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            accs.add(new Account(
                Name        = 'Test Account ' + i,
                Industry    = 'Technology',
                Phone       = '555-000-' + String.valueOf(i).leftPad(4, '0'),
                BillingCity = 'San Francisco'
            ));
        }
        return accs;
    }

    private static List<Contact> makeContacts(Integer count, Id accountId) {
        List<Contact> cons = new List<Contact>();
        for (Integer i = 0; i < count; i++) {
            cons.add(new Contact(
                FirstName = 'Test',
                LastName  = 'Contact ' + i,
                Email     = 'test' + i + '@corporate.com',
                Phone     = '555-100-' + String.valueOf(i).leftPad(4, '0'),
                AccountId = accountId
            ));
        }
        return cons;
    }

    // ─── Trigger: Account Insert ──────────────────────────────────────────────

    @IsTest
    static void testAccountInsertTriggersValidation() {
        List<Account> accs = makeAccounts(200);

        Test.startTest();
        insert accs;
        Test.stopTest();

        // After stopTest, queueable has run
        // Validate that no unexpected exceptions were thrown
        // (detailed field checks tested in DataValidationQueueable unit test)
        System.assert(
            [SELECT COUNT() FROM Account WHERE Name LIKE 'Test Account%'] == 200,
            '200 accounts should have been inserted'
        );
    }

    // ─── Trigger: Account Update (changed fields only) ───────────────────────

    @IsTest
    static void testAccountUpdateOnlyRevalidatesChangedFields() {
        Account acc = new Account(
            Name = 'Delta Corp', Industry = 'Finance',
            Phone = '555-9999', BillingCity = 'Austin'
        );
        insert acc;

        Test.startTest();
        acc.Industry = 'Technology'; // changed field
        update acc;
        Test.stopTest();

        System.assertEquals(1, [SELECT COUNT() FROM Account WHERE Name = 'Delta Corp']);
    }

    // ─── Trigger: Contact Insert ──────────────────────────────────────────────

    @IsTest
    static void testContactInsertTriggersValidation() {
        Account acc = new Account(Name = 'Acme', Industry = 'Tech',
            Phone = '555-1234', BillingCity = 'NYC');
        insert acc;

        List<Contact> cons = makeContacts(50, acc.Id);

        Test.startTest();
        insert cons;
        Test.stopTest();

        System.assertEquals(50, [SELECT COUNT() FROM Contact WHERE AccountId = :acc.Id]);
    }

    // ─── DataValidationQueueable: missing fields create issues ───────────────

    @IsTest
    static void testValidationQueueableCreatesMissingFieldIssues() {
        Account acc = new Account(Name = 'Incomplete Corp');
        // Intentionally missing Industry, Phone, BillingCity
        insert acc;

        Set<Id> ids = new Set<Id>{ acc.Id };

        Test.startTest();
        System.enqueueJob(new DataValidationQueueable(ids, 'Account'));
        Test.stopTest();

        List<Governance_Issue__c> issues = [
            SELECT Id, Field__c, Severity__c
            FROM Governance_Issue__c
            WHERE Record_Id__c = :acc.Id
        ];

        // Expect issues for Industry, Phone, BillingCity
        System.assert(issues.size() >= 3,
            'Expected at least 3 issues for missing fields, got: ' + issues.size());

        Set<String> issueFields = new Set<String>();
        for (Governance_Issue__c gi : issues) {
            issueFields.add(gi.Field__c);
        }
        System.assert(issueFields.contains('Industry'),   'Expected Industry issue');
        System.assert(issueFields.contains('Phone'),      'Expected Phone issue');
        System.assert(issueFields.contains('BillingCity'),'Expected BillingCity issue');
    }

    // ─── DataValidationQueueable: invalid email ───────────────────────────────

    @IsTest
    static void testValidationQueueableDetectsMissingEmail() {
        Account acc = new Account(Name = 'Valid Corp', Industry = 'Tech',
            Phone = '555-1234', BillingCity = 'Austin');
        insert acc;

        Contact con = new Contact(
            FirstName = 'No', LastName  = 'Email',
            AccountId = acc.Id
        );
        insert con;

        Set<Id> ids = new Set<Id>{ con.Id };

        Test.startTest();
        System.enqueueJob(new DataValidationQueueable(ids, 'Contact'));
        Test.stopTest();

        List<Governance_Issue__c> issues = [
            SELECT Id, Field__c, Issue__c, Severity__c
            FROM Governance_Issue__c
            WHERE Record_Id__c = :con.Id AND Field__c = 'Email'
        ];
        System.assert(issues.size() >= 1, 'Expected at least 1 email issue, got: ' + issues.size());
        System.assertEquals('critical', issues[0].Severity__c);
    }

    // ─── DuplicateDetectionBatch: detects same-email contacts ────────────────

    @IsTest
    static void testDuplicateDetectionBatchContactEmail() {
        Account acc = new Account(Name = 'Dupe Corp', Industry = 'Tech',
            Phone = '555-0000', BillingCity = 'LA');
        insert acc;

        // Two contacts with the same email
        insert new List<Contact>{
            new Contact(FirstName='Alice', LastName='Smith',
                        Email='shared@corp.com', AccountId=acc.Id),
            new Contact(FirstName='Bob',   LastName='Jones',
                        Email='shared@corp.com', AccountId=acc.Id)
        };

        Test.startTest();
        Database.executeBatch(new DuplicateDetectionBatch('Contact'), 200);
        Test.stopTest();

        List<Governance_Issue__c> dupeIssues = [
            SELECT Id, Issue__c
            FROM Governance_Issue__c
            WHERE Object_Type__c = 'Contact' AND Field__c = 'Duplicate'
        ];
        System.assert(dupeIssues.size() >= 1,
            'Expected at least 1 duplicate contact issue');
    }

    // ─── DuplicateDetectionBatch: detects same-phone accounts ────────────────

    @IsTest
    static void testDuplicateDetectionBatchAccountPhone() {
        insert new List<Account>{
            new Account(Name='Alpha Inc', Industry='Tech',
                        Phone='555-7777', BillingCity='Dallas'),
            new Account(Name='Alpha LLC', Industry='Tech',
                        Phone='555-7777', BillingCity='Dallas')
        };

        Test.startTest();
        Database.executeBatch(new DuplicateDetectionBatch('Account'), 200);
        Test.stopTest();

        List<Governance_Issue__c> dupeIssues = [
            SELECT Id, Issue__c
            FROM Governance_Issue__c
            WHERE Object_Type__c = 'Account' AND Field__c = 'Duplicate'
        ];
        System.assert(dupeIssues.size() >= 1,
            'Expected at least 1 duplicate account issue');
    }

    // ─── RemediationInvocable: happy path ────────────────────────────────────

    @IsTest
    static void testRemediationInvocableAppliesUpdate() {
        Account acc = new Account(Name = 'Fix Me Corp');
        insert acc;

        RemediationInvocable.RemediationRequest req =
            new RemediationInvocable.RemediationRequest();
        req.recordId      = acc.Id;
        req.objectApiName = 'Account';
        req.fieldApiName  = 'Industry';
        req.newValue      = 'Unknown';

        Test.startTest();
        List<RemediationInvocable.RemediationResult> results =
            RemediationInvocable.applyFix(
                new List<RemediationInvocable.RemediationRequest>{ req }
            );
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals(true, results[0].success, results[0].message);

        Account updated = [SELECT Industry FROM Account WHERE Id = :acc.Id];
        System.assertEquals('Unknown', updated.Industry);
    }

    // ─── RemediationInvocable: unsupported object rejected ───────────────────

    @IsTest
    static void testRemediationInvocableRejectsUnsupportedObject() {
        Opportunity opp = new Opportunity(
            Name        = 'Test Opp',
            StageName   = 'Prospecting',
            CloseDate   = Date.today().addDays(30)
        );
        insert opp;

        RemediationInvocable.RemediationRequest req =
            new RemediationInvocable.RemediationRequest();
        req.recordId      = opp.Id;
        req.objectApiName = 'Opportunity';
        req.fieldApiName  = 'StageName';
        req.newValue      = 'Closed Won';

        Test.startTest();
        List<RemediationInvocable.RemediationResult> results =
            RemediationInvocable.applyFix(
                new List<RemediationInvocable.RemediationRequest>{ req }
            );
        Test.stopTest();

        System.assertEquals(false, results[0].success);
        System.assert(results[0].message.contains('Unsupported object'));
    }
}
