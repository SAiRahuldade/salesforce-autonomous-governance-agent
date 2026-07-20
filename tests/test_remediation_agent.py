from unittest.mock import MagicMock
import pytest
from backend.agents.remediation_agent import RemediationAgent


def test_generate_fixes_validation():
    agent = RemediationAgent(None)

    # 1. Warning validation issue (should have a proposed value and be auto-fixable)
    warning_issue = {
        "object": "Account",
        "record_id": "acc_123",
        "record_name": "Acme Corp",
        "field": "Industry",
        "issue": "Missing required field: Industry",
        "severity": "warning"
    }

    # 2. Critical validation issue (should NOT be auto-fixable)
    critical_issue = {
        "object": "Contact",
        "record_id": "con_456",
        "record_name": "John Doe",
        "field": "Email",
        "issue": "Missing email address",
        "severity": "critical"
    }

    validation_issues = [warning_issue, critical_issue]
    duplicate_issues = {}

    response = agent.generate_fixes(validation_issues, duplicate_issues)

    assert response["status"] == "success"
    assert response["summary"]["total_fixes"] == 2
    assert response["summary"]["auto_fixable"] == 1
    assert response["summary"]["manual_review"] == 1

    fixes = response["data"]["fixes"]
    
    # Check warning fix
    warning_fix = next(f for f in fixes if f["record_id"] == "acc_123")
    assert warning_fix["action"] == "UPDATE"
    assert warning_fix["proposed_value"] == "Unknown"
    assert warning_fix["safe_to_automate"] is True
    assert warning_fix["requires_manual_review"] is False

    # Check critical fix
    critical_fix = next(f for f in fixes if f["record_id"] == "con_456")
    assert critical_fix["action"] == "UPDATE"
    assert critical_fix["proposed_value"] is None
    assert critical_fix["safe_to_automate"] is False
    assert critical_fix["requires_manual_review"] is True


def test_generate_fixes_phone_warning():
    agent = RemediationAgent(None)

    phone_issue = {
        "object": "Account",
        "record_id": "acc_123",
        "record_name": "Acme Corp",
        "field": "Phone",
        "issue": "Missing phone number",
        "severity": "warning"
    }

    response = agent.generate_fixes([phone_issue], {})
    fixes = response["data"]["fixes"]

    assert len(fixes) == 1
    assert fixes[0]["proposed_value"] == "0000000000"
    assert fixes[0]["safe_to_automate"] is True


def test_missing_email_gets_placeholder_and_is_safe_to_automate():
    agent = RemediationAgent(None)
    issue = {
        "object": "Contact",
        "record_id": "con_123",
        "record_name": "Jane Doe",
        "field": "Email",
        "issue": "Missing email address",
        "issue_type": "missing_email",
        "severity": "warning",
    }

    response = agent.generate_fixes([issue], {})
    fixes = response["data"]["fixes"]

    assert len(fixes) == 1
    assert fixes[0]["proposed_value"] == "no-email-con_123@placeholder.internal"
    assert fixes[0]["safe_to_automate"] is True
    assert fixes[0]["requires_manual_review"] is False


def test_malformed_email_stays_gated():
    agent = RemediationAgent(None)
    issue = {
        "object": "Contact",
        "record_id": "con_456",
        "record_name": "John Doe",
        "field": "Email",
        "issue": "Invalid email format: bad-email",
        "issue_type": "malformed_email",
        "severity": "critical",
    }

    response = agent.generate_fixes([issue], {})
    fixes = response["data"]["fixes"]

    assert len(fixes) == 1
    assert fixes[0]["proposed_value"] is None
    assert fixes[0]["safe_to_automate"] is False
    assert fixes[0]["requires_manual_review"] is True


def test_generate_fixes_duplicates():
    agent = RemediationAgent(None)

    duplicate_issues = {
        "data": {
            "account_duplicates": [
                {
                    "type": "Account",
                    "record1_id": "acc_1",
                    "record1_name": "Acme Inc",
                    "record2_id": "acc_2",
                    "record2_name": "Acme",
                    "confidence": 95
                }
            ],
            "contact_duplicates": [
                {
                    "type": "Contact",
                    "record1_id": "con_1",
                    "record1_name": "Jane Doe",
                    "record2_id": "con_2",
                    "record2_name": "Jane A. Doe",
                    "confidence": 85
                }
            ]
        }
    }

    response = agent.generate_fixes([], duplicate_issues)

    assert response["status"] == "success"
    assert response["summary"]["total_fixes"] == 2
    assert response["summary"]["auto_fixable"] == 0
    assert response["summary"]["manual_review"] == 2

    fixes = response["data"]["fixes"]
    
    # Assert account duplicate action
    acc_dup = next(f for f in fixes if f["object"] == "Account")
    assert acc_dup["action"] == "MERGE"
    assert acc_dup["priority"] == "high"
    assert acc_dup["safe_to_automate"] is False
    assert acc_dup["requires_manual_review"] is True

    # Assert contact duplicate action
    con_dup = next(f for f in fixes if f["object"] == "Contact")
    assert con_dup["action"] == "MERGE"
    assert con_dup["priority"] == "medium"
    assert con_dup["safe_to_automate"] is False
    assert con_dup["requires_manual_review"] is True


def test_apply_fix_success():
    agent = RemediationAgent(None)
    sf_client_mock = MagicMock()

    valid_fix = {
        "action": "UPDATE",
        "object": "Account",
        "record_id": "acc_123",
        "field": "Industry",
        "proposed_value": "Unknown",
        "safe_to_automate": True
    }

    result = agent.apply_fix(sf_client_mock, valid_fix)

    assert result["status"] == "applied"
    assert "applied" in result
    assert result["applied"]["object"] == "Account"
    assert result["applied"]["record_id"] == "acc_123"
    assert result["applied"]["field"] == "Industry"
    assert result["applied"]["value"] == "Unknown"

    sf_client_mock.update_record.assert_called_once_with(
        "Account", "acc_123", {"Industry": "Unknown"}
    )


def test_apply_fix_manual_review_required():
    agent = RemediationAgent(None)
    sf_client_mock = MagicMock()

    # unsafe to automate
    unsafe_fix = {
        "action": "UPDATE",
        "object": "Account",
        "record_id": "acc_123",
        "field": "Industry",
        "proposed_value": "Unknown",
        "safe_to_automate": False
    }

    result = agent.apply_fix(sf_client_mock, unsafe_fix)
    assert result["status"] == "manual_review_required"
    sf_client_mock.update_record.assert_not_called()

    # action is not UPDATE
    merge_fix = {
        "action": "MERGE",
        "object": "Account",
        "record1_id": "acc_1",
        "record2_id": "acc_2",
        "safe_to_automate": True
    }

    result = agent.apply_fix(sf_client_mock, merge_fix)
    assert result["status"] == "manual_review_required"
    sf_client_mock.update_record.assert_not_called()


def test_apply_fix_validation_errors():
    agent = RemediationAgent(None)
    sf_client_mock = MagicMock()

    # Unsupported object
    invalid_object_fix = {
        "action": "UPDATE",
        "object": "Opportunity",
        "record_id": "opp_123",
        "field": "StageName",
        "proposed_value": "Closed Won",
        "safe_to_automate": True
    }
    with pytest.raises(ValueError, match="Unsupported Salesforce object"):
        agent.apply_fix(sf_client_mock, invalid_object_fix)

    # Missing record ID
    missing_id_fix = {
        "action": "UPDATE",
        "object": "Account",
        "field": "Industry",
        "proposed_value": "Unknown",
        "safe_to_automate": True
    }
    with pytest.raises(ValueError, match="Fix is missing the target record or field"):
        agent.apply_fix(sf_client_mock, missing_id_fix)

    # Missing field
    missing_field_fix = {
        "action": "UPDATE",
        "object": "Account",
        "record_id": "acc_123",
        "proposed_value": "Unknown",
        "safe_to_automate": True
    }
    with pytest.raises(ValueError, match="Fix is missing the target record or field"):
        agent.apply_fix(sf_client_mock, missing_field_fix)

    # Missing proposed value
    missing_value_fix = {
        "action": "UPDATE",
        "object": "Account",
        "record_id": "acc_123",
        "field": "Industry",
        "proposed_value": None,
        "safe_to_automate": True
    }
    with pytest.raises(ValueError, match="Fix is missing a proposed value"):
        agent.apply_fix(sf_client_mock, missing_value_fix)
