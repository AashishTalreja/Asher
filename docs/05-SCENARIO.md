# Scenario

## Data Scenario

| Data Source | Available? | Quality | Hackathon |
|---|---|---|---|
| Bank transactions | Yes | High but fragmented | Synthesised |
| KYC records | Yes | Incomplete | Synthesised |
| NCRP complaints | Yes | Free-text, messy | Synthesised |
| Device/IP telemetry | Partial | UPI-only | Simulated |
| Cross-bank graph | No | — | Synthesised shared entities |

**Design implication:** the system must handle **fragmented, delayed, imprecise data**. Not a unified data lake.

## Three Concrete Flows

### Flow 1 — Proactive Early Detection

> A dormant student account receives ₹4.9L in 12 credits within 40 min, then starts fanning out.

1. Alert fires in < 60s — risk 84
2. Account 360 shows baseline deviation (~32x normal amount), fired RBI/FIU-IND Indicators, layer contributions
3. Money Trail shows 4-hop chain ending at ATM Muzaffarpur
4. Network Explorer reveals 3 shared devices
5. Officer creates case, exports BSA §63 PDF
6. **Total: 6 minutes** (today: 3 weeks)

### Flow 2 — Reactive Complaint Investigation

> A 62-year-old files an NCRP complaint: "sent ₹47,000 to rahul***@ybl for a job offer."

1. Complaint ingested; UPI extracted
2. Fuzzy match → `rahul.kumar@ybl` (91% confidence)
3. Cross-reference shows same account in 6 other complaints
4. Linked complaints raise the fused risk score into the CRITICAL tier
5. Network view reveals 12-account ring
6. Officer opens **network-level case**, not single-complaint case
7. **Total: 90 seconds** for pipeline

### Flow 3 — Network Disruption

> Recruiter account received ₹500 from 8 newly-opened accounts before they all began receiving large inflows.

1. Star topology detected in graph
2. Query: all accounts receiving ₹500 from this recruiter in 60 days → 34 accounts
3. 22 flagged as pre-mule
4. Bulk KYC re-verification requested
5. **Root cause addressed** (recruitment), not just symptoms

## Scale Scenario

- Bihar population: ~130M; adult accounts: ~80M
- Reported cyber frauds: ~12K/year; unreported 5–10×
- ~2% of active accounts are suspect mules → **~1.6M candidates**
- One officer reviews ~30 alerts/day
- **99.997% reduction required** — impossible without AI prioritisation

## Hackathon vs. Production

| Aspect | Hackathon | Production |
|---|---|---|
| Data | Synthetic | Bank CBS + NCRP API |
| Scale | 2K accounts / 20K txns | 80M accounts / 100M+ txns |
| Freshness | Batch seed + Rich Live replay | Kafka from CBS |
| Enforcement | Simulated webhook | Live bank API + RBI MuleHunter.AI |
| Users | Single demo user | RBAC, per-district scoping |
| Compliance | Reference DPDP/BSA §63 | Full audit + DPIA + ISMS |