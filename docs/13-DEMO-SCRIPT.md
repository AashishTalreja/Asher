# Demo Script (9:15 target)

**Video length hard limit: 8:00 to 10:00. Target 9:15.**

## Structure

| Time | Segment | Content |
|---|---|---|
| 0:00–0:45 | Problem | Mule accounts, layering, Bihar context |
| 0:45–2:00 | Architecture | 5-layer diagram + tech stack |
| 2:00–2:30 | Data generation | Fixed case + random mode |
| 2:30–7:30 | Live demo | Full workflow walkthrough |
| 7:30–8:15 | PS mapping | O1–O6 coverage |
| 8:15–9:00 | Alternate dataset + roadmap | Generalisation + production plan |
| 9:00–9:15 | Closing | Team + call to action |

## Beat-by-Beat Script

### 0:00–0:45 — Problem

> "Bihar reports thousands of cyber frauds each year. Behind almost every one is a chain of mule accounts — bank accounts used to break the money trail across 3–5 hops before cash-out. The individual transactions look normal. The badness is in the network, the timing, and the way complaints cluster around the same beneficiaries. Today, investigators piece this together in Excel over weeks. We built a platform that does it in 3 minutes."

### 0:45–2:00 — Architecture

> "Our system has 5 detection layers fused into one risk score: a rules engine for RBI red flags; a per-account baseline that flags deviations from *this* account's own normal behaviour; an XGBoost scorer enriched with graph features; a complaint correlator that resolves messy NCRP text to actual accounts; and a graph layer for money-trail tracing and mule-ring detection."

> "Everything runs in a terminal, built with Rich, on plain Python. No cloud, no external service — deployable to any police station."

### 2:00–2:30 — Data

> "For the demo, we generate a reproducible synthetic case: a 12-account mule ring across Patna, Nalanda, and Muzaffarpur, with 23 real-format NCRP complaints totalling ₹8.7 lakh. The generator is seeded, so every judge can reproduce the same case."

### 2:30–7:30 — Live Demo

**[Screen 1: Live Alerts]**
> "We're in the Live Alert Feed. A critical alert just fired — account ACC-22451, risk 91, ₹4.9 lakh."

**[Screen 3: Account 360]**
> "Opening Account 360. Notice the score trajectory: this account went from 34 to 91 in 6 hours. Contributions are visible — rules, baseline deviation, ML, complaints, graph. Rules fired include dormancy burst and structuring. The baseline deviation panel shows something powerful: normally this account does 2 transactions a day at ₹500. Today it did 47 transactions at ₹9,999. That's a 23-sigma deviation from its *own* normal."

**[Screen 6: Complaints]**
> "Linked complaints: 7, totalling ₹8.7 lakh across 2 districts. These weren't manually connected — the system resolved 'rahul***@ybl' and 'Rahul Kumar' variants to this exact account with 91% confidence."

**[Screen 4: Money Trail]**
> "Let's trace the money. [clicks T] Here's the trail — Victim → Mule-1 in Patna → Mule-2 in Gaya → Mule-3 in Muzaffarpur → ATM cash-out in 20 minutes. The system classifies this as Classic Layering. All three mules share the same phone number."

**[Screen 5: Network]**
> "The network view confirms this — four accounts share devices, three share a phone. This is a ring, not a coincidence."

**[Screen 8: PDF Export]**
> "One-click evidence export. The PDF has a BSA Section 63 header, SHA-256 hash chain, money-trail diagram, and all linked complaints. Court-ready in 8 seconds."

### 7:30–8:15 — PS Mapping

> "This covers all six PS asks: transaction analysis, dynamic risk scores with explanation, money trail with intermediaries, complaint correlation, graph-based investigation, and a prioritised investigation dashboard with evidence reports."

### 8:15–9:00 — Roadmap

> "We tested the full pipeline against a completely different random dataset — different account IDs, different ring, different complaints — and it works. For production, we'd swap the CSV loader for a Postgres + Neo4j backend, wire Kafka for streaming, and pilot with 2 banks and 2 districts in 90 days. The core is frontend-agnostic — a web UI is a 2-day swap."

### 9:00–9:15 — Closing

> "Three students, thirty-five hours, one goal: give Bihar Police a tool that turns weeks of investigation into minutes. Thank you."

## Production Rules

- **Screen recording + voiceover** — faces optional, don't waste time
- **1080p resolution**, OBS Studio
- **Do NOT edit for perfection** — raw recording is fine
- **Record at hour 26**, edit at hour 30
- **Test upload at hour 20** (30-second test, verify from incognito)

## Fallbacks

- If demo crashes during recording: **stop, restart, record again from the point of failure**
- If a screen is broken: **skip it in the script** — narration can bridge the gap
- If total recording exceeds 10 min: **cut architecture section** (least valuable)