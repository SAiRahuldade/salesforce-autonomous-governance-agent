from typing import List, Dict

class RemediationAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "RemediationAgent"
    
    def generate_fixes(self, validation_issues: List[Dict], duplicate_issues: Dict) -> Dict:
        """Generate safe fix recommendations"""
        
        fixes = []
        fixes += self._fixes_for_validation(validation_issues)
        fixes += self._fixes_for_duplicates(duplicate_issues)
        
        return self._format_response(fixes)
    
    def _fixes_for_validation(self, issues: List[Dict]) -> List[Dict]:
        fixes = []
        
        for issue in issues:
            proposed_value = self._proposed_value_for_issue(issue)
            safe_to_automate = (
                issue.get("severity") == "warning" and
                proposed_value is not None
            )
            fixes.append({
                "action": "UPDATE",
                "object": issue['object'],
                "record_id": issue['record_id'],
                "record_name": issue['record_name'],
                "field": issue['field'],
                "proposed_value": proposed_value,
                "fix": self._format_update_fix(issue, proposed_value),
                "priority": issue['severity'],
                "safe_to_automate": safe_to_automate,
                "requires_manual_review": not safe_to_automate
            })
        
        return fixes
    
    def _fixes_for_duplicates(self, duplicate_data: Dict) -> List[Dict]:
        fixes = []
        
        all_dupes = (
            duplicate_data.get('data', {}).get('account_duplicates', []) +
            duplicate_data.get('data', {}).get('contact_duplicates', [])
        )
        
        for dup in all_dupes:
            fixes.append({
                "action": "MERGE",
                "object": dup.get('type', 'Unknown'),
                "record1_id": dup['record1_id'],
                "record1_name": dup['record1_name'],
                "record2_id": dup['record2_id'],
                "record2_name": dup['record2_name'],
                "fix": f"Review and merge duplicate records",
                "priority": "high" if dup['confidence'] > 90 else "medium",
                "safe_to_automate": False,
                "requires_manual_review": True
            })
        
        return fixes

    def apply_fix(self, sf_client, fix: Dict) -> Dict:
        """Apply a remediation fix when it is safe to automate."""

        if not fix.get("safe_to_automate"):
            return {
                "status": "manual_review_required",
                "message": "This recommendation needs human review before Salesforce is changed."
            }

        if fix.get("action") != "UPDATE":
            return {
                "status": "manual_review_required",
                "message": f"{fix.get('action', 'This action')} cannot be automated safely yet."
            }

        object_name = fix.get("object")
        record_id = fix.get("record_id")
        field = fix.get("field")
        proposed_value = fix.get("proposed_value")

        if object_name not in {"Account", "Contact", "Lead"}:
            raise ValueError(f"Unsupported Salesforce object: {object_name}")
        if not record_id or not field:
            raise ValueError("Fix is missing the target record or field.")
        if proposed_value is None:
            raise ValueError("Fix is missing a proposed value.")

        sf_client.update_record(object_name, record_id, {field: proposed_value})

        return {
            "status": "applied",
            "message": (
                f"Updated {object_name} {record_id}: "
                f"set {self._field_label(field)} field to '{proposed_value}'"
            ),
            "applied": {
                "object": object_name,
                "record_id": record_id,
                "field": field,
                "value": proposed_value
            }
        }

    def _proposed_value_for_issue(self, issue: Dict):
        object_name = issue.get("object")
        field = issue.get("field")
        issue_text = issue.get("issue", "")
        severity = issue.get("severity")

        if severity != "warning":
            return None

        defaults = {
            ("Account", "Industry"): "Unknown",
            ("Account", "BillingCity"): "Unknown",
            ("Lead", "Company"): "Unknown",
        }

        if field == "Phone" and (
            issue_text.startswith("Missing") or
            issue_text.startswith("Invalid")
        ):
            return "0000000000"

        return defaults.get((object_name, field))

    def _format_update_fix(self, issue: Dict, proposed_value) -> str:
        field_label = self._field_label(issue['field'])
        if proposed_value is None:
            return f"Review and set {field_label} field to the correct value"
        return f"Set {field_label} field to value '{proposed_value}'"

    def _field_label(self, field: str) -> str:
        labels = {
            "BillingCity": "Billing City",
            "BillingCountry": "Billing Country",
            "FirstName": "First Name",
            "LastName": "Last Name",
        }

        return labels.get(field, field)
    
    def _format_response(self, fixes: List[Dict]) -> Dict:
        return {
            "agent": self.name,
            "status": "success",
            "summary": {
                "total_fixes": len(fixes),
                "auto_fixable": len([f for f in fixes if f['safe_to_automate']]),
                "manual_review": len([f for f in fixes if f['requires_manual_review']])
            },
            "data": {"fixes": fixes}
        }
