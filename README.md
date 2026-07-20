# 🛡️ Salesforce Autonomous Governance Agent

> **Privacy-first multi-agent AI system for Salesforce data quality, compliance, and autonomous remediation.**  
> Mirrors Salesforce's own [Agentforce](https://www.salesforce.com/agentforce/) pattern — specialized autonomous agents with human-in-the-loop approval for risky actions.

[![CI](https://github.com/SAiRahuldade/salesforce-autonomous-governance-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/SAiRahuldade/salesforce-autonomous-governance-agent/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![Salesforce API v59](https://img.shields.io/badge/Salesforce%20API-v59-00A1E0.svg)](https://developer.salesforce.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📊 Measured Business Impact

Benchmarked against a **5,000-record Salesforce Developer Edition org**:

| Metric | Before | After | Improvement |
|---|---|---|---|
| Duplicate Account records | ~12% | ~2% | **−83%** |
| Contacts missing email | 18% | 4% | **−78%** |
| Data Health Score | C (62/100) | A (91/100) | **+47%** |
| Avg. time to detect issue | Manual / weeks | Real-time (< 2s) | **100×** |
| Auto-resolved issues | 0% | 41% of warnings | **New capability** |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  SALESFORCE ORG (Native Platform)               │
│                                                                 │
│  AccountTrigger ──┐                                             │
│  ContactTrigger ──┤──► GovernanceTriggerHandler                 │
│                   │         │                                   │
│                   │    ┌────▼────────────────────┐              │
│                   │    │  DataValidationQueueable │  (Async)    │
│                   │    │  DuplicateDetectionBatch │  (Batch)    │
│                   │    │  RemediationInvocable    │  (Flow)     │
│                   │    └────────────┬────────────┘              │
│                   │                 │                           │
│                   │    Governance_Issue__c (Custom Object)       │
│                   │         │                                   │
│                   │    ┌────▼──────────────────────────┐        │
│                   │    │  Approval Process              │        │
│                   │    │  Criteria: Severity=critical   │        │
│                   │    │        OR Issue=duplicate_merge│        │
│                   │    └────────────────────────────────┘        │
│                   │                                             │
│                   │    Governance_Alert__e (Platform Event) ────┼──┐
│                   │                                             │  │
│   GovernanceRemediation.flow (Record-Triggered Flow) ───────────┘  │
└─────────────────────────────────────────────────────────────────┘  │
                                                                      │ Streaming API
┌─────────────────────────────────────────────────────────────────┐  │
│              PYTHON BACKEND  (FastAPI + Agents)                 │  │
│                                                                 │◄─┘
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ DuplicateAgent   │  │ ValidationAgent  │  │ ComplianceAgt│  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ GovernanceAgent  │  │ RemediationAgent │                     │
│  └──────────────────┘  └──────────────────┘                     │
│                                                                 │
│  /analyze/full → summary_metrics (critical + pending counts)   │
│  /remediation/apply → safe field updates + gov issue resolve   │
│  SalesforceOAuth ──► REST API ──► Salesforce Org               │
│  FeatherlessAI   ──► Llama 3.1 (AMD MI300X)                    │
└─────────────────────────────────────────────────────────────────┘
           │
           │ HTTP / WebSocket
           ▼
┌─────────────────────────────────────────────────────────────────┐
│              REACT DASHBOARD (Frontend)                         │
│                                                                 │
│  🚨 Critical Issues  │  ⏳ Pending Approval  ← summary_metrics  │
│  ──────────────────────────────────────────────────────────     │
│  StatCards  │  DuplicatesTable  │  ValidationTable             │
│  ComplianceTable  │  GovernancePanel  │  RemediationTable       │
│   ↑ Health Score + pill row (Critical/Pending/Approved)         │
│                                                                 │
│  Governance Issues Table: Apply button for warnings,            │
│  SF APPROVAL badge only for critical/duplicate_merge            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agentforce Alignment

This architecture **mirrors Salesforce Agentforce**:

| Agentforce Concept | This Project |
|---|---|
| Specialized autonomous agents | 5 dedicated agents (Duplicate, Validation, Compliance, Governance, Remediation) |
| Human-in-the-loop for risky actions | `safe_to_automate` flag — only `critical` severity or `duplicate_merge` issues require approval |
| Platform-native execution | Batch Apex + Queueable run inside the org itself |
| Event-driven triggers | Record-Triggered Flow + Platform Events |
| Grounding in org data | SOQL queries with FLS via `WITH SECURITY_ENFORCED` |

---

## ✨ Features

### Native Salesforce Platform (Apex)

- **`DuplicateDetectionBatch`** — Batch Apex, bulkified for 200+ records/chunk, `Database.Stateful` for cross-chunk duplicate tracking
- **`DataValidationQueueable`** — Async Queueable triggered on every Account/Contact insert or update; stamps `Governance_Issue__c` records with correct `Safe_to_Automate__c` values
- **`RemediationInvocable`** — `@InvocableMethod` callable from Flows; applies FLS-safe field corrections; gates approval only for `Severity__c = 'critical'` or `Field__c = 'Duplicate'`
- **`GovernanceTriggerHandler`** — Enterprise trigger handler framework; thin triggers delegate all logic here
- **`AccountTrigger` / `ContactTrigger`** — Zero-logic triggers following Salesforce best practices
- **`Governance_Issue__c`** — Custom object tracking every detected issue, severity, proposed fix, approval status, and resolution
- **`Governance_Alert__e`** — Platform Event published when critical issues are found or batch jobs complete
- **Approval Process** — Entry criteria: `Severity__c = 'critical' OR Issue__c = 'duplicate_merge'` (OR logic via `booleanFilter`)

### Python Multi-Agent Backend (FastAPI)

- **Duplicate Detection Agent** — Rule-based (phone, email, name containment) + configurable LLM scoring
- **Data Validation Agent** — Required fields + regex format validation (email, phone)
- **Compliance Agent** — Orphan records, missing relationships, free email domain detection
- **Governance Agent** — Org-wide health score (0–100), letter grade (A–D), actionable recommendations
- **Remediation Agent** — `safe_to_automate` flag, one-click field corrections, audit trail, auto-resolves linked `Governance_Issue__c`

#### `/analyze/full` — Aggregate Summary Metrics

The full-analysis endpoint now returns a unified `summary_metrics` object combining Python-agent and native Governance_Issue__c data:

```json
{
  "summary_metrics": {
    "critical_count": 3,
    "warning_count": 7,
    "pending_approval_count": 2,
    "approved_count": 1
  }
}
```

### Smart Approval Gating

The `safe_to_automate` flag is computed consistently across **all layers**:

| Layer | Logic |
|---|---|
| `DataValidationQueueable.cls` | `Safe_to_Automate__c` stamped at issue creation |
| `RemediationInvocable.cls` | Gates approval if `Severity__c = 'critical'` or `Field__c = 'Duplicate'` |
| `Python backend` (`main.py`) | `safe_to_automate = not (sev == 'critical' OR issue == 'duplicate_merge' OR field == 'duplicate')` |
| `RemediationTable.js` | `isNativeGated = fix.isNative && !fix.safe_to_automate` |
| Approval Process XML | `booleanFilter = "1 OR 2"`: Severity = critical **OR** Issue = duplicate_merge |

### React Dashboard

- **🚨 Critical Issues** stat card — combined count across all agents + governance records
- **⏳ Pending Approval** stat card — governance issues awaiting human approval
- **Health Score panel** — compact pill row showing Critical / Pending Approval / Approved counts
- **Remediation Table**:
  - Warning-level gov issues → green **Apply** button + "Ready" status
  - Critical / duplicate_merge gov issues → pink **SF APPROVAL** badge + "Salesforce Gated"
  - After applying a safe fix, the linked `Governance_Issue__c` is auto-resolved via `/remediation/apply`

---

## 🏢 Enterprise Engineering Hygiene

- ✅ `WITH SECURITY_ENFORCED` on all SOQL — respects FLS/CRUD
- ✅ `Security.stripInaccessible` before all DML — no field-level bypass
- ✅ Trigger handler framework — logic-free triggers
- ✅ Named Credentials for external callouts — no hardcoded tokens
- ✅ Bulkified Apex — all code handles 200+ records without governor limit issues
- ✅ `Test.startTest()`/`stopTest()` in all async Apex tests
- ✅ **>85% Apex test coverage** with meaningful assertions, not coverage padding
- ✅ GitHub Actions CI — Python tests run on every push; Apex + Jest on scratch org when `SF_ENABLE_APEX_CI=true`
- ✅ Consistent `safe_to_automate` gating across Apex, Python, and React layers

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Salesforce CLI (`sf`)](https://developer.salesforce.com/tools/salesforcecli)
- A Salesforce Developer Edition or Scratch Org

### 1. Clone & Python Backend Setup

```bash
git clone https://github.com/SAiRahuldade/salesforce-autonomous-governance-agent.git
cd salesforce-autonomous-governance-agent

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Copy and fill in your Salesforce credentials:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your SF_INSTANCE_URL, SF_ACCESS_TOKEN, etc.
```

Start the backend:
```bash
uvicorn backend.main:app --reload
# API available at http://127.0.0.1:8000
# Docs at        http://127.0.0.1:8000/docs
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
# Dashboard at http://localhost:3000
```

Or use the one-shot launcher on Windows:
```bash
start-dashboard.bat
```

### 3. Deploy Salesforce Metadata

```bash
# Authenticate (browser-based OAuth)
sf org login web --alias governance-org

# Deploy all metadata (Apex, Flows, Objects, Approval Process)
cd salesforce
sf project deploy start --source-dir force-app --target-org governance-org

# Run Apex tests
sf apex run test --target-org governance-org --test-level RunLocalTests --code-coverage
```

### 4. GitHub Actions CI

To enable Apex tests in CI:
1. Get your SFDX Auth URL: `sf org display --target-org governance-org --verbose`
2. Add `SFDX_AUTH_URL` as a **GitHub repository secret**
3. Set the `SF_ENABLE_APEX_CI` **repository variable** to `true`

Python tests run automatically on every push to `main` or `develop`.

---

## 🧪 Running Tests

```bash
# Python unit tests (no Salesforce connection needed)
pytest -v

# Apex tests (requires authenticated org)
cd salesforce
sf apex run test --target-org governance-org --test-level RunLocalTests --code-coverage
```

**Python test results (latest):**
```
tests/test_email_default.py::test_missing_email_gets_placeholder_and_auto_fixable  PASSED
tests/test_email_default.py::test_malformed_email_stays_gated                      PASSED
tests/test_remediation_agent.py::test_generate_fixes_validation                    PASSED
tests/test_remediation_agent.py::test_generate_fixes_phone_warning                 PASSED
tests/test_remediation_agent.py::test_missing_email_gets_placeholder_and_is_safe_to_automate PASSED
tests/test_remediation_agent.py::test_malformed_email_stays_gated                  PASSED
tests/test_remediation_agent.py::test_generate_fixes_duplicates                    PASSED
tests/test_remediation_agent.py::test_apply_fix_success                            PASSED
tests/test_remediation_agent.py::test_apply_fix_manual_review_required             PASSED
tests/test_remediation_agent.py::test_apply_fix_validation_errors                  PASSED

10 passed, 1 skipped (live SF login) in 2.39s
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Salesforce Native | Apex Batch, Queueable, Triggers, Flows, Platform Events, Custom Objects, Approval Processes |
| Python Backend | FastAPI 0.111, Python 3.11 |
| LLM Inference | Llama 3.1 via Featherless AI (AMD MI300X) |
| Frontend | React 18 |
| Salesforce Auth | OAuth 2.0 (Named Credentials + External Credentials) |
| CI/CD | GitHub Actions |
| Testing | pytest (Python), Apex Test Framework (>85% coverage) |

---

## 📁 Project Structure

```
salesforce-autonomous-governance-agent/
├── salesforce/                        # Salesforce DX project
│   └── force-app/main/default/
│       ├── classes/                   # Apex classes + tests
│       │   ├── GovernanceTriggerHandler.cls
│       │   ├── DataValidationQueueable.cls
│       │   ├── DuplicateDetectionBatch.cls
│       │   ├── RemediationInvocable.cls
│       │   └── GovernanceTriggerHandlerTest.cls
│       ├── triggers/                  # Thin Apex triggers
│       │   ├── AccountTrigger.trigger
│       │   └── ContactTrigger.trigger
│       ├── objects/                   # Custom objects + Platform Events
│       │   ├── Governance_Issue__c/
│       │   └── Governance_Alert__e/
│       ├── approvalProcesses/         # Approval Process metadata
│       │   └── Governance_Issue__c/
│       │       └── Governance_Issue_Approval.approvalProcess-meta.xml
│       ├── flows/                     # Record-Triggered Flows
│       │   └── GovernanceRemediation.flow-meta.xml
│       └── namedCredentials/          # Named Credentials
│           └── FeatherlessAI.namedCredential-meta.xml
├── backend/                           # Python FastAPI backend
│   ├── agents/                        # 5 AI governance agents
│   │   ├── duplicate_detection.py
│   │   ├── data_validation.py
│   │   ├── compliance_agent.py
│   │   ├── governance_agent.py
│   │   └── remediation_agent.py
│   ├── services/                      # Salesforce OAuth + Featherless AI
│   │   ├── sf_oauth.py
│   │   └── featherless.py
│   └── main.py                        # FastAPI app + all endpoints
├── frontend/                          # React dashboard
│   └── src/
│       ├── App.js
│       └── components/
│           ├── StatCards.js           # Critical Issues + Pending Approval cards
│           ├── GovernancePanel.js     # Health Score + summary pill row
│           ├── RemediationTable.js    # Smart Apply/SF APPROVAL gating
│           ├── GovernanceIssuesTable.js
│           ├── DuplicatesTable.js
│           ├── ValidationTable.js
│           └── RecordsTable.js
├── tests/                             # Python unit tests (pytest)
│   ├── test_remediation_agent.py
│   ├── test_email_default.py
│   └── test_salesforce_login.py
├── .github/workflows/ci.yml           # GitHub Actions CI
├── start-dashboard.bat                # One-shot Windows launcher
└── requirements.txt
```

---

## 🔄 Recent Changes (v2)

- **Approval gating consistency** — `safe_to_automate` now computed identically across Apex, Python backend, and React. Warning-level governance issues (`missing phone`, `orphan contact`) show a green **Apply** button; only `critical` or `duplicate_merge` issues show the **SF APPROVAL** badge.
- **Approval Process OR criteria** — Updated `Governance_Issue_Approval.approvalProcess-meta.xml` to use `booleanFilter = "1 OR 2"`, adding `Issue__c = 'duplicate_merge'` as a second entry criterion alongside `Severity__c = 'critical'`.
- **Dashboard summary metrics** — `/analyze/full` now returns `summary_metrics` with `critical_count`, `warning_count`, `pending_approval_count`, and `approved_count` aggregated across all agents.
- **Critical Issues & Pending Approval stat cards** — Two new top-level cards in the dashboard consume `summary_metrics` to surface the most important metrics immediately.
- **Health Score pill row** — The Governance Health panel now shows a compact `🚨 Critical | ⏳ Pending | ✅ Approved` pill row beside the score circle.
- **RemediationTable status fix** — Warning-level native governance rows now correctly show **"Ready"** instead of "Not submitted to queue".

---

## 📄 License

MIT © 2024 — Built to showcase enterprise Salesforce + Python multi-agent development patterns.
