# TODO

All items complete. See README.md for the full feature list and deployment guide.

## Completed
- [x] Fix/adjust tests so they don't require live Salesforce credentials during default CI/test runs.
- [x] Add unit tests for `RemediationAgent.generate_fixes()` and `apply_fix()` using mocked `sf_client`.
- [x] Re-run `pytest` to confirm pass.
- [x] Implement native Apex: `DuplicateDetectionBatch`, `DataValidationQueueable`, `RemediationInvocable`
- [x] Implement Trigger Handler framework: `GovernanceTriggerHandler`, `AccountTrigger`, `ContactTrigger`
- [x] Create `Governance_Issue__c` custom object
- [x] Create `Governance_Alert__e` Platform Event
- [x] Create `GovernanceRemediation` Record-Triggered Flow
- [x] Create `FeatherlessAI` Named Credential
- [x] Create `GovernanceTriggerHandlerTest` with >85% coverage target, bulkified
- [x] Create GitHub Actions CI pipeline (`python-tests` + `apex-tests` jobs)
- [x] Rewrite README with architecture diagram, quantified metrics, Agentforce alignment

## Pending (requires org access)
- [ ] Fix Salesforce Connected App OAuth settings (see README)
- [ ] Run `sf org login web --alias governance-org` once OAuth is fixed
- [ ] `sf project deploy start --source-dir force-app --target-org governance-org`
- [ ] Add `SFDX_AUTH_URL` to GitHub secrets to activate Apex CI job
