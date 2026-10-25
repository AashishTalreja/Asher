# Problem Definition

## 1. What Is a Mule Account

A **mule account** is a bank account used to receive proceeds of cybercrime, break the trail through rapid transfers across 3–5 accounts (layering), and eventually cash out or convert the funds. The account holder is often unaware, coerced, or paid a small fee to lend their account.

**The core difficulty:** each individual transaction looks normal. The badness is in the *pattern* across accounts and time — not in any single event.

## 2. Why This Is Hard

| Challenge | Description |
|---|---|
| **Individually clean** | A single ₹9,999 transfer is normal. Forty of them in 3 hours is not. Batch models miss temporal patterns. |
| **Network-shaped** | Mule rings that share devices, phones, or transact in tight cycles look clean per account. |
| **Fast layering** | Median pass-through time: 6–15 minutes. Manual investigation takes weeks. |
| **Messy complaints** | NCRP text is free-form: "sent ₹5000 to rahul***@ybl" — no clean IDs. |
| **Fragmented visibility** | Each bank sees only one slice. No central view exists. |
| **Alert fatigue** | Naïve rules generate 40%+ false positives. Investigators stop trusting the system. |

## 3. What the PS Asks For (Decoded)

The Bihar Cyber Hackathon PS-01 lists six explicit requirements:

1. **Transaction Analysis** — unusual patterns, rapid transfers, layering, **deviations from normal account behaviour**
2. **Mule Account Detection** — **dynamic** risk scores, ranked accounts, **explainable indicators**
3. **Money Trail Analysis** — trace fund movements, identify **intermediary accounts**, **connected entities**, **suspicious chains**
4. **Complaint Correlation** — correlate transactions with **multiple complaints**, identify **related incidents**
5. **Graph-Based Investigation** — visualise relationships, clusters, **organised criminal networks**
6. **Investigation Dashboard** — risk alerts, **prioritised leads**, **transaction timelines**, **evidence-based reports**

## 4. Requirement Traceability

| PS Ask | Implementation |
|---|---|
| O1 — Deviations | Per-account 90-day baseline + z-score deviation |
| O2 — Dynamic scores + explainability | Event-driven score fusion + rule trace + contribution breakdown |
| O3 — Money trail + intermediaries | 5-hop BFS traversal + chain classification + intermediary scoring |
| O4 — Complaint correlation | NLP extraction + fuzzy entity resolution + incident clustering |
| O5 — Graph investigation | Louvain community detection + interactive terminal graph view |
| O6 — Dashboard + reports | 7-screen terminal UI + BSA §63-style PDF with SHA-256 |

## 5. Non-Goals

- Not a real bank CBS integration (simulated for hackathon)
- Not an auto-block system (recommendation only, human-in-the-loop)
- Not a real-time NCRP feed (batch ingestion simulated)
- Not a general-purpose fraud platform (focused on mule detection)