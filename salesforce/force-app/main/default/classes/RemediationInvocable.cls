/**
 * RemediationInvocable
 *
 * @InvocableMethod that allows Salesforce Flow (Record-Triggered or Screen Flow)
 * to call this Apex action and apply safe field-level corrections to Account,
 * Contact, or Lead records.
 *
 * This class demonstrates "clicks-not-code" integration:
 * a Flow decides *when* to remediate; Apex handles *how* safely.
 *
 * Uses Security.stripInaccessible to respect FLS — updates will only be
 * applied for fields the running user has write access to.
 */
public with sharing class RemediationInvocable {

    public class RemediationRequest {
        @InvocableVariable(label='Record Id' required=true)
        public Id recordId;

        @InvocableVariable(label='Object API Name' required=true)
        public String objectApiName;

        @InvocableVariable(label='Field API Name' required=true)
        public String fieldApiName;

        @InvocableVariable(label='New Value' required=true)
        public String newValue;
    }

    public class RemediationResult {
        @InvocableVariable(label='Success')
        public Boolean success;

        @InvocableVariable(label='Message')
        public String message;
    }

    @InvocableMethod(
        label       = 'Apply Governance Remediation'
        description = 'Apply a safe field-level fix to an Account, Contact, or Lead record. Called by the GovernanceRemediation Flow.'
        category    = 'Data Governance'
    )
    public static List<RemediationResult> applyFix(List<RemediationRequest> requests) {
        List<RemediationResult> results = new List<RemediationResult>();

        Set<String> allowedObjects = new Set<String>{'Account', 'Contact', 'Lead'};

        for (RemediationRequest req : requests) {
            RemediationResult res = new RemediationResult();
            try {
                if (!allowedObjects.contains(req.objectApiName)) {
                    res.success = false;
                    res.message = 'Unsupported object: ' + req.objectApiName;
                    results.add(res);
                    continue;
                }

                // Build SObject dynamically
                SObject record = Schema.getGlobalDescribe()
                    .get(req.objectApiName)
                    .newSObject(req.recordId);
                record.put(req.fieldApiName, req.newValue);

                // Strip fields the running user cannot write
                List<SObject> strippedList = Security.stripInaccessible(
                    AccessType.UPDATABLE,
                    new List<SObject>{ record }
                ).getRecords();

                if (strippedList.isEmpty()) {
                    res.success = false;
                    res.message = 'FLS check failed — user does not have write access to ' +
                                  req.fieldApiName + ' on ' + req.objectApiName;
                } else {
                    // Critical / destructive fixes require approval before update
                    Governance_Issue__c issue = getIssueForRecord(req.recordId, req.fieldApiName);
                    Boolean requiresApproval = issue != null &&(
                        issue.Severity__c == 'critical' ||
                        issue.Field__c == 'Duplicate'
                    );

                    if (requiresApproval && !issue.Approved__c) {
                        submitForApproval(issue.Id, req.objectApiName, req.fieldApiName);
                        res.success = false;
                        res.message = 'Approval required before applying this fix. The governance issue was submitted to Salesforce approval.';
                        results.add(res);
                        continue;
                    }

                    Database.update(strippedList);

                    // Mark the Governance_Issue__c as Resolved
                    resolveIssue(req.recordId, req.fieldApiName);

                    res.success = true;
                    res.message = 'Updated ' + req.objectApiName + ' ' + req.recordId +
                                  ': set ' + req.fieldApiName + ' = "' + req.newValue + '"';
                }
            } catch (Exception e) {
                res.success = false;
                res.message = 'Error: ' + e.getMessage();
            }
            results.add(res);
        }

        return results;
    }

    // ─── Private Helper ──────────────────────────────────────────────────────

    private static Governance_Issue__c getIssueForRecord(Id recordId, String fieldApiName) {
        List<Governance_Issue__c> issues = [
            SELECT Id, Field__c, Severity__c, Approved__c, Approval_Status__c
            FROM Governance_Issue__c
            WHERE Record_Id__c = :recordId
              AND Field__c     = :fieldApiName
            ORDER BY CreatedDate DESC
            LIMIT 1
        ];
        return issues.isEmpty() ? null : issues[0];
    }

    private static void submitForApproval(Id issueId, String objectApiName, String fieldApiName) {
        Governance_Issue__c issue = [
            SELECT Id, Approval_Status__c
            FROM Governance_Issue__c
            WHERE Id = :issueId
            LIMIT 1
        ];
        if (issue == null) {
            return;
        }

        issue.Approval_Status__c = 'Submitted';
        update issue;

        try {
            Approval.ProcessSubmitRequest req = new Approval.ProcessSubmitRequest();
            req.setObjectId(issueId);
            req.setSubmitterId(UserInfo.getUserId());
            req.setComments('Submitted from Governance remediation flow for ' + objectApiName + '.' + fieldApiName);
            Approval.process(req);
        } catch (Exception e) {
            issue.Approval_Status__c = 'Not Submitted';
            update issue;
            throw e;
        }
    }

    private static void resolveIssue(Id recordId, String fieldApiName) {
        List<Governance_Issue__c> openIssues = [
            SELECT Id, Status__c
            FROM Governance_Issue__c
            WHERE Record_Id__c = :recordId
              AND Field__c     = :fieldApiName
              AND Status__c    = 'Open'
            LIMIT 50
        ];
        for (Governance_Issue__c gi : openIssues) {
            gi.Status__c = 'Resolved';
            gi.Approval_Status__c = 'Approved';
            gi.Approved__c = true;
        }
        if (!openIssues.isEmpty()) {
            update openIssues;
        }
    }
}
