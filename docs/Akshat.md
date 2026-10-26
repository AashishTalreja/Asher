ASHER PS-01 — HACKATHON PROJECT SUMMARY
Source: Uploaded “Pasted text.txt” only. This summarizes the proposed plan;
features, recovery figures and demo claims are not verified implementation results.

PURPOSE AND SCOPE
Team Asher (3 members) is building a Mule Account Detection & Financial Fraud
Investigation Platform for Bihar Government Cyber Hackathon 2026, PS-01.
The primary user is a police officer; a secondary bank mode is planned.
The workbench takes a 1930/NCRP complaint and bank statements through a
cross-bank money trail, account risk assessment, freeze prioritization and
case paperwork. Key differentiators are statement ingestion, a golden-hour
freeze plan and one-click legal paperwork. The source positions it against
RBI MuleHunter.AI as cross-bank complaint-to-case work versus work within a bank.

Included: bank-format statement parsing, layered trails, cash-out detection,
explainable Hindi/English scores, complaint correlation, ranked leads, notices,
BSA Section 63 certificate, case PDF, SHA-256 file hashes and audit history.
Excluded: Kafka, Neo4j, Redis, Celery, GNN, LSTM, OCR and live feeds.

ARCHITECTURE AND SHARED INTERFACES
- Backend: FastAPI, SQLAlchemy and PostgreSQL (source of truth).
- Graph: NetworkX/igraph in memory, built from transfers and account identifiers.
- Parsing: pandas, openpyxl, pdfplumber and rapidfuzz.
- ML: LightGBM, scikit-learn isotonic calibration and SHAP.
- Frontend: React, TypeScript, Vite and Cytoscape.js.
- Delivery: Docker Compose and GitHub Actions lint.
- contracts/ contains canonical Pydantic models, JSON Schema and sample data.
  Interface changes affect all three members and must be flagged.
- Parser sends list[Txn]; ML returns score, tier and reasons with English/Hindi
  text and transaction IDs; frontend uses FastAPI OpenAPI and contract mocks.

Core records: complaints; accounts uniquely identified by IFSC/account number;
normalized identifiers and account links; statements with unique file hashes,
parser version and uploader; transactions with source rows; matched transfers
with method/confidence; complaint trail hops/layers; historical risk scores;
cases and linked items; and a hash-chained audit log.
Channels: UPI, IMPS, NEFT, RTGS, AEPS, ATM, POS, CASH, CHEQUE and OTHER.

END-TO-END PIPELINE
1. Import a complaint and upload bank statements. Hash each file with SHA-256,
   retain the original read-only and register the statement.
2. Detect format using adapter scores based on file type, headers, IFSC prefix
   and bank text. Low confidence triggers manual column mapping, saved as an
   adapter. Target: two adapters (one XLSX, one CSV/text-PDF), mainly YAML config.
3. Extract XLSX/CSV via pandas/openpyxl and text PDFs via pdfplumber; merge
   wrapped narrations and remove repeated headers. Normalize Indian dates,
   number formats, Cr/Dr suffixes and debit/credit layouts. Channel-specific
   narration patterns extract references, counterparties and cash-out details.
4. Validate running balances and file parse confidence; flag failing rows.
   Officers compare source and parsed rows; edits enter the audit log.
5. Match transfers in order: exact reference (0.99 confidence), UPI handle
   (0.9), then amount/time (same amount, within 10 minutes, fuzzy name score
   at least 85; confidence 0.6–0.8). An unmatched counterparty becomes a
   “statement not yet received” placeholder with a draft bank notice.
6. Build CFCFRMS-style Layer 1, 2, 3... trails; label layering, fan-out, fan-in,
   cycles and cash-out. Flag AePS, ATM and CSP cash-out points.
7. Score accounts, correlate complaints, rank leads and prioritize freezes.
8. Generate hold/KYC/statement notices, BSA Section 63 certificate and case PDF.

DETECTION, SCORING AND RECOVERY FEATURES
Signals include dwell time, 24-hour pass-through, 7-day fan-in/fan-out, account
age, dormancy before bursts, cash-out share, round/near-threshold amounts,
night activity (23:00–05:00), complaint count/districts, shared identifiers,
PageRank, Leiden community risk and deviation from a 90-day account baseline.

Rules set score floors:
- At least 3 complaints: at least High risk.
- Dwell below 15 minutes and pass-through above 0.9: at least Medium risk.
- Account younger than 90 days with over Rs 2 lakh credited in 7 days.
- Over 50% AePS/ATM cash-out within 24 hours of credit.
- Shared phone/device with a confirmed mule.
The source does not specify numeric floors for the last three rules.

LightGBM output is isotonic-calibrated to 0–100. Final score is the maximum of
rule floor and model score. Tiers: Critical >=80; High 60–79; Medium 40–59.
Top-five SHAP reasons become Hindi/English sentences citing transaction IDs.
Behavioral signals may decay; complaint links do not. Preserve score history
and the triggering event.

Freeze priority = T_a * exp(-lambda_a * delta_t) * c_a, where T_a is victim
money remaining under proportional attribution, lambda_a is inverse median
dwell time, delta_t is expected bank-hold delay (default 2 hours), and c_a is
trail confidence. Selecting accounts shows cumulative expected recovery.

Complaint correlation extracts UPI IDs, accounts, phones and amounts,
normalizes UPI IDs, fuzzy-matches names, clusters shared entities and links
complaints to transactions by amount/time window. Leads are ranked by risk
times money at risk times complaint count, with freeze/KYC/monitor actions.

DATA AND EVALUATION
- Training/benchmark: IBM AMLworld (NeurIPS 2023), small HI subset.
- Synthetic demo: Gaya victim loses Rs 4.2 lakh to a fake trading app; four
  layers across three banks lead to AePS cash-out in Nawada. A layer-2 account
  shares a phone with six accounts named in nine complaints across five
  districts. Add about 2,000 background accounts and fake XLSX/CSV/PDF bank
  statements so the parser runs end to end.
- Report PR-AUC, precision@50 and recall on a held-out laundering pattern;
  compare rules-only, model-only and combined approaches honestly in README.


Feature freeze: Sunday 25 October 2026, 10 PM IST.
Internal submission target: Monday 26 October 2026, 6 PM IST.
Official deadline: Monday 26 October 2026, 11:59 PM IST.

HACKATHON AND DEVELOPMENT RULES
- Private repository named after the team; all members are collaborators.
- Develop on team members' own systems. Commit iteratively: final code dumps
  are disqualified. Each member commits their own work from their own account.
- Never commit real customer data, real statements or secrets; gitignore .env.
- Use small, reviewable steps, with a review/commit suggestion after each
  logical step. Use feat/<area>-<short-name> branches per issue; main is
  protected with a PR and one review.
- Keep complaint -> upload -> trail -> freeze plan -> notices/case PDF working.
- The source instructs use of BSA 2023 Section 63, BNSS 2023 and BNS terminology.
  Keep BNSS notice section numbers as {{BNSS_SECTION}} pending legal advice.
- Do not invent pitch/README statistics; mark unsupported figures
  [SOURCE NEEDED].