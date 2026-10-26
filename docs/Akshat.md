# ASHER — PS-01
## Mule Account Detection & Financial Fraud Investigation Platform

**Bihar Government Cyber Hackathon 2026**

**Team:** Asher (3 Members)  
**Problem Statement:** PS-01  
**Project Type:** Cybercrime Investigation and Financial Fraud Detection  
**Primary Users:** Police and Cybercrime Investigation Officers  
**Secondary Users:** Banking Personnel (Planned)

**Document Status:** Project Plan Summary  
**Source:** Uploaded project notes

> **Note:** This document describes the proposed system, architecture, development plan, and demonstration. Features, performance claims, and estimated recovery figures are not verified implementation results.

---

# 1. Executive Summary

Asher is a proposed financial fraud investigation platform designed to help cybercrime investigators identify mule accounts, trace fraudulent transactions across multiple banks, assess account risk, and prioritize fund-freezing actions.

The system is designed to transform a cybercrime complaint into an actionable investigation through a unified workflow:

**Complaint Registration → Bank Statement Ingestion → Transaction Matching → Money Trail Reconstruction → Mule Account Detection → Freeze Prioritization → Legal Documentation**

### Key Differentiators

1. **Cross-Bank Investigation:** Reconstructs financial trails involving accounts across different banks.
2. **Automated Statement Ingestion:** Processes bank statements in multiple formats.
3. **Golden-Hour Freeze Planning:** Prioritizes accounts based on potentially recoverable victim funds.
4. **Explainable Risk Assessment:** Provides account risk scores with reasons in Hindi and English.
5. **Automated Legal Documentation:** Generates notices, evidence certificates, and investigation reports.

The project positions itself as complementary to RBI MuleHunter.AI by focusing on cross-bank, complaint-to-case investigation workflows rather than analysis within an individual bank.

---

# 2. Problem Statement and Objectives

## 2.1 Problem

Financial fraud investigations often require officers to reconstruct the movement of stolen funds across several accounts and financial institutions.

The proposed platform addresses challenges such as:

- Bank statements arriving in different formats.
- Difficulty linking transfers across multiple accounts.
- Identifying intermediary and mule accounts.
- Recognizing cash withdrawals and transaction layering.
- Prioritizing time-sensitive freezing requests.
- Correlating related complaints across districts.
- Preparing supporting investigation documentation.

## 2.2 Project Objectives

The platform aims to:

- Standardize financial transaction data from different banks.
- Build multi-layer transaction trails.
- Identify potentially suspicious account behavior.
- Detect relationships between complaints and accounts.
- Generate explainable account risk scores.
- Rank freeze targets using estimated recoverable funds.
- Reduce manual effort in preparing investigation documents.
- Maintain evidence integrity and an auditable investigation history.

---

# 3. Scope of the Project

## 3.1 Included Features

| Module | Proposed functionality |
|---|---|
| Complaint Management | Import and correlate 1930/NCRP complaints |
| Statement Parser | Process XLSX, CSV and text-based PDF statements |
| Transaction Matching | Link debit and credit transactions across banks |
| Money Trail Visualization | Display layered fund movement and cash-out points |
| Mule Account Detection | Identify suspicious behavioral and network patterns |
| Risk Scoring | Explainable account scores with Hindi/English reasons |
| Complaint Correlation | Find shared identifiers across complaints |
| Freeze Prioritization | Rank accounts by expected recoverable funds |
| Investigation Leads | Recommend freeze, KYC request or monitoring |
| Legal Documentation | Generate notices, BSA certificate and case PDF |
| Evidence Management | SHA-256 file hashes and audit history |

## 3.2 Excluded Features

The following technologies and capabilities are intentionally outside the hackathon scope:

- Kafka
- Neo4j
- Redis
- Celery
- Graph Neural Networks (GNN)
- Long Short-Term Memory models (LSTM)
- Optical Character Recognition (OCR)
- Live transaction feeds

These exclusions are intended to keep development manageable within the hackathon timeline.

---

# 4. Technology Architecture

## 4.1 Technology Stack

| Layer | Technologies |
|---|---|
| Backend API | FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Graph Processing | NetworkX / igraph |
| Data Processing | pandas, openpyxl |
| PDF Parsing | pdfplumber |
| Fuzzy Matching | rapidfuzz |
| Machine Learning | LightGBM |
| Model Calibration | scikit-learn |
| Model Explainability | SHAP |
| Frontend | React, TypeScript, Vite |
| Graph Visualization | Cytoscape.js |
| Deployment | Docker Compose |
| CI | GitHub Actions lint |

## 4.2 Architecture Overview

The system uses PostgreSQL as the primary source of truth.

Transaction graphs are generated in memory using stored transfers and account identifiers.

### Logical Workflow

**Data Sources**
- NCRP/1930 complaints
- Bank statements
- Synthetic demonstration data

↓

**Ingestion and Normalization**
- Statement format detection
- Transaction extraction
- Data validation
- Standardized transaction records

↓

**Investigation Engine**
- Transfer matching
- Layered money trail construction
- Account and complaint correlation

↓

**Intelligence Engine**
- Rule-based detection
- Machine learning scoring
- Graph analysis
- Freeze prioritization

↓

**Investigation Dashboard**
- Account profiles
- Transaction graphs
- Risk explanations
- Investigation leads
- Freeze planning

↓

**Documentation**
- Bank notices
- BSA Section 63 certificate
- Case PDF
- Audit records

---

# 5. Repository Structure and Interfaces

## 5.1 Project Organization

| Directory | Responsibility |
|---|---|
| `contracts/` | Canonical Pydantic models, JSON Schema, sample data |
| `backend/` | APIs, database, matching, trail, freeze planning, authentication, audit |
| `parser/` | Statement adapters, normalization, balance validation |
| `generator/` | Synthetic fraud scenarios and fake bank statements |
| `ml/` | Features, rules, LightGBM, SHAP and evaluation |
| `frontend/` | React investigation dashboard |
| `reports/` | Notices, evidence certificate and case PDF |
| `docs/` | Architecture, requirements and demo script |

## 5.2 Shared Interfaces

**Parser → Backend**

Returns standardized transactions using the canonical `list[Txn]` contract.

**Backend ↔ Machine Learning**

The ML component receives features and returns:

- Risk score
- Risk tier
- English explanation
- Hindi explanation
- Supporting transaction IDs

**Backend → Frontend**

The frontend consumes FastAPI endpoints documented through OpenAPI.

Until endpoints are ready, it uses mock JSON based on shared contracts.

**Important:** Changes to `contracts/` affect all three members and must be communicated before implementation.

---

# 6. Database Design

PostgreSQL stores the core investigation records.

| Entity | Key information |
|---|---|
| Complaint | NCRP acknowledgement, victim details, fraud type, amount, date |
| Account | IFSC, account number, bank, holder, branch |
| Identifier | UPI, phone, device, IP, email, masked PAN |
| Account Identifier | Links accounts with normalized identifiers |
| Statement | File hash, bank format, period, parser version, uploader |
| Transaction | Timestamp, direction, amount, channel, references, narration |
| Transfer | Matched debit/credit transactions and confidence |
| Trail Hop | Complaint-linked transfer and trail layer |
| Risk Score | Score, tier, explanations, model version, history |
| Case / Case Item | Investigation records and associated evidence |
| Audit Log | Actor, action, timestamp and hash-chain fields |

### Supported Transaction Channels

UPI, IMPS, NEFT, RTGS, AEPS, ATM, POS, CASH, CHEQUE and OTHER.

---

# 7. Core Functional Modules

## 7.1 Complaint Intake

The system imports a cybercrime complaint and extracts relevant financial and identifying information.

**Extracted information may include:**

- Complaint reference number
- Victim details
- Fraud amount
- Reported time
- Account numbers
- UPI identifiers
- Phone numbers

The extracted information becomes the starting point for transaction tracing.

## 7.2 Bank Statement Ingestion

The statement parser converts different bank formats into standardized transactions.

### Processing Stages

**Step 1 — File Intake**

- Calculate the SHA-256 file hash.
- Preserve the original file in read-only form.
- Register statement metadata.

**Step 2 — Format Detection**

Identify the appropriate parser using:

- File extension/type
- Column headings
- IFSC prefix
- Bank identification text

If confidence is insufficient, the system falls back to manual column mapping.

**Step 3 — Data Extraction**

- XLSX/CSV: pandas and openpyxl
- Text-based PDF: pdfplumber
- Handle wrapped narrations and repeated headers.

**Step 4 — Normalization**

Standardize:

- Indian date formats
- Indian currency formatting
- Debit and credit indicators
- Transaction references
- Counterparty details
- Payment channels

**Step 5 — Validation**

Check running balances, calculate parsing confidence and flag problematic rows.

**Target Implementation:** Two statement adapters with manual mapping fallback, using YAML configuration where possible.

## 7.3 Cross-Bank Transaction Matching

The system attempts to identify corresponding debit and credit transactions.

| Matching Method | Proposed Confidence |
|---|---:|
| Exact transaction reference | 0.99 |
| UPI handle match | 0.90 |
| Amount/time/fuzzy name match | 0.60–0.80 |

For approximate matching, the plan uses equal amounts, a maximum 10-minute time difference and fuzzy-name similarity of at least 85.

When a matching bank statement is unavailable, the system creates a placeholder counterparty account and prepares a draft statement request.

## 7.4 Money Trail Reconstruction

Matched transfers are used to reconstruct the movement of victim funds.

The system follows CFCFRMS-style transaction layers:

- Layer 1: Initial recipient
- Layer 2: Subsequent transfer recipients
- Layer 3+: Further movement of funds

### Transaction Patterns

- Layering
- Fan-in
- Fan-out
- Cyclic transactions
- Cash-out

The system highlights potential cash-out through AePS, ATM and CSP channels.

---

# 8. Mule Account Detection and Risk Assessment

## 8.1 Detection Features

The proposed scoring engine examines four groups of signals.

**Transaction Behavior**
- Median fund dwell time
- 24-hour pass-through ratio
- Transaction frequency
- Round or near-threshold amounts
- Night-time activity (23:00–05:00)

**Account Behavior**
- Account age
- Dormancy followed by sudden activity
- Deviation from a 90-day account baseline
- AePS/ATM cash-out share

**Network Behavior**
- Seven-day fan-in and fan-out
- Shared identifiers
- PageRank
- Leiden community risk

**Complaint Intelligence**
- Complaint count
- Complaint districts
- Connections with flagged accounts

## 8.2 Rule-Based Detection

| Rule | Condition | Minimum Tier |
|---|---|---|
| R1 | Account linked to at least 3 complaints | High |
| R2 | Dwell below 15 minutes and pass-through above 90% | Medium |
| R3 | Account under 90 days old and over ₹2 lakh credited in 7 days | Not specified |
| R4 | Over 50% AePS/ATM cash-out within 24 hours of credit | Not specified |
| R5 | Shared phone/device with confirmed mule | Not specified |

Rules impose minimum risk scores where defined.

## 8.3 Machine Learning

The proposed ML pipeline is:

**Feature Extraction → LightGBM → Isotonic Calibration → Rule-Floor Combination → Final Risk Score**

The final risk score is the maximum of the calibrated model score and applicable rule-based floor.

### Risk Classification

| Risk Tier | Score |
|---|---|
| Critical | 80–100 |
| High | 60–79 |
| Medium | 40–59 |
| Below Medium | Below 40; label not specified |

## 8.4 Explainability

The platform proposes SHAP-based explanations for the five most influential scoring factors.

Explanations will:

- Be available in Hindi and English.
- Reference supporting transaction IDs.
- Explain why an account received its score.
- Preserve historical scores and triggering events.

Behavioral risk signals may decay over time, while complaint links remain persistent.

---

# 9. Freeze Prioritization and Recovery Planning

The freeze prioritization engine is intended to rank accounts according to expected recoverable victim funds.

## 9.1 Priority Formula

**Priority(a) = Tₐ × exp(−λₐ × Δt) × cₐ**

Where:

- **Tₐ:** Victim funds estimated to remain in the account using proportional attribution.
- **λₐ:** Inverse median fund dwell time.
- **Δt:** Expected delay before the bank applies a hold.
- **cₐ:** Confidence in the reconstructed transaction trail.

The default expected bank-hold delay is two hours.

## 9.2 Expected Output

The freeze planning dashboard is designed to display:

- Accounts recommended for freezing
- Estimated recoverable funds per account
- Prioritization order
- Cumulative expected recovery as accounts are selected

These amounts are model-based estimates, not guaranteed recoveries.

---

# 10. Complaint Correlation and Investigation Leads

## 10.1 Complaint Correlation

The system identifies potentially connected complaints using:

- Shared UPI identifiers
- Account numbers
- Phone numbers
- Fuzzy-matched names
- Transaction amounts and time windows

Complaints sharing identifiers can be grouped into related investigation clusters.

## 10.2 Investigation Leads

The proposed ranking formula is:

**Lead Priority = Risk × Money at Risk × Complaint Count**

Each lead includes a recommended action:

- Freeze account
- Request KYC
- Monitor account

---

# 11. Evidence Management and Legal Documentation

## 11.1 Automated Documents

The reporting module is intended to generate:

1. Bank hold/freezing request notices
2. KYC information requests
3. Bank statement requests
4. Bharatiya Sakshya Adhiniyam, 2023 Section 63 certificate
5. Consolidated investigation case PDF

## 11.2 Evidence Integrity

The system records SHA-256 hashes for uploaded files and maintains a hash-chained audit history.

The audit log tracks relevant actions, actors, timestamps and changes.

## 11.3 Legal Terminology

The project specifies use of current Indian legal terminology:

- Bharatiya Sakshya Adhiniyam, 2023
- Bharatiya Nagarik Suraksha Sanhita, 2023
- Bharatiya Nyaya Sanhita

BNSS section numbers in notice templates must remain as `{{BNSS_SECTION}}` until confirmed by a legal advisor.

---

# 12. Dataset and Evaluation Strategy

## 12.1 Training and Benchmark Data

**Dataset:** IBM AMLworld (NeurIPS 2023), small HI subset.

The proposed evaluation compares:

- Rule-only detection
- ML-only detection
- Combined rule and ML detection

## 12.2 Evaluation Metrics

| Metric | Purpose |
|---|---|
| PR-AUC | Assess precision-recall performance |
| Precision@50 | Evaluate accuracy of the top 50 ranked results |
| Held-out pattern recall | Assess detection of an unseen laundering pattern |

Results must be reported accurately. No evaluation scores are supplied in the source material.

## 12.3 Synthetic Demonstration Dataset

The planned synthetic scenario includes:

- Victim located in Gaya
- Fake trading application fraud
- Victim loss of ₹4.2 lakh
- Four transaction layers across three banks
- AePS cash-out in Nawada
- A layer-2 account sharing a phone with six other accounts
- Nine associated complaints across five districts
- Approximately 2,000 background accounts

Fake XLSX, CSV and PDF bank statements will support the end-to-end demonstration.

---

# 13. Team Responsibilities

## Member 1 — Project Lead / Backend

Responsible for:

- Repository setup
- Shared contracts
- Database implementation
- Transaction matching
- Money trail API
- Freeze prioritization
- Complaint correlation
- Integration
- Final submission

## Member 2 — Data Engineering / Machine Learning

Responsible for:

- Synthetic data generation
- Bank statement adapters
- Transaction normalization
- Balance validation
- Detection features
- Rule-based scoring
- LightGBM and SHAP
- Model evaluation

## Member 3 — Frontend / Reports

Responsible for:

- React application
- Dashboard navigation
- Complaint interface
- Money trail visualization
- Account risk pages
- Freeze planning interface
- Investigation leads
- Notices and case PDF
- Presentation and backup video

---

# 14. Development Schedule

| Date | Backend / Lead | Data / ML | Frontend / Reports |
|---|---|---|---|
| Fri, 23 Oct | Repository, skeleton, contracts, sample data | Demo scenario and background generator | Application shell, routes, mocks |
| Sat, 24 Oct | Database loading, matching, trail API | Statements, first adapter, balance checks | Complaint, graph and account pages |
| Sun, 25 Oct | Freeze plan, correlation, scoring integration | Second adapter, features, rules, ML, evaluation | Freeze panel, leads, timeline, notices, PDF |
| Mon, 26 Oct | Fixes, README, submission | Evaluation table and demo data | Backup video and slides |

### Key Deadlines

**Feature Freeze:** Sunday, 25 October 2026 — 10:00 PM IST

**Internal Submission Target:** Monday, 26 October 2026 — 6:00 PM IST

**Official Submission Deadline:** Monday, 26 October 2026 — 11:59 PM IST

---

# 15. Five-Minute Demonstration Plan

| Stage | Demonstration |
|---|---|
| 1. Problem | Explain the difficulty of cross-bank fraud tracing |
| 2. Complaint | Import the Gaya fraud complaint |
| 3. Ingestion | Upload statements from three banks |
| 4. Money Trail | Reconstruct the layered transaction network |
| 5. Missing Evidence | Show unmatched counterparty and draft notice |
| 6. Mule Detection | Highlight Nawada AePS cash-out and shared-phone network |
| 7. Freeze Planning | Display recommended accounts and expected recovery |
| 8. Explainability | Show Hindi/English account risk explanations |
| 9. Documentation | Generate case PDF and BSA Section 63 certificate |
| 10. Closing | Present the intended complaint-to-freeze workflow |

### Proposed Demo Claims

- Victim loss: ₹4.2 lakh
- Proposed freeze targets: Four accounts
- Illustrative estimated recovery: ₹3.1 lakh
- Intended workflow time: Under 10 minutes

These are demonstration targets or scenario figures, not verified real-world outcomes.

---

# 16. Development and Submission Guidelines

## 16.1 Repository Rules

- Maintain a private GitHub repository named after the team.
- Add all three members as collaborators.
- Each member must commit their own work using their own GitHub account.
- Make iterative commits rather than submitting one final code dump.
- Develop using team members' own systems.

## 16.2 Branching and Review

Use feature branches following:

`feat/<area>-<short-name>`

The `main` branch must remain protected.

Changes require a pull request and one review.

Development should proceed in small, reviewable steps, with a suggested commit message after each logical change.

## 16.3 Data Protection

- Never commit actual customer records.
- Never upload genuine customer bank statements.
- Never commit credentials or secrets.
- Keep `.env` excluded through `.gitignore`.
- Use synthetic data for demonstration.

## 16.4 Integration Requirement

The core demonstration workflow must remain functional throughout development:

**Complaint → Statement Upload → Money Trail → Freeze Plan → Notices / Case PDF**

## 16.5 Claims and Evidence

Do not invent project statistics or evaluation results.

Mark unsupported numerical claims with:

`[SOURCE NEEDED]`

---

# 17. Contingency Plan

If the ML implementation is not ready before the deadline, the planned fallback is to ship:

- Rule-based account risk detection
- Human-readable explanation strings
- Transaction-linked reasons
- The working complaint-to-case investigation pipeline

The fallback avoids making the full application dependent on LightGBM or SHAP completion.

---

# 18. Conclusion

Asher proposes an integrated cybercrime investigation platform that combines bank statement normalization, cross-bank transaction tracing, mule account detection, complaint correlation, recoverable-funds-based freeze prioritization, and automated legal documentation.

Its principal value proposition is to help investigators move from a fraud complaint to a structured financial investigation and prioritized bank actions within one workbench.

The project's success depends on maintaining a functional end-to-end workflow, ensuring the accuracy and explainability of transaction matching and risk scoring, and demonstrating its capabilities using synthetic data.

**Project:** Asher — PS-01  
**Event:** Bihar Government Cyber Hackathon 2026  
**Team Size:** 3 Members  
**Status:** Proposed Hackathon Implementation Plan

*End of Project Summary*