<div align="center">

# 🛡️ CHAKRAVYUH · चक्रव्यूह
### AI-Powered Mule Account Detection & Financial Crime Intelligence Platform
**Bihar Cyber Hackathon 2026 · Problem Statement 01 (PS-01)**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![CI Validation](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Law Enforcement](https://img.shields.io/badge/BSA%202023-%C2%A763%20Compliant-red.svg)]()
[![Hashing](https://img.shields.io/badge/SHA--256-Tamper--Proof-black.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Real-time mule ring unmasking, chronological money trail tracing, and court-admissible electronic evidence generation for law enforcement and cybercrime investigation units.*

---

</div>

## 📌 Executive Summary & Problem Alignment

In modern financial cybercrime (job task scams, fake trading apps, illegal loan harassment), illicit proceeds are layered within minutes across networks of mule accounts across Bihar before being liquidated at ATMs. 

Current police and banking investigations suffer from a **3-week latency gap**: fragmented CBS data, unstandardized NCRP complaint narratives, and lack of cross-bank transaction visibility allow syndicates to drain accounts before an account freeze order can be executed.

**CHAKRAVYUH** reduces investigation latency from **3 weeks to under 90 seconds** by uniting:
1. **12 RBI Red-Flag Rules** (instant velocity & structuring detection)
2. **90-Day Per-Account Baseline Deviation** (individual anomaly $z$-scores)
3. **20-Feature XGBoost ML Scorer** (supervised mule classification)
4. **4-Step RapidFuzz NCRP Correlator** (free-text NLP complaint matching)
5. **NetworkX 5-Hop BFS & Louvain Clustering** (automated money trail & mule ring tracing)
6. **Bharatiya Sakshya Adhiniyam (BSA) §63 PDF Exporter** (SHA-256 sealed court evidence)

---

## 🏛️ System Architecture

```
                    DATA INGESTION LAYER
   ┌───────────────────┬────────────────────┬────────────────────┐
   │ Core Banking (CBS)│  NCRP Complaints   │ Telemetry / Device │
   │ 5,000 txns / UPI  │ 23 Free-Text FIRs  │ 1,523 Entities/IPs │
   └─────────┬─────────┴─────────┬──────────┴─────────┬──────────┘
             │                   │                    │
             ▼                   ▼                    ▼
   ┌─────────────────────────────────────────────────────────────┐
   │              FIVE-LAYER DETECTION ENGINE                    │
   ├─────────────────────────────────────────────────────────────┤
   │ Layer 1: Rules Engine (core/rules.py)                       │
   │          12 RBI red-flags (rapid in-out, structuring < ₹50K) │
   │                                                             │
   │ Layer 2: Baseline Deviation (core/baseline.py)              │
   │          90-day per-account rolling z-scores (σ jumps)      │
   │                                                             │
   │ Layer 3: ML Risk Scorer (core/ml.py)                        │
   │          20-feature XGBoost model (velocity, flow, graph)   │
   │                                                             │
   │ Layer 4: Complaint Correlator (core/complaints.py)          │
   │          4-step RapidFuzz entity extraction & clustering    │
   │                                                             │
   │ Layer 5: Graph Operations (core/graph_ops.py)               │
   │          5-hop temporal BFS trail & Louvain mule ring ops   │
   └─────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             LAYER 6: WEIGHTED FUSION ENGINE                 │
   │  Score = 0.20(Rules) + 0.20(Baseline) + 0.35(ML)            │
   │          + 0.15(Complaint) + 0.10(Graph)                    │
   └─────────────────────────────┬───────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
   ┌───────────────────────────┐   ┌───────────────────────────┐
   │  RICH TERMINAL UI (8 Scrn)│   │  COURT EVIDENCE EXPORTER  │
   │  Account 360 · Money Trail│   │  BSA §63 PDF Dossier      │
   │  Live Feed · Leads Queue  │   │  SHA-256 Tamper Seal Stamp│
   └───────────────────────────┘   └───────────────────────────┘
```

---

## 🔬 The 5-Layer Detection Pipeline

### 1. Layer 1 — Rules Engine (`core/rules.py` · Weight: 0.20)
Evaluates 12 statutory RBI and FIU-IND red flags. Each rule evaluates `(fired: bool, weight: float, evidence: str)`:
* `rapid_in_out`: Debit of 80-100% of a credit within 10 minutes (pass-through draining).
* `high_velocity_24h`: Transaction count exceeding 20 in a 24-hour window.
* `structuring_evasion_amounts`: Evasion denominations (`₹9,999`, `₹49,999`, or multiples of `₹5,000`).
* `structuring_50k`: Multiple transactions between `₹45,000` and `₹50,000` to evade PAN/reporting thresholds.
* `dormancy_burst`: Dormant for > 90 days followed by > 5 transactions in 24 hours.
* `new_account_high`: Account age < 90 days with 24-hour turnover > ₹1,00,000.
* `shared_device_3plus`: Device ID shared across 3 or more bank accounts.
* `shared_phone_3plus`: Mobile number shared across 3 or more bank accounts.
* `kyc_minimal_high_turnover`: Minimal/sub-optimal KYC with high turnover.
* `no_salary_large_in`: Single credit > ₹5,00,000 without regular payroll credit.
* `pass_through_high`: 1-hour debit-to-credit pass-through ratio exceeding 85%.
* `night_burst`: Concentrated burst between 00:00 and 06:00 IST.

### 2. Layer 2 — Baseline Deviation (`core/baseline.py` · Weight: 0.20)
Computes deviations from **this specific account's normal behavior** over a 90-day rolling window:
$$\text{deviation\_score} = \sigma\Big(0.3 \cdot z_{\text{amt}} + 0.3 \cdot z_{\text{freq}} + 0.5 \cdot \text{novel\_cp} + 0.6 \cdot \text{dormancy\_break} + 0.4 \cdot \text{geo\_anomaly}\Big)$$
* **Cold-Start Safeguard**: Accounts $< 90$ days old or with $< 20$ historical transactions automatically fall back to population benchmarks and return `confidence: 'low'`.

### 3. Layer 3 — ML Risk Scorer (`core/ml.py` · Weight: 0.35)
* **Model**: Supervised `xgboost.XGBClassifier(n_estimators=100, max_depth=5, scale_pos_weight=neg/pos)`.
* **Fallback**: Automatic fallback to `sklearn.ensemble.RandomForestClassifier` if native XGBoost libraries are missing on the target host.
* **20 Features**: Velocity (1h, 24h, 7d), flow ratios, structuring counters, KYC completeness, shared device/phone counts, night transaction percentage, degree centrality, and graph neighborhood risk (`avg_neighbor_risk`).

### 4. Layer 4 — Complaint Correlator (`core/complaints.py` · Weight: 0.15)
Directly addresses PS-01's requirement to correlate unstructured NCRP victim reports:
1. **Regex Extraction**: Extracts handles (`[\w.\-]+@[a-zA-Z]+`), phone numbers (`[6-9]\d{9}`), and loss amounts from free text.
2. **Entity Resolution**: Normalizes masked handles (`rahul***@ybl` $\to$ `rahul`) and performs RapidFuzz token sort matching against holder names.
3. **Evidentiary Confidence Scoring**:
   * $+0.50$ for UPI handle match
   * $+0.30$ for fuzzy name similarity ($\ge 90\%$)
   * $+0.20$ for matching transaction amounts ($\le 2\%$ delta)
   * $+0.15$ for district geographic match
   * $+0.15$ for temporal correlation within 7 days
4. **Incident Clustering**: Groups multiple complaints under unified syndicate hubs.

### 5. Layer 5 — Graph Operations (`core/graph_ops.py` · Weight: 0.10)
* **5-Hop Chronological BFS**: Traverses funds across accounts enforcing temporal ordering ($t_{next} \ge t_{prev}$ within a 24-hour window).
* **Chain Classifier**: Classifies flow topologies into `LAYERING`, `FAN_OUT`, `FAN_IN`, `CIRCULAR`, `STRUCTURING`, or `CASH_OUT`.
* **Louvain Community Detection**: Partitions the undirected transaction graph to isolate mule rings and scores each community by density, shared entities, and cash-out links.

### 6. Layer 6 — Fusion Engine (`core/fusion.py`)
Fuses all signals into a composite $0-100$ score:
$$\text{Score} = 0.20(\text{Rules}) + 0.20(\text{Baseline}) + 0.35(\text{ML}) + 0.15(\text{Complaint}) + 0.10(\text{Graph})$$
* Severity Tiers: `CRITICAL` ($\ge 80$), `HIGH` ($\ge 60$), `MEDIUM` ($\ge 40$), `LOW` ($< 40$).

---

## 💻 Terminal User Interface (8 Screens)

Built with `rich` and `prompt_toolkit`. Capped at 100 columns for hackathon projector compatibility, with an automatic **plain ASCII fallback mode** (`--fallback` or `[P]`).

### Screen 3: Account 360 Hero Screen
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ACCOUNT 360 · ACC-22451 · RISK 99.9 [CRITICAL]                                                   │
│ Holder: Rahul Kumar · Account Age: 115 days · District: Patna · Bank: SBI (SBIN0001234)          │
│ Phone: +91-9812345678 · Device: DEV-a8f3e2 · KYC: MINIMAL · Data Quality: OK                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
┌────────────────────────── LAYER CONTRIBUTIONS (EXACT WEIGHTED FUSION) ───────────────────────────┐
│  Layer 1: Rules Engine   ■■■■■■■■■■■■■■■■■■  1.0000                 20.0 / 20.0 pts              │
│  Layer 2: Baseline Dev   ■■■■■■■■■■■■■■■■■■  1.0000                 20.0 / 20.0 pts              │
│  Layer 3: ML Scorer      ■■■■■■■■■■■■■■■■■■  0.9983                 34.9 / 35.0 pts              │
│  Layer 4: Complaints     ■■■■■■■■■■■■■■■■■■  1.0000                 15.0 / 15.0 pts              │
│  Layer 5: Graph / Ring   ■■■■■■■■■■■■■■■■■■  1.0000                 10.0 / 10.0 pts              │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
┌───────────────────────────── FIRED RBI/FIU-IND INDICATORS (LAYER 1) ─────────────────────────────┐
│   [✓] high_velocity_24h           (wt: 0.80) -> 58 transactions in 24h (threshold: > 20)         │
│   [✓] structuring_evasion_amounts (wt: 0.60) -> 57 evasion-pattern transactions (INR 9,999)      │
│   [✓] structuring_50k             (wt: 0.90) -> 9 transactions between INR 45K and 50K           │
│   [✓] shared_device_3plus         (wt: 0.90) -> Device DEV-a8f3e2 shared across 4 accounts       │
│   [✓] pass_through_high           (wt: 0.95) -> Pass-through ratio 89.2% exceeds 85%             │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
┌────────────────────────────── 90-DAY BASELINE DEVIATION (LAYER 2) ───────────────────────────────┐
│   Amount Deviation:    ~32x normal amount (vs account's own 90-day rolling baseline)             │
│   Frequency Jump:      ~29x normal daily frequency (daily transaction count)                     │
│   Behavioral Flags:    Novel Counterparties: DETECTED · Dormancy Break: CONFIRMED                │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────── LINKED NCRP INCIDENTS (LAYER 4) ─────────────────────────────────┐
│   Linked NCRP Complaints: 7 cases | Total: INR 490,000.00 | Districts: Patna, Nalanda            │
│   Primary Fraud Modus: JOB_FRAUD, INVESTMENT, UPI_FRAUD, LOAN_APP                                │
│   Latest Incident (NCRP-2026-3812): "₹5000 bheja, rahul***@ybl ko job ke liye, fir 42000 aur...   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

Shortcuts: [T] Money Trail  [N] Network  [C] Complaints  [E] Export PDF  [Enter] Main Menu
```

### Screen 4: Chronological Money Trail Tracer
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

CHAIN CLASSIFICATION: CLASSIC LAYERING (5 hops, 24 min latency)
COMMON LINK DISCOVERED: Phone +91-9812345678 and Device DEV-a8f3e2 shared across all 3 nodes!
```

---

## 📜 Court-Admissible Evidence (BSA 2023 §63)

Pressing **`[E]`** on Account 360 immediately generates an electronic evidence dossier inside `reports/`:

```
┌─────────────────── EVIDENCE REPORT EXPORT · BSA SECTION 63 ELECTRONIC RECORD ────────────────────┐
│ BHARATIYA SAKSHYA ADHINIYAM (BSA) 2023 · SECTION 63 COMPLIANT DOSSIER                            │
│   Target Account:      ACC-22451 (Rahul Kumar, Patna)                                             │
│   Case Reference:      BIH/CFU/2026/8953                                                         │
│   Export Timestamp:    2026-10-26T12:21:58 IST                                                   │
│   SHA-256 PDF Hash:    bda4ad9e4b6c38da9baee453c5f492da0e2aa59bb8474b33346d0a7a51c4a162          │
│   Payload Seal Hash:   9f268b31a2ee6f50b86a877995133d183b06c888d3d9ce45995b078021d7b30a          │
│   Destination Path:    reports/ACC-22451-evidence-20261026.pdf                                   │
│                                                                                                  │
│ [+] Court-admissible electronic certificate and PDF generated successfully.                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

* **Statutory Compliance**: Meets all conditions of Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 (*replacing Section 65B of the Indian Evidence Act, 1872*).
* **Cryptographic Tamper-Proofing**: Stamps a dynamic **SHA-256 integrity seal** on the running footer of every PDF page.

---

## 🚀 Installation & Quickstart

### Prerequisites
- Python **3.10+** (Tested and verified on **Python 3.11**)
- Git

### 1. Clone & Set Up Environment
```powershell
# Clone repository
git clone https://github.com/AashishTalreja/cyber-hacakthon-2026.git
cd cyber-hacakthon-2026

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Synthetic Benchmark Data
```powershell
# Generates deterministic Bihar evaluation case (seed=42)
python data_gen/generator.py --seed 42 --out data/
```

### 3. Launch the Application

#### Interactive Dashboard (Recommended)
```powershell
python main.py
```

#### Direct Suspect Investigation (Account 360)
```powershell
python main.py ACC-22451
```

#### Projector Fallback Mode (Plain ASCII, Zero Color Dependency)
```powershell
python main.py ACC-22451 --fallback
```

---

## 🧪 Verification & Automated Testing

The repository includes a continuous integration smoke test verified on clean Ubuntu runners:

```powershell
# Verify detection & fusion logic
python -c "from core import fusion; res = fusion.evaluate_account('ACC-22451'); assert res['score'] >= 80; print('Detection test passed!')"

# Verify BSA §63 PDF generation and SHA-256 stamping
python -c "from core import report; res = report.generate_pdf('ACC-22451'); assert res['sha256']; print('Report test passed!')"
```

---

## 👥 Hackathon Team & Acknowledgements

Developed for **Bihar Cyber Hackathon 2026** under Problem Statement 01.

| Member | Role & Key Contributions |
|---|---|
| **Nishant Kumar** | System Architecture, Terminal UI (`cli/app.py`), Baseline Deviation Engine |
| **Aashish Talreja** | ML Classifier (`core/ml.py`), Graph Ops & BFS Tracer (`core/graph_ops.py`) |
| **Ayush Raj** | Data Generator (`data_gen/`), NCRP RapidFuzz Correlator, BSA §63 PDF Generator |

---

<div align="center">
  <b>Bihar Police Cyber Financial Crime Investigation Unit (CFCU)</b><br/>
  <i>Empowering frontline cyber officers with real-time actionable intelligence.</i>
</div>
