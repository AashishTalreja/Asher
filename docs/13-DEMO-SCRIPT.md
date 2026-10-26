# Hackathon Evaluation & Live Demonstration Script

**Event:** Bihar Cyber Hackathon 2026  
**Problem Statement:** PS-01 — Mule Account Detection & Financial Crime Intelligence Platform  
**Target Suspect Account:** `ACC-22451` (Rahul Kumar, Patna)  
**Target Mule Ring:** 12 interconnected accounts across Patna, Gaya, Muzaffarpur, and Nalanda  

---

## 1. Executive Summary for Judges

This platform solves the critical bottleneck in cyber financial crime policing: **reducing investigation latency from 3 weeks to under 90 seconds** while producing court-admissible electronic evidence compliant with **Section 63 of the Bharatiya Sakshya Adhiniyam (BSA), 2023**.

```
                ┌────────────────────────────────────────────────────────┐
                │          PS-01 FIVE-LAYER FUSION DETECTION             │
                │  0.20(Rules) + 0.20(Baseline) + 0.35(ML)              │
                │         + 0.15(Complaints) + 0.10(Graph)               │
                └────────────────────────────────────────────────────────┘
```

---

## 2. Setup & Environment Warm-Up

```powershell
# 1. Activate virtual environment (if not already active)
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies (verified on Python 3.11)
pip install -r requirements.txt

# 3. Generate deterministic evaluation dataset (seed=42)
python data_gen/generator.py --seed 42 --out data/
```

**Dataset Generated:**
- `accounts.csv`: 512 bank accounts across Bihar districts (Patna, Gaya, Muzaffarpur, Nalanda)
- `transactions.csv`: 5,000 transactions with realistic UPI, IMPS, NEFT, and ATM cash-outs
- `complaints.csv`: 23 NCRP cyber fraud complaints (Job fraud, Investment scam, UPI fraud, Loan app)
- `entities.csv`: 1,523 shared phones (`+91-9812345678`), shared devices (`DEV-a8f3e2`), and IP clusters

---

## 3. End-to-End Demonstration Walkthrough (9-Minute Script)

### Step 1: Launch Interactive Command Center (Minute 0:00 - 1:00)
```powershell
python main.py
```
- Showcase the **Main Navigation Menu** (8 screens reachable in $\le 2$ keystrokes).
- Point out **Bilingual / Local Context**: Bihar districts and native INR formatting.
- Demonstrate **Projector Fallback Mode**: Press `[P]` to toggle between Rich color rendering and plain ASCII mode to safeguard against venue display glitching.

---

### Step 2: Screen 1 — Live Alert Feed Replay (Minute 1:00 - 2:30)
- In the main menu, press `[1]` or type `ALERTS`.
- **What Judges See:**
  - Real-time simulated transaction event stream.
  - Streaming event queue detects sudden surge in account `ACC-22451` receiving structured credits of ₹9,999.
  - Risk score dynamically escalates to **99.9 [CRITICAL]**.
- **Action:** Type `ACC-22451` at the quick-investigate prompt to immediately drill into Account 360.

---

### Step 3: Screen 3 — Account 360 Hero Screen (Minute 2:30 - 4:30)
- Directly inspect: `python main.py ACC-22451`
- **What Judges See:**
  1. **Account Metadata**: Rahul Kumar, 115 days old, KYC: `MINIMAL`, District: `Patna`, Device: `DEV-a8f3e2`, Phone: `+91-9812345678`.
  2. **Layer Contributions**:
     - Layer 1 (Rules Engine): **1.0000** (20.0 / 20.0 pts)
     - Layer 2 (Baseline Deviation): **1.0000** (20.0 / 20.0 pts)
     - Layer 3 (ML Risk Scorer): **0.9983** (34.9 / 35.0 pts)
     - Layer 4 (Complaint Correlator): **1.0000** (15.0 / 15.0 pts)
     - Layer 5 (Graph Ring Ops): **1.0000** (10.0 / 10.0 pts)
     - **Final Score: 99.9 / 100.0 [CRITICAL]**
  3. **Fired RBI Rules**: `rapid_in_out` (4.0 min latency), `high_velocity_24h` (58 txns), `round_amounts` (57 evasion txns), `structuring_50k` (9 txns in ₹45k-₹50k window), `shared_device_3plus` (4 accounts on DEV-a8f3e2), `pass_through_high` (89.2% ratio).
  4. **90-Day Baseline Jump**: Amount deviation **615.8σ** above historical mean (₹500); velocity spike **56.0σ** (58 txns vs 2.0 daily normal); novelty flag confirmed.
  5. **NCRP Incidents**: 7 linked cases totaling ₹4,90,000.00 with complaint narratives.

---

### Step 4: Screen 4 — Money Trail Tracer (Minute 4:30 - 5:45)
- On the Account 360 screen, press `[T]` to trace the money trail.
- **What Judges See:**
  ```
  VICTIM ACCOUNTS (INR 4.90L aggregated across 47 UPI deposits)
        │
        ▼ (latency: 4 min)
    MULE-1: ACC-22451 (Patna) ──────── 89.2% Pass-Through Ratio
        │
        ▼ (latency: 7 min, INR 2.41L IMPS)
    MULE-2: ACC-10033 (Gaya)  ──────── 97.9% Pass-Through Ratio
        │
        ▼ (latency: 5 min, INR 2.40L IMPS)
    MULE-3: ACC-99810 (Muzaffarpur) ── Pre-Cashout Staging Node
        │
        ▼ (latency: 5 min, INR 2.15L Cash Withdrawal)
    TERMINAL CASH-OUT: ATM-MZR-01 (Muzaffarpur) ◀── END POINT
  ```
- **Chain Classification:** `LAYERING` & `CASH_OUT` (5 hops, 24 minutes total).
- **Syndicate Link:** Phone `+91-9812345678` and device `DEV-a8f3e2` shared across all three hops.

---

### Step 5: Screen 6 — Complaint Correlator (Minute 5:45 - 7:00)
- From the main menu, select `[6]` or press `[C]`.
- Search query: `rahul***@ybl` (victim complaint text input).
- **What Judges See:**
  - Automated 4-step NLP pipeline:
    - Regex extraction parses masked handle `rahul***@ybl` and loss amount ₹47,000.
    - RapidFuzz token sorting matches holder `Rahul Kumar` with 100% confidence.
    - Temporal and structured multi-payment correlation matches 7 independent NCRP complaints.
    - Clusters cases under syndicate hub: **Syndicate Cluster on ACC-22451**.

---

### Step 6: Screen 8 — Court-Admissible BSA §63 PDF Export (Minute 7:00 - 8:30)
- On the Account 360 screen, press `[E]` to export evidence report.
- **What Judges See:**
  - Dossier compiled and saved directly into `reports/ACC-22451-evidence-YYYYMMDD.pdf`.
  - **Cryptographic SHA-256 Hash**: Document file hash and evidentiary payload seal printed to terminal and stamped on the running footer of every PDF page.
  - **Statutory Certificate**: Complete legal affirmation block under Section 63 of Bharatiya Sakshya Adhiniyam, 2023.

---

### Step 7: Clean Machine / Verifier Test (Minute 8:30 - 9:00)
- Demonstrate instant one-line evaluation for hackathon evaluators:
  ```powershell
  python main.py ACC-22451 --fallback
  ```
- Exits with return code 0, executing full pipeline in $< 1.5$ seconds.
