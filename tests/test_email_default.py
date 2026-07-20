from backend.agents.data_validation import DataValidationAgent
from backend.agents.remediation_agent import RemediationAgent


def test_missing_email_gets_placeholder_and_auto_fixable():
    val = DataValidationAgent(None)
    rem = RemediationAgent(None)

    contacts = [
        {"Id": "con_1", "FirstName": "Alice", "LastName": "A", "Email": None, "Phone": None}
    ]
    issues = val._validate_contacts(contacts)
    email_issues = [issue for issue in issues if issue.get("field") == "Email"]
    assert len(email_issues) == 1
    issue = email_issues[0]
    assert issue["issue_type"] == "missing_email"
    assert issue["severity"] == "warning"

    fixes = rem._fixes_for_validation(issues)
    email_fixes = [fix for fix in fixes if fix.get("field") == "Email"]
    assert len(email_fixes) == 1
    fix = email_fixes[0]
    assert fix["safe_to_automate"] is True
    assert fix["proposed_value"].endswith("@placeholder.internal")


def test_malformed_email_stays_gated():
    val = DataValidationAgent(None)
    rem = RemediationAgent(None)

    contacts = [
        {"Id": "con_2", "FirstName": "Bob", "LastName": "B", "Email": "not-an-email", "Phone": None}
    ]
    issues = val._validate_contacts(contacts)
    email_issues = [issue for issue in issues if issue.get("field") == "Email"]
    assert len(email_issues) == 1
    issue = email_issues[0]
    assert issue["issue_type"] == "malformed_email"
    assert issue["severity"] == "critical"

    fixes = rem._fixes_for_validation(issues)
    email_fixes = [fix for fix in fixes if fix.get("field") == "Email"]
    assert len(email_fixes) == 1
    fix = email_fixes[0]
    assert fix["safe_to_automate"] is False
    assert fix["proposed_value"] is None
