import json
import re
from typing import List, Dict, Any

class DuplicateDetectionAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "DuplicateDetectionAgent"
    
    def analyze(self, accounts: List[Dict], contacts: List[Dict]) -> Dict:
        """Detect duplicates in accounts and contacts"""
        
        results = {
            "account_duplicates": self._find_account_duplicates(accounts),
            "contact_duplicates": self._find_contact_duplicates(contacts)
        }
        
        return self._format_response(results)
    
    def _find_account_duplicates(self, accounts: List[Dict]) -> List[Dict]:
        """Find duplicate accounts using rule-based + LLM analysis"""
        duplicates = []
        
        # Rule-based: same phone number
        phone_map = {}
        for acc in accounts:
            phone = acc.get('Phone')
            if phone:
                if phone in phone_map:
                    duplicates.append({
                        "record1_id": phone_map[phone]['Id'],
                        "record1_name": phone_map[phone]['Name'],
                        "record2_id": acc['Id'],
                        "record2_name": acc['Name'],
                        "reason": f"Same phone number: {phone}",
                        "confidence": 85,
                        "type": "Account"
                    })
                else:
                    phone_map[phone] = acc
        
        # Rule-based: similar names
        names = [(acc['Id'], acc['Name']) for acc in accounts]
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                id1, name1 = names[i]
                id2, name2 = names[j]
                # Check if one name contains the other
                n1 = name1.lower().replace('.','').replace(',','').strip()
                n2 = name2.lower().replace('.','').replace(',','').strip()
                if n1 in n2 or n2 in n1:
                    duplicates.append({
                        "record1_id": id1,
                        "record1_name": name1,
                        "record2_id": id2,
                        "record2_name": name2,
                        "reason": f"Similar company names",
                        "confidence": 75,
                        "type": "Account"
                    })
        
        return duplicates
    
    def _find_contact_duplicates(self, contacts: List[Dict]) -> List[Dict]:
        """Find duplicate contacts"""
        duplicates = []
        
        # Rule-based: same email
        email_map = {}
        for con in contacts:
            email = con.get('Email')
            if email:
                if email in email_map:
                    duplicates.append({
                        "record1_id": email_map[email]['Id'],
                        "record1_name": f"{email_map[email]['FirstName']} {email_map[email]['LastName']}",
                        "record2_id": con['Id'],
                        "record2_name": f"{con['FirstName']} {con['LastName']}",
                        "reason": f"Same email: {email}",
                        "confidence": 99,
                        "type": "Contact"
                    })
                else:
                    email_map[email] = con
        
        # Rule-based: same phone
        phone_map = {}
        for con in contacts:
            phone = con.get('Phone')
            name = f"{con['FirstName']} {con['LastName']}"
            if phone:
                if phone in phone_map:
                    prev = phone_map[phone]
                    prev_name = f"{prev['FirstName']} {prev['LastName']}"
                    # Only flag if different people same phone
                    if prev_name != name:
                        duplicates.append({
                            "record1_id": prev['Id'],
                            "record1_name": prev_name,
                            "record2_id": con['Id'],
                            "record2_name": name,
                            "reason": f"Same phone number: {phone}",
                            "confidence": 70,
                            "type": "Contact"
                        })
                else:
                    phone_map[phone] = con
        
        return duplicates
    
    def _format_response(self, data: Dict) -> Dict:
        total = len(data['account_duplicates']) + len(data['contact_duplicates'])
        return {
            "agent": self.name,
            "status": "success",
            "summary": {
                "total_duplicates_found": total,
                "account_duplicates": len(data['account_duplicates']),
                "contact_duplicates": len(data['contact_duplicates'])
            },
            "data": data
        }