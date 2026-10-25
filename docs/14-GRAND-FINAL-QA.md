# Grand Final Q&A Preparation

15 likely questions and answers for the 27 November 2026 defence.

## Detection & Methodology

**Q1: What makes this different from a rules engine?**
> Rules alone miss three things: (a) deviations from an account's own baseline — a ₹50K transaction is normal for a shop, abnormal for a student; (b) network structure — a mule ring where each account looks clean individually; (c) complaint correlation — free-text NCRP data that no rule can parse. Our 5-layer fusion catches all three.

**Q2: Why no deep learning / GNN?**
> Three reasons: interpretability, training data, and time. XGBoost with graph features gives ~80% of a GNN's value with full feature-importance explainability. A GNN that can't explain itself is inadmissible under BSA §63. Deep learning is on our production roadmap once we have 6+ months of labeled data.

**Q3: How do you handle false positives from rules?**
> Rules generate ~40% false positives in isolation. Our fusion with baseline deviation, ML, and complaint correlation reduces that dramatically. Every alert still requires human review — we recommend, we don't block.

**Q4: What about cold-start accounts?**
> Accounts under 90 days or under 20 historical transactions fall back to a population baseline. The ML layer marks `confidence: 'low'` in that case; the officer sees this and knows to weight the score accordingly.

## Data & Privacy

**Q5: How do you handle DPDP Act 2023 compliance?**
> Data minimisation — we only store what's needed for detection. No raw PII in logs. Evidence artifacts are hashed with SHA-256. Production deployment would require a full DPIA, which is on the roadmap.

**Q6: Can a mule account holder claim defamation?**
> The system never accuses. It produces a risk score with an explanation — a recommendation, not a verdict. The officer decides. Court admissibility comes through evidence chains, not "the AI said so."

**Q7: What if a complaint is fake?**
> Confidence scoring. Each complaint-to-account link has a numeric confidence (0.0–1.0). Low-confidence links are visible separately. The system flags potential patterns — the officer investigates.

## Architecture & Scale

**Q8: How does this scale to 80 million accounts?**
> Three things change in production: (a) batch pre-scoring — nightly run scores all accounts, on-demand scoring only for alerts; (b) graph DB (Neo4j) replaces networkx in-memory; (c) Kafka replaces the batch ingestion. The core logic doesn't change.

**Q9: Why is the frontend terminal?**
> Deliberate choice. Investigators work on shared desktops with limited bandwidth; a terminal app loads instantly and runs anywhere. The core is frontend-agnostic — a web UI is a 2-day swap, not a rewrite.

**Q10: How is the score "dynamic"?**
> Event-driven updates. Every new complaint linkage, every new transaction triggers re-scoring. The score history log shows old → new → trigger. Demonstrated in the video: risk went 34 → 78 → 91 as evidence arrived.

## Legal & Evidence

**Q11: How is the PDF court-admissible?**
> SHA-256 hash chain per artifact, BSA Section 63 authentication header with timestamp and system info, tamper-evident structure. Not a substitute for legal review — but built to the format that survives it.

**Q12: Who owns the data?**
> In our production vision — the state government, on state infrastructure, per their data sovereignty policy. Our platform is designed to be deployed on-prem or MeitY-empanelled cloud.

## Alternate Dataset & Demo

**Q13: What happens if the judges' dataset has a different schema?**
> Our loader requires three CSVs with documented schemas (`accounts.csv`, `transactions.csv`, `complaints.csv`). If a judge's dataset matches, it works. If not, we have a schema-adapter interface that can be extended in ~30 minutes. We tested on three different synthetic datasets (`seed=42`, `seed=999`, `seed=1234`) with different ring sizes, account counts, and complaint volumes.

**Q14: What if the demo crashes?**
> We have a backup demo video. We also have a fallback if a specific screen fails — the other screens run independently.

## Production Roadmap

**Q15: What would it take to deploy this in Bihar?**
> Three things: (1) NCRP and CBS API access — legal + technical integration; (2) a 90-day pilot with 2 banks and 2 districts to calibrate on real data; (3) DPIA + ISMS certification. The architecture is production-shaped — nothing needs to be rebuilt. Realistic timeline: **6 months from green-light to pilot**.

---

## Member Contribution Statements

**Member A (Backend/ML):**
> "I built the detection core — rules engine, baseline deviation, XGBoost scorer, complaint correlator, money trail tracer, and the fusion layer. I also built the synthetic data generator that underpins all demos."

**Member B (Terminal UI):**
> "I built the terminal interface — all 8 screens, the Rich theme, the ASCII money-trail renderer, the network visualization, and the PDF export screen. I also drove the demo recording."

**Member C (Docs/Test/Video):**
> "I wrote the project documentation — problem definition, architecture, technical spec, and success benchmarks. I generated and tested the alternate datasets to validate generalisation. I produced the demo video, including the upload and Google Drive access verification."

---

## Delivery Tips

- **Pause before answering** — 2 seconds of thinking beats a rushed wrong answer
- **If you don't know: say so** — "That's not something we tested; here's what we'd do to find out."
- **Point to specific screens** — walk judges back to what they saw in the video
- **Never blame a teammate** — answer as a team
- **Have a 30-second elevator pitch memorised** — practice it 10 times