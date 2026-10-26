# Detection Pipeline

Five layers. Fused into one score. Each layer adds a different kind of signal.

## Layer 1 — Rules Engine

**File:** `core/rules.py`

12 RBI red-flag rules. Each returns `(fired, weight, evidence)`.

| Rule | Condition |
|---|---|
| `rapid_in_out` | outflow of 80-100% of an inflow within 10 min |
| `high_velocity_24h` | txn_count_24h > 20 |
| `structuring_evasion_amounts` | amount in {9999, 49999, 99999} or % 5000 == 0 |
| `structuring_50k` | count(45K ≤ amt ≤ 50K) > 3 in 24h |
| `dormancy_burst` | dormant_days > 90 and txn_count_24h > 5 |
| `new_account_high` | age_days < 90 and sum_24h > 1L |
| `shared_device_3plus` | accounts sharing device > 3 |
| `shared_phone_3plus` | accounts sharing phone > 3 |
| `kyc_minimal_high_turnover` | kyc_status in {MINIMAL, PENDING} and sum_24h > 50K |
| `no_salary_large_in` | inflow > 5L and no salary pattern |
| `pass_through_high` | pass_through_ratio_1h > 0.85 |
| `night_burst` | txn_count_1h > 10 and hour in [0..5] |

`rule_score = min(1.0, sum(weights) / MAX_WEIGHT)`

## Layer 2 — Baseline Deviation

**File:** `core/baseline.py`

Per-account 90-day rolling baseline. Detects deviations from *this account's* normal.

```python
baseline = {
    'amt_mean': ..., 'amt_std': ...,
    'txn_per_day': ..., 'freq_std': ...,
    'cp_set': set of past counterparties,
    'hour_hist': normalized histogram,
    'primary_geo': mode of past districts,
    'avg_gap_days': mean gap between txns,
}

deviation_score = sigmoid(
    0.3 * z_amt
    + 0.3 * z_freq
    + 0.5 * new_counterparty
    + 0.6 * dormancy_break
    + 0.4 * geo_anomaly
)
```

**Explanation example:** *"~32x normal amount (historical mean: INR 502), ~29x normal daily frequency (58 txns today vs 2.0 avg), new/unseen counterparties in 24h."* Z-scores above 50 are shown as a plain multiplier; smaller ones as sigma (e.g. *"4.2 sigma above normal amount"*).

**Cold-start handling:** age < 90 days or < 20 historical txns → fall back to population baseline, mark `confidence='low'`.

## Layer 3 — ML Risk Scorer

**File:** `core/ml.py`

XGBoost binary classifier. **No SHAP** — uses `feature_importances_` for global + top-3 rule contributions for per-alert explanation.

### Feature Set

```
velocity:      txn_count_1h, txn_count_24h, txn_count_7d
amount:        sum_24h, mean_24h, max_24h
flow:          in_out_ratio_24h, pass_through_ratio_1h
counterparty:  unique_cp_24h, new_cp_pct_24h
structuring:   count_below_50k, count_round_amounts
profile:       age_days, kyc_completeness, balance_var
device:        shared_device_count, shared_phone_count
time:          night_pct, activity_entropy
graph:         degree, degree_centrality, avg_neighbor_risk   ← replaces GNN
```

### Training

```python
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=5,
    scale_pos_weight=neg / pos,
    eval_metric='auc',
)
model.fit(X_train, y_train)
```

**Labels:** y=1 for 12 ring accounts + recruiters + cash-outs; y=0 for background.

### Inference

```python
{
    'score': float,  # probability
    'top_features': [(name, importance), ...],
    'confidence': 'low' if cold_start else 'normal',
}
```

**Graph features** (`avg_neighbor_risk`) give ~70% of GNN benefit in 20 minutes of feature engineering.

## Layer 4 — Complaint Correlator

**File:** `core/complaints.py`

The unique feature. Directly answers PS-01's "correlate with multiple complaints."

### 4-Step Pipeline

**Step 1 — Extract entities from free-text:**

```python
PATTERNS = {
    'upi':     r'[\w.\-]+@[a-zA-Z]+',
    'account': r'\b\d{9,18}\b',
    'phone':   r'\b[6-9]\d{9}\b',
    'amount':  r'(?:₹|rs\.?|inr)\s*([\d,]+)',
}
```

**Step 2 — Resolve entities to accounts:**

```python
candidates = []
for upi in complaint.upis:
    candidates += accounts_df[accounts_df.upi_norm == upi_norm(upi)]
for name in complaint.names:
    candidates += rapidfuzz.process.extract(
        name, accounts_df.holder_name,
        scorer=fuzz.WRatio, limit=3, score_cutoff=85,
    )
```

**Step 3 — Confidence scoring:**

```
+0.50  exact UPI match
+0.30  fuzzy name > 90
+0.20  amount within 2% of nearby txn
+0.15  complaint_date - txn_date < 7d
+0.15  district match
```

**Step 4 — Incident clustering:**

Group complaints sharing: same beneficiary account, same shared device, same UPI root.

### Output per account

```python
{
    'linked_complaints': [
        {'complaint_id': 'NCRP-2026-3812',
         'confidence': 0.91,
         'amount': 47000,
         'fraud_type': 'JOB_FRAUD',
         'district': 'Patna'},
        ...
    ],
    'complaint_count': 7,
    'complaint_sum': 870000,
    'fraud_types': ['JOB_FRAUD', 'INVESTMENT'],
    'districts': ['Patna', 'Nalanda'],
    'risk_score': 0.85,
}
```

## Layer 5 — Graph Ops

**File:** `core/graph_ops.py`

### 5a — Louvain Community Detection

```python
G = nx.DiGraph()
for t in txns:
    G.add_edge(t.from_, t.to, amount=t.amount, ts=t.ts)

communities = nx.community.louvain_communities(
    G.to_undirected(), weight='amount'
)
# Score each community:
#   density, complaint linkage, shared-entity count
```

### 5b — Money Trail Tracer

```python
def trace(origin, max_hops=5, window_hours=24):
    paths = nx.single_source_shortest_path(G, origin, cutoff=max_hops)
    paths = filter_by_time_window(paths, window_hours)
    chain_type = classify_chain(paths)
    intermediaries = score_intermediaries(paths)
    cash_outs = find_cash_out_points(paths)
```

### 5c — Chain Classifier

| Chain Type | Detection |
|---|---|
| `LAYERING` | All hops pass-through > 85%, gap < 10 min |
| `FAN_OUT` | Origin degree > 5 |
| `FAN_IN` | Terminal in-degree > 5 |
| `CIRCULAR` | Cycle detected |
| `STRUCTURING` | All amounts < reporting threshold × 0.98 |
| `CASH_OUT` | Terminal node is ATM/POS |

### 5d — Intermediary Scoring

Per hop: `pass_through_ratio_1h`, `time_to_pass`, `counterparty_novelty`.

## Layer 6 — Fusion & Scoring

**File:** `core/fusion.py`

### Weights

```python
WEIGHTS = {
    'rule':      0.20,
    'baseline':  0.20,
    'ml':        0.35,
    'complaint': 0.15,
    'graph':     0.10,
}
```

### Scoring Function

```python
def score(account_id):
    parts = {
        'rule':      rules.evaluate(account_id)['score'],
        'baseline':  baseline.deviation(account_id)['score'],
        'ml':        ml.predict(account_id)['score'],
        'complaint': complaints.score(account_id),
        'graph':     graph_ops.ring_risk(account_id),
    }
    raw = sum(WEIGHTS[k] * parts[k] for k in parts)
    final = round(raw * 100, 1)
    return {
        'score': final,
        'tier': tier_of(final),
        'contributions': parts,
        'confidence': 'low' if cold_start else 'normal',
    }
```

### Score History (event-driven)

Append-only JSON log. Every time a new complaint is linked, re-score and append:

```json
{
  "ts": "2026-10-25T14:45:00+05:30",
  "old": 34,
  "new": 78,
  "trigger": "complaint NCRP-2026-3812 linked",
  "delta": 44
}
```

This satisfies the PS's "**dynamic** risk scores" requirement without a time-decay formula.