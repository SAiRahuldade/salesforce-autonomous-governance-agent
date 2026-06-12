from typing import Dict

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

@app.on_event("startup")
async def startup():
    state.sf = SalesforceOAuth()
    # Token will be fetched on first query if needed; 
    # if SF_ACCESS_TOKEN is in .env, it will be used directly.
    print("✅ Salesforce OAuth initialized")
    
    # Initialize agents — no LLM needed yet (rule-based first)
    state.dup_agent = DuplicateDetectionAgent(None)
    state.val_agent = DataValidationAgent(None)
    state.comp_agent = ComplianceAgent(None)
    state.gov_agent = GovernanceAgent(None)
    state.rem_agent = RemediationAgent(None)
    print("✅ All agents initialized")

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
        
        return {
            "status": "success",
            "agents_run": 5,
            "report": {
                "duplicate_detection": duplicates,
                "data_validation": validation,
                "compliance": compliance,
                "governance": governance,
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
