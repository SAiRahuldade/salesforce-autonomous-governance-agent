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
            fixes.append({
                "action": "UPDATE",
                "object": issue['object'],
                "record_id": issue['record_id'],
                "record_name": issue['record_name'],
                "field": issue['field'],
                "fix": f"Set {issue['field']} to a valid value",
                "priority": issue['severity'],
                "safe_to_automate": False,
                "requires_manual_review": True
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