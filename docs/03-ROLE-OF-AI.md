# Role of AI

## Summary

> AI is the **force multiplier for scarce investigator hours**. It does what humans cannot do at scale (perception, connection, prioritisation, articulation) and leaves judgement, action, and accountability to humans.

## The Four AI Roles

| Role | What AI Does | What It Replaces |
|---|---|---|
| **Perception** | Detects deviations across high-dimensional, temporal, and relational data | Manual transaction scanning |
| **Connection** | Links complaints ↔ accounts ↔ devices ↔ network clusters | Cross-referencing Excel sheets |
| **Prioritisation** | Ranks thousands of candidates into a shortlist respecting officer capacity | Chronological backlog |
| **Articulation** | Generates human-readable, court-admissible explanations | Handwritten notes |

## What AI Does Not Do

| Non-Role | Reason |
|---|---|
| Does not block accounts | Enforcement requires legal authorisation |
| Does not accuse individuals | DPDP Act 2023; risk flag ≠ verdict |
| Does not replace investigators | Human-in-the-loop for accountability |
| Does not act on unlabeled data alone | Unsupervised signals need review |
| Does not hide its reasoning | BSA §63 requires auditable electronic evidence |

## Why Rules Alone Are Not Enough

| Problem | Why Rules Fail | What AI Does |
|---|---|---|
| Criminals adapt to published thresholds | Rules are static | ML learns from data |
| Rings look clean per-account | No rule fires | Graph ML scores by neighbourhood |
| Deviations are per-account | Rules are global | Baseline deviation is per-account |
| Complaints are free-text | Rules cannot parse | NLP + fuzzy matching |
| Volume exceeds capacity | Rules generate 40%+ FPs | Fusion reduces FPs while maintaining recall |

## Three Bands of AI Action
BAND 1: DETECT BAND 2: CONNECT BAND 3: DEFEND
───────────── ────────────── ──────────────
Rules Entity Resolution Rule trace
Baseline deviation Complaint clustering Score history log
XGBoost risk Money trail traversal SHA-256 evidence chain
Louvain ring detect Intermediary scoring BSA §63 PDF report

text

Each band answers: **What's happening?** · **Who's involved?** · **How do I prove it?**

## One-Line Pitch

> *"AI gives every investigator a team of ten analysts working 24/7 — it sees what they cannot see, connects what they cannot connect, and hands them evidence they can defend in court."*