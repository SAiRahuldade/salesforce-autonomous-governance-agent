from typing import List, Dict

class GovernanceAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.name = "GovernanceAgent"
    
    def analyze(self, accounts: List[Dict], contacts: List[Dict], leads: List[Dict]) -> Dict:
        """Analyze data governance health"""
        
        score = self._calculate_health_score(accounts, contacts, leads)
        recommendations = self._generate_recommendations(accounts, contacts, leads)
        stats = self._generate_stats(accounts, contacts, leads)
        
        return self._format_response(score, recommendations, stats)
    
    def _calculate_health_score(self, accounts, contacts, leads) -> int:
        score = 100
        
        for acc in accounts:
            if not acc.get('Phone'): score -= 2
            if not acc.get('Industry'): score -= 2
            if not acc.get('BillingCity'): score -= 3
        
        for con in contacts:
            if not con.get('Email'): score -= 3
            if not con.get('Phone'): score -= 1
        
        return max(0, score)
    
    def _generate_recommendations(self, accounts, contacts, leads) -> List[Dict]:
        recommendations = []
        
        missing_industry = [a for a in accounts if not a.get('Industry')]
        if missing_industry:
            recommendations.append({
                "priority": "high",
                "category": "Data Completeness",
                "recommendation": f"Fill Industry field for {len(missing_industry)} accounts",
                "affected_records": len(missing_industry),
                "business_impact": "Industry field enables market segmentation and reporting"
            })
        
        missing_city = [a for a in accounts if not a.get('BillingCity')]
        if missing_city:
            recommendations.append({
                "priority": "medium",
                "category": "Data Completeness",
                "recommendation": f"Add BillingCity for {len(missing_city)} accounts",
                "affected_records": len(missing_city),
                "business_impact": "Location data enables territory management"
            })
        
        missing_email = [c for c in contacts if not c.get('Email')]
        if missing_email:
            recommendations.append({
                "priority": "critical",
                "category": "Communication",
                "recommendation": f"Add email addresses for {len(missing_email)} contacts",
                "affected_records": len(missing_email),
                "business_impact": "Email is required for marketing campaigns"
            })
        
        return recommendations
    
    def _generate_stats(self, accounts, contacts, leads) -> Dict:
        return {
            "total_accounts": len(accounts),
            "total_contacts": len(contacts),
            "total_leads": len(leads),
            "accounts_with_phone": len([a for a in accounts if a.get('Phone')]),
            "accounts_with_industry": len([a for a in accounts if a.get('Industry')]),
            "contacts_with_email": len([c for c in contacts if c.get('Email')]),
        }
    
    def _format_response(self, score, recommendations, stats) -> Dict:
        return {
            "agent": self.name,
            "status": "success",
            "summary": {
                "health_score": score,
                "health_grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D",
                "total_recommendations": len(recommendations)
            },
            "data": {
                "health_score": score,
                "recommendations": recommendations,
                "org_stats": stats
            }
        }