# Motivation

## Why This Matters

Cyber-enabled financial fraud in India has grown steadily — Bihar alone reports thousands of cases annually, with most citizens unaware of recovery procedures. Behind almost every case is a chain of **mule accounts** through which the money disappears.

## The Pain Today

1. **Investigators are overwhelmed.** A cyber cell officer may handle hundreds of cases simultaneously. Each case requires manually cross-referencing bank statements, complaint text, and transaction trails — often in Excel.
2. **The trail goes cold fast.** Mule funds are typically withdrawn within 15–60 minutes. By the time a case is filed, the money is gone and the accounts are abandoned.
3. **Fragmentation blocks visibility.** Bank A sees money leaving. Bank B sees it arriving. No one sees both ends.
4. **Complaints are disconnected.** Twenty victims may file separate complaints pointing at the same beneficiary account — but nothing links them.

## What Changes If We Ship

| Before | After |
|---|---|
| Manual Excel analysis per case | Prioritised leads queue, ranked by risk and amount |
| Weeks per money trail | 5-hop trace in under 5 seconds |
| Isolated complaints | Clustered incident view linking victims to accounts |
| No court-admissible evidence | SHA-256 hash-chained PDF with BSA §63 header |
| Zero network visibility | Louvain ring detection on the full transaction graph |

## Why AI Is Necessary

Rules alone cannot:
- Model each account's **personal baseline** (a ₹50K txn is normal for a shop, abnormal for a student)
- Detect **network structure** — rings where each account looks clean
- **Resolve entities** across messy free-text complaints
- **Prioritise** 1.6M candidate accounts down to 30 alerts a day per officer

AI is the force multiplier that turns investigator time from data collection into decision-making.

## Why Terminal

Investigators often work on shared desktops with limited bandwidth. A terminal app:
- Runs anywhere Python runs
- Requires zero training
- Loads instantly
- Handles low bandwidth gracefully
- Keeps the technical core clean for future web deployment

## Design Motivation

Every screen must answer: **"Can an investigator who has never seen this tool use it in under 60 seconds?"**

If the answer is no, the feature is not done.