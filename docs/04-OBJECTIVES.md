# Objectives

## North Star

> **"Every mule account in Bihar is flagged before the money leaves the banking system — with a risk score, an explanation, and a court-admissible evidence chain attached — in under 60 seconds from the first suspicious transaction."**

## Operational Objectives (Mapped to PS)

| # | PS Ask | Objective | Measurable Target |
|---|---|---|---|
| **O1** | Transaction analysis + deviations | Detect deviations vs. per-account baseline | Precision > 0.80, Recall > 0.75 |
| **O2** | Dynamic scores + explainability | 0–100 risk score, event-driven, with rule trace | 100% of alerts explained |
| **O3** | Money trail + intermediaries | 5-hop trace + chain classification | Latency < 5s per trace |
| **O4** | Complaint correlation | Auto-link complaints to accounts via entity resolution | Precision > 0.80 |
| **O5** | Graph investigation | Louvain ring detection + terminal network view | Ring detection F1 > 0.85 |
| **O6** | Leads + timelines + reports | Prioritised leads queue + BSA §63 PDF | Report generation < 30s |

## Outcome Objectives

| Outcome | Metric | Target |
|---|---|---|
| Earlier detection | Time from first suspicious txn to alert | < 60 seconds |
| Loss reduction | ₹ at risk flagged before cash-out | > 70% of mule inflows |
| Investigator efficiency | Leads surfaced per officer per day | 20+ (vs. 2–3 today) |
| False positive reduction | vs. rules-only baseline | 40% reduction |
| Legal defensibility | Alerts with court-admissible evidence | 100% |

## Non-Goals

| Not Building | Why |
|---|---|
| Law enforcement replacement | Enforcement is a human decision |
| Real bank CBS integration | Hackathon scope; simulated |
| Predictive fraud typology for unseen types | Out of scope |
| Privacy-invasive surveillance | DPDP Act 2023 compliance |
| Cryptocurrency mule tracking | Out of Bihar's current threat |
| Auto-block accounts | Legal + operational — human-in-the-loop |