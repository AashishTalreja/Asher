"""
Layer 2: Baseline Deviation Engine (core/baseline.py)

Calculates 90-day per-account rolling baseline deviations using z-scores:
- z_amt: Transaction amount deviation from account's own historical normal.
- z_freq: Daily transaction frequency deviation.
- new_counterparty: Detection of novel/unseen counterparties.
- dormancy_break: Sudden burst following dormancy or low activity.
- geo_anomaly: Transactions outside historical district profile.

Handles cold-start accounts (< 90 days or < 20 historical txns) by falling
back to a population baseline and marking confidence='low'.

Matches specifications in docs/09-DETECTION-PIPELINE.md and docs/07-TECHNICAL-SPECIFICATION.md.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def _sigmoid(x: float) -> float:
    """Stable sigmoid function."""
    return float(1.0 / (1.0 + np.exp(-np.clip(x, -50.0, 50.0))))


def compute_population_baseline(transactions_df: pd.DataFrame) -> dict:
    """Compute default baseline across population for cold-start accounts."""
    if transactions_df is None or len(transactions_df) == 0:
        return {
            "amt_mean": 1500.0,
            "amt_std": 2500.0,
            "freq_mean": 2.0,
            "freq_std": 2.0,
        }

    amt_mean = float(transactions_df["amount"].mean())
    amt_std = float(transactions_df["amount"].std())
    if np.isnan(amt_std) or amt_std < 1.0:
        amt_std = 1500.0

    return {
        "amt_mean": amt_mean,
        "amt_std": amt_std,
        "freq_mean": 2.0,
        "freq_std": 2.0,
    }


def deviation(account_id: str, as_of: datetime = None, ctx: dict = None) -> dict:
    """
    Calculate baseline deviation score and metrics for an account.

    Parameters:
        account_id: Target account ID (e.g., 'ACC-22451')
        as_of: Evaluation reference timestamp
        ctx: Context dictionary containing:
            - 'accounts_df': pd.DataFrame
            - 'transactions_df': pd.DataFrame

    Returns:
        {
            'score': float,             # 0.0 to 1.0
            'z_amt': float,             # amount z-score (e.g. 23.0)
            'z_freq': float,            # frequency z-score
            'new_counterparty': bool,   # novel counterparties detected
            'dormancy_break': bool,     # dormancy break detected
            'confidence': 'normal' | 'low',
            'explanation': str
        }
    """
    if ctx is None:
        ctx = {}

    accounts_df = ctx.get("accounts_df")
    transactions_df = ctx.get("transactions_df")

    if accounts_df is None or transactions_df is None or len(transactions_df) == 0:
        return {
            "score": 0.0,
            "z_amt": 0.0,
            "z_freq": 0.0,
            "new_counterparty": False,
            "dormancy_break": False,
            "confidence": "low",
            "explanation": "Insufficient transaction data for baseline calculation.",
        }

    # Ensure timestamp column is datetime
    if "dt" not in transactions_df.columns or not pd.api.types.is_datetime64_any_dtype(transactions_df["dt"]):
        transactions_df = transactions_df.copy()
        transactions_df["dt"] = pd.to_datetime(transactions_df["timestamp"])

    acct_txns = transactions_df[
        (transactions_df["from_account"] == account_id) |
        (transactions_df["to_account"] == account_id)
    ].copy()

    # Look up account metadata
    acct_meta_rows = accounts_df[accounts_df["account_id"] == account_id]
    acct_meta = acct_meta_rows.iloc[0] if len(acct_meta_rows) > 0 else {}
    age_days = int(acct_meta.get("age_days", 100))

    # Reference evaluation time
    if as_of is None:
        as_of = ctx.get("as_of")
        if as_of is None:
            if len(acct_txns) > 0:
                as_of = acct_txns["dt"].max()
            else:
                as_of = transactions_df["dt"].max()

    # Normalize timezone
    if hasattr(as_of, "tz") and as_of.tz is None and len(transactions_df) > 0:
        sample_tz = transactions_df["dt"].iloc[0].tz
        if sample_tz is not None:
            as_of = as_of.tz_localize(sample_tz)

    window_24h_start = as_of - timedelta(hours=24)
    baseline_start = as_of - timedelta(days=90)

    # Historical transactions: [as_of - 90d, as_of - 24h]
    hist_txns = acct_txns[(acct_txns["dt"] >= baseline_start) & (acct_txns["dt"] < window_24h_start)]

    # Current window transactions: [as_of - 24h, as_of]
    curr_txns = acct_txns[(acct_txns["dt"] >= window_24h_start) & (acct_txns["dt"] <= as_of)]

    # Cold-start check (< 90 days old or < 20 historical transactions)
    is_cold_start = (age_days < 90) or (len(hist_txns) < 20)
    confidence = "low" if is_cold_start else "normal"

    if is_cold_start and len(hist_txns) < 5:
        # Fall back to population baseline
        pop_base = compute_population_baseline(transactions_df)
        amt_mean = pop_base["amt_mean"]
        amt_std = pop_base["amt_std"]
        freq_mean = pop_base["freq_mean"]
        freq_std = pop_base["freq_std"]
        past_cp = set()
        past_districts = set()
    else:
        amt_mean = float(hist_txns["amount"].mean())
        amt_std = float(hist_txns["amount"].std())
        if np.isnan(amt_std) or amt_std < 1.0:
            amt_std = max(25.0, amt_mean * 0.1)

        # Historical daily frequency
        hist_days = hist_txns["dt"].dt.date.nunique()
        freq_mean = len(hist_txns) / max(1, hist_days)
        daily_counts = hist_txns.groupby(hist_txns["dt"].dt.date).size()
        freq_std = float(daily_counts.std()) if len(daily_counts) > 1 else 1.0
        if np.isnan(freq_std) or freq_std < 0.5:
            freq_std = 1.0

        past_cp = set(hist_txns["from_account"]).union(set(hist_txns["to_account"])) - {account_id}
        past_districts = set(hist_txns["district"].dropna().unique())

    # Current evaluation metrics
    if len(curr_txns) > 0:
        curr_amt_mean = float(curr_txns["amount"].mean())
        curr_freq = len(curr_txns)

        curr_cp = set(curr_txns["from_account"]).union(set(curr_txns["to_account"])) - {account_id}
        new_cp = len(curr_cp - past_cp) > 0 if len(past_cp) > 0 else True

        curr_districts = set(curr_txns["district"].dropna().unique())
        geo_anomaly = len(curr_districts - past_districts) > 0 if len(past_districts) > 0 else False

        # Z-scores
        z_amt = max(0.0, (curr_amt_mean - amt_mean) / amt_std)
        z_freq = max(0.0, (curr_freq - freq_mean) / freq_std)

        # Dormancy break check: low historical daily volume (< 3 txns/day) and curr_freq > 15
        dormancy_break = (freq_mean <= 3.0 and curr_freq >= 15) or (len(hist_txns) > 0 and len(curr_txns) > 10 and (curr_txns['dt'].min() - hist_txns['dt'].max()).days >= 15)
    else:
        z_amt = 0.0
        z_freq = 0.0
        new_cp = False
        dormancy_break = False
        geo_anomaly = False

    # Detection formula from docs/09-DETECTION-PIPELINE.md:
    # deviation_score = sigmoid(0.3 * z_amt + 0.3 * z_freq + 0.5 * new_cp + 0.6 * dormancy_break + 0.4 * geo_anomaly)
    # Calibrated with center offset so normal accounts (z=0) yield ~0 score, while strong deviations yield ~1.0.
    raw_signal = (
        0.3 * min(z_amt, 30.0) +
        0.3 * min(z_freq, 30.0) +
        0.5 * (1.0 if new_cp else 0.0) +
        0.6 * (1.0 if dormancy_break else 0.0) +
        0.4 * (1.0 if geo_anomaly else 0.0)
    )

    if raw_signal <= 0.3:
        deviation_score = 0.0
    else:
        # Sigmoid centered around 2.5: 23-sigma gives > 0.95, 0-sigma gives 0.0
        deviation_score = round(float(_sigmoid(raw_signal - 2.5)), 4)

    # Build human-readable explanation
    explanations = []
    if z_amt >= 3.0:
        explanations.append(f"{z_amt:.1f} sigma above normal amount (historical mean: INR {amt_mean:,.0f})")
    if z_freq >= 3.0:
        explanations.append(f"{z_freq:.1f} sigma above normal daily frequency ({len(curr_txns)} txns today vs {freq_mean:.1f} avg)")
    if new_cp:
        explanations.append("new/unseen counterparties in 24h")
    if dormancy_break:
        explanations.append("dormancy break with sudden activity burst")
    if geo_anomaly:
        explanations.append("unusual transaction geography")

    explanation_str = ", ".join(explanations) if explanations else "Normal activity consistent with 90-day baseline."

    return {
        "score": deviation_score,
        "z_amt": round(float(z_amt), 2),
        "z_freq": round(float(z_freq), 2),
        "new_counterparty": bool(new_cp),
        "dormancy_break": bool(dormancy_break),
        "confidence": confidence,
        "explanation": explanation_str,
    }
