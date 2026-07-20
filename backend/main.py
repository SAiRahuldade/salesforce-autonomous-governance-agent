from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from requests.exceptions import Timeout
from dotenv import load_dotenv

from backend.services.sf_oauth import SalesforceOAuth
from backend.agents.duplicate_detection import DuplicateDetectionAgent
from backend.agents.data_validation import DataValidationAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.governance_agent import GovernanceAgent
from backend.agents.remediation_agent import RemediationAgent
from backend.services.featherless import generate_text, FeatherlessError

load_dotenv()

app = FastAPI(title="Salesforce Autonomous Governance Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AppState:
    sf = None
    dup_agent = None
    val_agent = None
    comp_agent = None
    gov_agent = None
    rem_agent = None

state = AppState()


class RemediationApplyRequest(BaseModel):
    fix: Dict


class FeatherlessRequest(BaseModel):
    prompt: str
    model: Optional[str] = "default"
    options: Optional[Dict] = None

@app.on_event("startup")
async def startup():
    state.sf = SalesforceOAuth()
    # Token will be fetched on first query if needed; 
    # if SF_ACCESS_TOKEN is in .env, it will be used directly.
    print("[OK] Salesforce OAuth initialized")
    
    # Initialize agents — no LLM needed yet (rule-based first)
    state.dup_agent = DuplicateDetectionAgent(None)
    state.val_agent = DataValidationAgent(None)
    state.comp_agent = ComplianceAgent(None)
    state.gov_agent = GovernanceAgent(None)
    state.rem_agent = RemediationAgent(None)
    print("[OK] All agents initialized")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/salesforce/status")
def sf_status():
    return state.sf.test_connection()

@app.post("/analyze/full")
def full_analysis():
    """Run all 5 agents and return complete report"""
    try:
        # Fetch data
        accounts = state.sf.query(
            "SELECT Id, Name, BillingCity, BillingCountry, Industry, Phone FROM Account LIMIT 50"
        )['records']
        
        contacts = state.sf.query(
            "SELECT Id, FirstName, LastName, Email, Phone, AccountId FROM Contact LIMIT 50"
        )['records']
        
        leads = state.sf.query(
            "SELECT Id, FirstName, LastName, Email, Company FROM Lead LIMIT 50"
        )['records']
        
        # Run all agents
        duplicates = state.dup_agent.analyze(accounts, contacts)
        validation = state.val_agent.analyze(accounts, contacts, leads)
        compliance = state.comp_agent.analyze(accounts, contacts)
        governance = state.gov_agent.analyze(accounts, contacts, leads)
        remediation = state.rem_agent.generate_fixes(
            validation['data']['issues'],
            duplicates
        )

        governance_issues_query = """
            SELECT Id, Name, Severity__c, Approval_Status__c, Approved__c,
                   Object_Type__c, Record_Id__c, Issue__c, Status__c, Proposed_Value__c, Safe_to_Automate__c, CreatedDate
            FROM Governance_Issue__c
            ORDER BY CreatedDate DESC
            LIMIT 100
        """
        raw_issues = state.sf.query(governance_issues_query).get('records', [])
        governance_issues = []
        for r in raw_issues:
            sev = (r.get("Severity__c") or "").lower()
            issue_val = (r.get("Issue__c") or "").lower()
            field_val = (r.get("Field__c") or "").lower()
            is_critical_or_dupe = (
                sev == "critical" or
                issue_val == "duplicate_merge" or
                field_val == "duplicate"
            )
            safe_to_automate = not is_critical_or_dupe

            governance_issues.append({
                "Id": r.get("Id"),
                "Name": r.get("Name"),
                "Severity__c": r.get("Severity__c"),
                "Approval_Status__c": r.get("Approval_Status__c"),
                "Approved__c": r.get("Approved__c"),
                "Object_Type__c": r.get("Object_Type__c"),
                "Record_Id__c": r.get("Record_Id__c"),
                "Issue__c": r.get("Issue__c"),
                "Field__c": r.get("Field__c"),
                "Status__c": r.get("Status__c"),
                "Proposed_Value__c": r.get("Proposed_Value__c"),
                "Safe_to_Automate__c": safe_to_automate,
                "safe_to_automate": safe_to_automate,
                "CreatedDate": r.get("CreatedDate"),
                "severity": r.get("Severity__c"),
                "approval_status": r.get("Approval_Status__c"),
                "approved": r.get("Approved__c"),
                "related_object": r.get("Object_Type__c"),
                "related_record_id": r.get("Record_Id__c"),
                "field": r.get("Field__c"),
                "proposed_value": r.get("Proposed_Value__c"),
                "description": r.get("Issue__c"),
                "created_date": r.get("CreatedDate"),
            })
        
        governance_issue_counts = {
            "critical": 0,
            "warning": 0,
            "medium": 0,
            "low": 0
        }
        governance_approval_counts = {
            "pending_approval": 0,
            "approved": 0,
            "not_submitted": 0
        }
        for r in raw_issues:
            sev = (r.get("Severity__c") or "medium").lower()
            if sev in governance_issue_counts:
                governance_issue_counts[sev] += 1
            else:
                governance_issue_counts[sev] = 1
            
            app_status = (r.get("Approval_Status__c") or "Not Submitted").lower()
            if r.get("Approved__c") is True:
                governance_approval_counts["approved"] += 1
            elif app_status == "submitted":
                governance_approval_counts["pending_approval"] += 1
            else:
                governance_approval_counts["not_submitted"] += 1

        # Python issues
        py_critical = (validation.get('summary', {}).get('critical', 0) +
                       compliance.get('summary', {}).get('critical', 0))
        py_warning = (validation.get('summary', {}).get('warnings', 0) +
                      compliance.get('summary', {}).get('warnings', 0) +
                      duplicates.get('summary', {}).get('total_duplicates_found', 0))

        # Combined/aggregated summary metrics
        summary_metrics = {
            "critical_count": py_critical + governance_issue_counts.get("critical", 0),
            "warning_count": py_warning + governance_issue_counts.get("warning", 0),
            "pending_approval_count": governance_approval_counts.get("pending_approval", 0),
            "approved_count": governance_approval_counts.get("approved", 0)
        }

        return {
            "status": "success",
            "agents_run": 5,
            "report": {
                "source_records": {
                    "accounts": accounts,
                    "contacts": contacts,
                    "leads": leads,
                },
                "duplicate_detection": duplicates,
                "data_validation": validation,
                "compliance": compliance,
                "governance": governance,
                "governance_issues": {"data": {"issues": governance_issues}},
                "governance_issue_counts": governance_issue_counts,
                "governance_approval_counts": governance_approval_counts,
                "summary_metrics": summary_metrics,
                "remediation": remediation
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/duplicates")
def analyze_duplicates():
    accounts = state.sf.query("SELECT Id, Name, Phone FROM Account LIMIT 50")['records']
    contacts = state.sf.query("SELECT Id, FirstName, LastName, Email, Phone FROM Contact LIMIT 50")['records']
    return state.dup_agent.analyze(accounts, contacts)

@app.post("/analyze/validation")
def analyze_validation():
    accounts = state.sf.query("SELECT Id, Name, BillingCity, Industry, Phone FROM Account LIMIT 50")['records']
    contacts = state.sf.query("SELECT Id, FirstName, LastName, Email, Phone, AccountId FROM Contact LIMIT 50")['records']
    leads = state.sf.query("SELECT Id, FirstName, LastName, Email, Company FROM Lead LIMIT 50")['records']
    return state.val_agent.analyze(accounts, contacts, leads)

@app.post("/analyze/governance")
def analyze_governance():
    accounts = state.sf.query("SELECT Id, Name, BillingCity, Industry, Phone FROM Account LIMIT 50")['records']
    contacts = state.sf.query("SELECT Id, FirstName, LastName, Email, Phone, AccountId FROM Contact LIMIT 50")['records']
    leads = state.sf.query("SELECT Id, FirstName, LastName, Email, Company FROM Lead LIMIT 50")['records']
    return state.gov_agent.analyze(accounts, contacts, leads)


@app.post("/analyze/governance-issues")
def analyze_governance_issues():
    """Fetch Governance_Issue__c records from Salesforce."""
    try:
        query = """
            SELECT Id, Name, Severity__c, Approval_Status__c, Approved__c,
                   Object_Type__c, Record_Id__c, Issue__c, Status__c, Proposed_Value__c, Safe_to_Automate__c, CreatedDate
            FROM Governance_Issue__c
            ORDER BY CreatedDate DESC
            LIMIT 100
        """
        result = state.sf.query(query)
        raw_issues = result.get('records', [])
        governance_issues = []
        for r in raw_issues:
            sev = (r.get("Severity__c") or "").lower()
            issue_val = (r.get("Issue__c") or "").lower()
            field_val = (r.get("Field__c") or "").lower()
            is_critical_or_dupe = (
                sev == "critical" or
                issue_val == "duplicate_merge" or
                field_val == "duplicate"
            )
            safe_to_automate = not is_critical_or_dupe

            governance_issues.append({
                "Id": r.get("Id"),
                "Name": r.get("Name"),
                "Severity__c": r.get("Severity__c"),
                "Approval_Status__c": r.get("Approval_Status__c"),
                "Approved__c": r.get("Approved__c"),
                "Object_Type__c": r.get("Object_Type__c"),
                "Record_Id__c": r.get("Record_Id__c"),
                "Issue__c": r.get("Issue__c"),
                "Field__c": r.get("Field__c"),
                "Status__c": r.get("Status__c"),
                "Proposed_Value__c": r.get("Proposed_Value__c"),
                "Safe_to_Automate__c": safe_to_automate,
                "safe_to_automate": safe_to_automate,
                "CreatedDate": r.get("CreatedDate"),
                "severity": r.get("Severity__c"),
                "approval_status": r.get("Approval_Status__c"),
                "approved": r.get("Approved__c"),
                "related_object": r.get("Object_Type__c"),
                "related_record_id": r.get("Record_Id__c"),
                "field": r.get("Field__c"),
                "proposed_value": r.get("Proposed_Value__c"),
                "description": r.get("Issue__c"),
                "created_date": r.get("CreatedDate"),
            })

        governance_issue_counts = {
            "critical": 0,
            "warning": 0,
            "medium": 0,
            "low": 0
        }
        governance_approval_counts = {
            "pending_approval": 0,
            "approved": 0,
            "not_submitted": 0
        }
        for r in raw_issues:
            sev = (r.get("Severity__c") or "medium").lower()
            if sev in governance_issue_counts:
                governance_issue_counts[sev] += 1
            else:
                governance_issue_counts[sev] = 1
            
            app_status = (r.get("Approval_Status__c") or "Not Submitted").lower()
            if r.get("Approved__c") is True:
                governance_approval_counts["approved"] += 1
            elif app_status == "submitted":
                governance_approval_counts["pending_approval"] += 1
            else:
                governance_approval_counts["not_submitted"] += 1

        return {
            "status": "success",
            "agent": "GovernanceAgent",
            "summary": f"Found {len(governance_issues)} governance issues",
            "data": {"issues": governance_issues},
            "governance_issue_counts": governance_issue_counts,
            "governance_approval_counts": governance_approval_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/remediation/apply")
def apply_remediation(request: RemediationApplyRequest):
    """Apply one recommended remediation action when safe."""
    try:
        result = state.rem_agent.apply_fix(state.sf, request.fix)
        return result
    except Timeout:
        raise HTTPException(
            status_code=504,
            detail="Salesforce timed out while applying this fix. Check your connection or VPN, then try again."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/featherless/generate")
def featherless_generate(request: FeatherlessRequest):
    """Generate text via Featherless AI using the server-side API key from environment."""
    try:
        opts = request.options or {}
        result = generate_text(request.prompt, model=request.model, **opts)
        return {"status": "success", "result": result}
    except FeatherlessError as fe:
        raise HTTPException(status_code=502, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
