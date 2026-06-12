from typing import List, Dict

class ComplianceAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "ComplianceAgent"
    
    def analyze(self, accounts: List[Dict], contacts: List[Dict]) -> Dict:
        """Check compliance rules"""
        violations = []
        
        # Rule 1: Accounts without contacts
        violations += self._check_accounts_without_contacts(accounts, contacts)
        
        # Rule 2: Contacts without accounts
        violations += self._check_orphan_contacts(contacts)
        
        # Rule 3: Suspicious email domains
        violations += self._check_email_domains(contacts)
        
        return self._format_response(violations)
    
    def _check_accounts_without_contacts(self, accounts, contacts):
        violations = []
        account_ids_with_contacts = set(
            c.get('AccountId') for c in contacts if c.get('AccountId')
        )
        
        for acc in accounts:
            if acc['Id'] not in account_ids_with_contacts:
                violations.append({
                    "rule": "Account must have at least one contact",
                    "object": "Account",
                    "record_id": acc['Id'],
                    "record_name": acc['Name'],
                    "severity": "warning",
                    "recommendation": "Add a primary contact to this account"
                })
        
        return violations
    
    def _check_orphan_contacts(self, contacts):
        violations = []
        
        for con in contacts:
            if not con.get('AccountId'):
                name = f"{con.get('FirstName','')} {con.get('LastName','')}".strip()
                violations.append({
                    "rule": "Contact must be linked to an Account",
                    "object": "Contact",
                    "record_id": con['Id'],
                    "record_name": name,
                    "severity": "warning",
                    "recommendation": "Link this contact to an Account"
                })
        
        return violations
    
    def _check_email_domains(self, contacts):
        violations = []
        free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        
        for con in contacts:
            email = con.get('Email', '')
            if email:
                domain = email.split('@')[-1].lower()
                if domain in free_domains:
                    name = f"{con.get('FirstName','')} {con.get('LastName','')}".strip()
                    violations.append({
                        "rule": "Business contacts should use corporate email",
                        "object": "Contact",
                        "record_id": con['Id'],
                        "record_name": name,
                        "severity": "warning",
                        "recommendation": f"Replace {email} with corporate email"
                    })
        
        return violations
    
    def _format_response(self, violations: List[Dict]) -> Dict:
        return {
            "agent": self.name,
            "status": "success",
            "summary": {
                "total_violations": len(violations),
                "critical": len([v for v in violations if v['severity'] == 'critical']),
                "warnings": len([v for v in violations if v['severity'] == 'warning'])
            },
            "data": {"violations": violations}
        }