# UI Specification

**Terminal UI built with Rich + prompt_toolkit.** Console width capped at 100 for projector compatibility. 8 screens, all reachable from the main menu or via REPL commands (`> account ACC-22451`).

## Main Menu

```
┌────────────────────────────────────────────────────────┐
│  🕵  BIHAR CYBER FRAUD INVESTIGATION PLATFORM          │
│      Mule Account Detection · Live Risk Intelligence   │
├────────────────────────────────────────────────────────┤
│  [1]  Live Alert Feed        (streaming)               │
│  [2]  Prioritized Leads      (ranked queue)            │
│  [3]  Investigate Account    (enter ID)                │
│  [4]  Money Trail Tracer     (enter ID)                │
│  [5]  Network Explorer       (enter ID)                │
│  [6]  Complaint Correlator   (search)                  │
│  [7]  District Summary       (Bihar overview)          │
│  [8]  Export Evidence Report (PDF + hash)              │
│  [Q]  Quit                                             │
└────────────────────────────────────────────────────────┘
```

## Screen 1 — Live Alert Feed

**File:** `cli/app.py` (`CLIApp.screen_live_alerts`)
**Tech:** Rich `Live` replays a pre-generated event queue with `time.sleep()`.

```
╭─ 🔴 LIVE ALERTS · simulated stream ────────────────────╮
│ 12:34:07  ⚠ CRITICAL  ACC-22451  Risk 99.9 ₹4.9L  Patna  │
│ 12:33:45  ⚠ HIGH      ACC-10033  Risk 78  ₹2.1L  Gaya   │
│ 12:33:12  ✓ RESOLVED  ACC-9981   Risk 45  ₹0.3L  Bhagal │
╰─────────────────────────────────────────────────────────╯
```

## Screen 2 — Prioritized Leads

**File:** `cli/app.py` (`CLIApp.screen_prioritized_leads`)
**Ranking:** `lead_score = risk × log(1+amount_at_risk) × (1+0.2×complaint_count)`

```
┌────┬───────────┬───────┬────────┬──────────┬──────────┐
│ #  │ Account   │ Score │ Amount │ Complaints│ District │
├────┼───────────┼───────┼────────┼──────────┼──────────┤
│ 1  │ ACC-22451 │  91   │ ₹4.9L  │ 7        │ Patna    │
│ 2  │ ACC-10033 │  87   │ ₹2.1L  │ 4        │ Gaya     │
│ 3  │ ACC-8812  │  82   │ ₹1.7L  │ 3        │ Nalanda  │
└────┴───────────┴───────┴────────┴──────────┴──────────┘
```

## Screen 3 — Account 360 ⭐

**File:** `cli/app.py` (`CLIApp.screen_account_360`)
**Most important screen.** Everything about one account at a glance.

```
╭─ ACC-22451 · Risk 99.9 · CRITICAL ──────────────────────╮
│ Holder: Rahul Kumar · Account Age: 115 days · Patna     │
│ KYC: MINIMAL · Data Quality: OK                         │
├─────────────────────────────────────────────────────────┤
│ Layer contributions (weighted fusion):                  │
│   Rules engine  ██████████████████  1.00  20.0/20 pts   │
│   Baseline      ██████████████████  1.00  20.0/20 pts   │
│   ML model      ██████████████████  1.00  34.9/35 pts   │
│   Complaints    ██████████████████  1.00  15.0/15 pts   │
│   Graph / Ring  ██████████████████  1.00  10.0/10 pts   │
├─────────────────────────────────────────────────────────┤
│ RBI/FIU-IND Indicators fired (8):                       │
│   high_velocity_24h ✓  structuring_evasion_amounts ✓    │
│   structuring_50k ✓  shared_device_3plus ✓              │
│   shared_phone_3plus ✓  kyc_minimal_high_turnover ✓     │
│   no_salary_large_in ✓  pass_through_high ✓             │
├─────────────────────────────────────────────────────────┤
│ Baseline deviation: ~32x normal amount                  │
│   Normal: 2.0 txn/day @ INR 502 · Today: 58 txns        │
│   ~29x normal daily frequency                           │
├─────────────────────────────────────────────────────────┤
│ Linked complaints: 6  (INR 4.1L total, 2 districts)     │
│ [T] Trail  [N] Network  [C] Complaints  [E] Export      │
╰─────────────────────────────────────────────────────────╯
```

## Screen 4 — Money Trail Tracer

**File:** `cli/app.py` (`CLIApp.screen_money_trail`)
ASCII Sankey + chain classification.

```
Victim (₹4.2L)
      │ 2min
      ▼
  Mule-1 (Patna) ─── 95% pass-through
      │ 8min
      ▼
  Mule-2 (Gaya) ──── 88% pass-through
      │ 4min
      ▼
  Mule-3 (Muzaffarpur)
      │ 6min
      ▼
  ATM Cash-out ₹3.8L ◀── END POINT

Chain type: CLASSIC LAYERING (4 hops, 20 min total)
Shared entity: All 3 mules share phone +91-98****4321
```

## Screen 5 — Network Explorer

**File:** `cli/app.py` (`CLIApp.screen_network_explorer`)
ASCII 2-hop tree + PNG export for complex graphs.

```
        ACC-22451 (99.9) ◀── CENTRAL
       ╱    │    ╲
    ACC-…  ACC-…  ACC-…     (all risk 70-89, same device)
     (72)   (68)   (81)
      │
    ACC-… (44) ◀── recruiter candidate

Force-graph PNG saved → reports/network-ACC-22451.png
```

## Screen 6 — Complaint Correlator

**File:** `cli/app.py` (`CLIApp.screen_complaint_correlator`)

```
Query: "rahul@ybl"  →  Matched: rahul.kumar@ybl (91%)

7 complaints · ₹8.7L · 2 districts · 3 fraud types
┌────────────┬───────────┬────────┬──────────┬─────────┐
│ NCRP-ID    │ Date      │ Amount │ Type     │ District│
├────────────┼───────────┼────────┼──────────┼─────────┤
│ NCRP-3812  │ 2026-11-02│ ₹47,000│ Job fraud│ Patna   │
│ NCRP-3901  │ 2026-11-05│ ₹99,000│ Invest.  │ Nalanda │
└────────────┴───────────┴────────┴──────────┴─────────┘
```

## Screen 7 — District Summary

**File:** `cli/app.py` (`CLIApp.screen_district_summary`)

```
Bihar Fraud Landscape
Patna        ████████████████████  ₹2.4Cr · 312 leads
Gaya         ██████████████        ₹1.7Cr · 204 leads
Muzaffarpur  ██████████            ₹1.1Cr · 156 leads
```

## Screen 8 — PDF Export

**File:** `cli/app.py` (`CLIApp.screen_export_evidence`)

```
Generating evidence report for ACC-22451...
✓ PDF generated
  Path:     reports/ACC-22451-2026-10-25.pdf
  SHA-256:  3a7f9c2e...
  Case ref: BIH/CFU/2026/0117
```

## UX Principles

- **Bilingual labels** (Hindi alongside English for key fields)
- **Width capped at 100 columns** for projector safety
- **No screen requires more than 2 keystrokes to reach**
- **Every panel shows context** — never a bare number
- **Command REPL fallback** — power users type `> leads` instead of navigating menus