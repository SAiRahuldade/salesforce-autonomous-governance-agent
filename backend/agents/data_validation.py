import re
from typing import List, Dict, Any

class DataValidationAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "DataValidationAgent"
    
    def analyze(self, accounts: List[Dict], contacts: List[Dict], leads: List[Dict]) -> Dict:
        """Validate data quality across all objects"""
        
        issues = []
        issues += self._validate_accounts(accounts)
        issues += self._validate_contacts(contacts)
        issues += self._validate_leads(leads)
        
        return self._format_response(issues)
    
    def _validate_accounts(self, accounts: List[Dict]) -> List[Dict]:
        issues = []
        required = ['Name', 'Industry', 'Phone', 'BillingCity']
        
        for acc in accounts:
            for field in required:
                val = acc.get(field)
                if not val or val == 'None':
                    issues.append({
                        "object": "Account",
                        "record_id": acc['Id'],
                        "record_name": acc.get('Name', 'Unknown'),
                        "field": field,
                        "issue": f"Missing required field: {field}",
                        "severity": "critical" if field == 'Name' else "warning"
                    })
            
            # Validate phone format
            phone = acc.get('Phone', '')
            if phone and not re.match(r'[\d\s\+\-\(\)]{7,20}', str(phone)):
                issues.append({
                    "object": "Account",
                    "record_id": acc['Id'],
                    "record_name": acc.get('Name', 'Unknown'),
                    "field": "Phone",
                    "issue": f"Invalid phone format: {phone}",
                    "severity": "warning"
                })
        
        return issues
    
    def _validate_contacts(self, contacts: List[Dict]) -> List[Dict]:
        issues = []
        email_regex = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

        for con in contacts:
            name = f"{con.get('FirstName','')} {con.get('LastName','')}".strip()
            
            # Check email
            email = con.get('Email', '')
            if not email:
                issues.append({
                    "object": "Contact",
                    "record_id": con['Id'],
                    "record_name": name,
                    "field": "Email",
                    "issue_type": "missing_email",
                    "issue": "Missing email address",
                    "severity": "warning",
                })
            elif not email_regex.match(str(email)):
                issues.append({
                    "object": "Contact",
                    "record_id": con['Id'],
                    "record_name": name,
                    "field": "Email",
                    "issue_type": "malformed_email",
                    "issue": f"Invalid email format: {email}",
                    "severity": "critical",
                })
            
            # Check phone
            if not con.get('Phone'):
                issues.append({
                    "object": "Contact",
                    "record_id": con['Id'],
                    "record_name": name,
                    "field": "Phone",
                    "issue": "Missing phone number",
                    "severity": "warning"
                })
        
        return issues
    
    def _validate_leads(self, leads: List[Dict]) -> List[Dict]:
        issues = []
        
        for lead in leads:
            name = f"{lead.get('FirstName','')} {lead.get('LastName','')}".strip()
            email = lead.get('Email')
            if not email:
                issues.append({
                    "object": "Lead",
                    "record_id": lead['Id'],
                    "record_name": name,
                    "field": "Email",
                    "issue_type": "missing_email",
                    "issue": "Missing email address",
                    "severity": "warning",
                })
            
            if not lead.get('Company'):
                issues.append({
                    "object": "Lead",
                    "record_id": lead['Id'],
                    "record_name": name,
                    "field": "Company",
                    "issue": "Missing company name",
                    "severity": "warning"
                })
        
        return issues
    
    def _format_response(self, issues: List[Dict]) -> Dict:
        critical = [i for i in issues if i['severity'] == 'critical']
        warnings = [i for i in issues if i['severity'] == 'warning']
        
        return {
            "agent": self.name,
            "status": "success",
            "summary": {
                "total_issues": len(issues),
                "critical": len(critical),
                "warnings": len(warnings)
            },
            "data": {
                "issues": issues
            }
        }