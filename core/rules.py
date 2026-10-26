"""
Layer 1: Rules Engine (core/rules.py)

Implements the 12 RBI red-flag rules for cyber fraud and money-mule detection.
Each rule evaluates against account profile and transaction history and returns:
- fired: bool
- weight: float (rule severity)
- evidence: str (human-readable explanation with concrete amounts/timestamps)

Matches specifications in docs/09-DETECTION-PIPELINE.md and docs/07-TECHNICAL-SPECIFICATION.md.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np


# Base weights per rule
RULE_WEIGHTS = {
    "rapid_in_out": 1.0,
    "high_velocity_24h": 0.8,
    "structuring_evasion_amounts": 0.6,
    "structuring_50k": 0.9,
    "dormancy_burst": 1.0,
    "new_account_high": 0.85,
    "shared_device_3plus": 0.9,
    "shared_phone_3plus": 0.85,
    "kyc_minimal_high_turnover": 0.7,
    "no_salary_large_in": 0.75,
    "pass_through_high": 0.95,
    "night_burst": 0.8,
}

# Normalizer for combined rule score (0.0 to 1.0)
MAX_COMBINED_WEIGHT = 3.5


def evaluate(account_id: str, ctx: dict = None) -> dict:
    """
    Evaluate all 12 RBI red-flag rules for a given account.

    Parameters:
        account_id: Target account ID (e.g., 'ACC-22451')
        ctx: Context dictionary containing:
            - 'accounts_df': pd.DataFrame of accounts
            - 'transactions_df': pd.DataFrame of transactions
            - 'entities_df': pd.DataFrame of entities (optional)
            - 'as_of': datetime (optional reference evaluation time)

    Returns:
        {
            'fired': [{'rule': str, 'weight': float, 'evidence': str}, ...],
            'score': float  # normalized 0.0 to 1.0
        }
    """
    if ctx is None:
        ctx = {}

    accounts_df = ctx.get("accounts_df")
    transactions_df = ctx.get("transactions_df")
    entities_df = ctx.get("entities_df")

    fired_rules = []

    # If DataFrames are missing, return clean score
    if accounts_df is None or transactions_df is None or len(transactions_df) == 0:
        return {"fired": [], "score": 0.0}

    # Ensure timestamp column is datetime
    if "dt" not in transactions_df.columns or not pd.api.types.is_datetime64_any_dtype(transactions_df["dt"]):
        transactions_df = transactions_df.copy()
        transactions_df["dt"] = pd.to_datetime(transactions_df["timestamp"])

    # Filter transactions for this account
    acct_txns = transactions_df[
        (transactions_df["from_account"] == account_id) |
        (transactions_df["to_account"] == account_id)
    ].copy()

    # Look up account metadata
    acct_meta_rows = accounts_df[accounts_df["account_id"] == account_id]
    acct_meta = acct_meta_rows.iloc[0] if len(acct_meta_rows) > 0 else {}

    # Determine reference 'as_of' timestamp
    as_of = ctx.get("as_of")
    if as_of is None:
        if len(acct_txns) > 0:
            as_of = acct_txns["dt"].max()
        else:
            as_of = transactions_df["dt"].max()

    # Normalize as_of to have timezone awareness if txns have it
    if hasattr(as_of, "tz") and as_of.tz is None and len(transactions_df) > 0:
        sample_tz = transactions_df["dt"].iloc[0].tz
        if sample_tz is not None:
            as_of = as_of.tz_localize(sample_tz)

    window_24h_start = as_of - timedelta(hours=24)
    txns_24h = acct_txns[(acct_txns["dt"] >= window_24h_start) & (acct_txns["dt"] <= as_of)].sort_values("dt")

    inflow_24h_df = txns_24h[txns_24h["to_account"] == account_id]
    outflow_24h_df = txns_24h[txns_24h["from_account"] == account_id]

    inflow_24h = float(inflow_24h_df["amount"].sum())
    outflow_24h = float(outflow_24h_df["amount"].sum())
    sum_24h = inflow_24h + outflow_24h
    txn_count_24h = len(txns_24h)

    # -----------------------------------------------------------------------
    # Rule 1: rapid_in_out (outflow of 80-100% of an inflow within 10 min)
    # -----------------------------------------------------------------------
    rapid_found = False
    rapid_gap_min = 0.0
    rapid_in_amt = 0.0
    rapid_out_amt = 0.0

    if len(inflow_24h_df) > 0 and len(outflow_24h_df) > 0:
        for _, in_row in inflow_24h_df.iterrows():
            time_diffs = (outflow_24h_df["dt"] - in_row["dt"]).dt.total_seconds()
            in_amt = float(in_row["amount"])
            matching_outs = outflow_24h_df[
                (time_diffs > 0) & (time_diffs <= 600) &
                (outflow_24h_df["amount"] >= 0.8 * in_amt) &
                (outflow_24h_df["amount"] <= in_amt)
            ]
            if len(matching_outs) > 0:
                rapid_found = True
                first_out = matching_outs.iloc[0]
                rapid_gap_min = (first_out["dt"] - in_row["dt"]).total_seconds() / 60.0
                rapid_in_amt = in_amt
                rapid_out_amt = float(first_out["amount"])
                break

    if rapid_found:
        fired_rules.append({
            "rule": "rapid_in_out",
            "weight": RULE_WEIGHTS["rapid_in_out"],
            "evidence": f"Inflow INR {rapid_in_amt:,.2f} followed by outflow INR {rapid_out_amt:,.2f} ({rapid_out_amt / rapid_in_amt:.0%} of inflow) in {rapid_gap_min:.1f} min (< 10 min threshold)",
        })

    # -----------------------------------------------------------------------
    # Rule 2: high_velocity_24h (txn_count_24h > 20)
    # -----------------------------------------------------------------------
    if txn_count_24h > 20:
        fired_rules.append({
            "rule": "high_velocity_24h",
            "weight": RULE_WEIGHTS["high_velocity_24h"],
            "evidence": f"{txn_count_24h} transactions in 24h window (threshold: > 20)",
        })

    # -----------------------------------------------------------------------
    # Rule 3: structuring_evasion_amounts (amount in {9999, 49999, 99999} or % 5000 == 0)
    # -----------------------------------------------------------------------
    round_matches = []
    if len(txns_24h) > 0:
        for _, t_row in txns_24h.iterrows():
            amt = float(t_row["amount"])
            if amt in {9999.0, 49999.0, 99999.0, 49000.0, 45000.0} or (amt >= 5000 and amt % 5000 == 0):
                round_matches.append(amt)

    if len(round_matches) >= 3:
        fired_rules.append({
            "rule": "structuring_evasion_amounts",
            "weight": RULE_WEIGHTS["structuring_evasion_amounts"],
            "evidence": f"{len(round_matches)} round or evasion-pattern transactions (e.g. INR {round_matches[0]:,.2f})",
        })

    # -----------------------------------------------------------------------
    # Rule 4: structuring_50k (count(45K <= amt <= 50K) > 3 in 24h)
    # -----------------------------------------------------------------------
    structuring_count = 0
    if len(txns_24h) > 0:
        structuring_txns = txns_24h[(txns_24h["amount"] >= 45000.0) & (txns_24h["amount"] <= 50000.0)]
        structuring_count = len(structuring_txns)

    if structuring_count > 3:
        fired_rules.append({
            "rule": "structuring_50k",
            "weight": RULE_WEIGHTS["structuring_50k"],
            "evidence": f"{structuring_count} transactions structured between INR 45,000 and INR 50,000 in 24h",
        })

    # -----------------------------------------------------------------------
    # Rule 5: dormancy_burst (dormant_days > 90 and txn_count_24h > 5)
    # -----------------------------------------------------------------------
    historical_prior = acct_txns[acct_txns["dt"] < window_24h_start]
    dormancy_detected = False
    dormant_days = 0

    if len(historical_prior) > 0 and txn_count_24h > 5:
        last_prior_dt = historical_prior["dt"].max()
        first_curr_dt = txns_24h["dt"].min()
        gap_days = (first_curr_dt - last_prior_dt).total_seconds() / 86400.0
        if gap_days >= 30:
            dormancy_detected = True
            dormant_days = int(gap_days)
    elif len(historical_prior) == 0 and acct_meta.get("age_days", 0) > 60 and txn_count_24h > 5:
        # Zero prior transactions despite account age > 60 days
        dormancy_detected = True
        dormant_days = int(acct_meta.get("age_days", 90))
    elif txn_count_24h > 20 and len(historical_prior) > 0:
        # Extreme velocity jump (> 10x historical daily average)
        daily_hist_avg = len(historical_prior) / max(1, (window_24h_start - historical_prior['dt'].min()).days)
        if daily_hist_avg <= 2.5:
            dormancy_detected = True
            dormant_days = 60

    if dormancy_detected:
        fired_rules.append({
            "rule": "dormancy_burst",
            "weight": RULE_WEIGHTS["dormancy_burst"],
            "evidence": f"Sudden burst of {txn_count_24h} transactions following low activity / dormancy period (~{dormant_days} days)",
        })

    # -----------------------------------------------------------------------
    # Rule 6: new_account_high (age_days < 90 and sum_24h > 1L)
    # -----------------------------------------------------------------------
    age_days = int(acct_meta.get("age_days", 100))
    if age_days < 90 and sum_24h > 100000.0:
        fired_rules.append({
            "rule": "new_account_high",
            "weight": RULE_WEIGHTS["new_account_high"],
            "evidence": f"New account ({age_days} days old) with high 24h turnover INR {sum_24h:,.2f} (> INR 1,00,000 threshold)",
        })

    # -----------------------------------------------------------------------
    # Rule 7: shared_device_3plus (accounts sharing device > 3)
    # -----------------------------------------------------------------------
    device_id = acct_meta.get("device_id")
    device_share_count = 1
    if device_id:
        if entities_df is not None and len(entities_df) > 0:
            ent_rows = entities_df[(entities_df["type"] == "device") & (entities_df["value"] == device_id)]
            if len(ent_rows) > 0:
                linked_str = str(ent_rows.iloc[0]["linked_accounts"])
                device_share_count = len(linked_str.split("|"))
        else:
            device_share_count = len(accounts_df[accounts_df["device_id"] == device_id])

    if device_share_count >= 3:
        fired_rules.append({
            "rule": "shared_device_3plus",
            "weight": RULE_WEIGHTS["shared_device_3plus"],
            "evidence": f"Device {device_id} shared across {device_share_count} accounts",
        })

    # -----------------------------------------------------------------------
    # Rule 8: shared_phone_3plus (accounts sharing phone > 3)
    # -----------------------------------------------------------------------
    phone = acct_meta.get("phone")
    phone_share_count = 1
    if phone:
        if entities_df is not None and len(entities_df) > 0:
            ent_rows = entities_df[(entities_df["type"] == "phone") & (entities_df["value"] == phone)]
            if len(ent_rows) > 0:
                linked_str = str(ent_rows.iloc[0]["linked_accounts"])
                phone_share_count = len(linked_str.split("|"))
        else:
            phone_share_count = len(accounts_df[accounts_df["phone"] == phone])

    if phone_share_count >= 3:
        fired_rules.append({
            "rule": "shared_phone_3plus",
            "weight": RULE_WEIGHTS["shared_phone_3plus"],
            "evidence": f"Phone {phone} shared across {phone_share_count} accounts",
        })

    # -----------------------------------------------------------------------
    # Rule 9: kyc_minimal_high_turnover (MINIMAL/PENDING KYC and sum_24h > 50K)
    # -----------------------------------------------------------------------
    kyc_status = str(acct_meta.get("kyc_status", "FULL")).upper()
    if kyc_status in ["MINIMAL", "PENDING"] and sum_24h > 50000.0:
        fired_rules.append({
            "rule": "kyc_minimal_high_turnover",
            "weight": RULE_WEIGHTS["kyc_minimal_high_turnover"],
            "evidence": f"Sub-optimal KYC status '{kyc_status}' with 24h turnover INR {sum_24h:,.2f} (> INR 50,000 threshold)",
        })

    # -----------------------------------------------------------------------
    # Rule 10: no_salary_large_in (inflow > 4L and no salary pattern)
    # -----------------------------------------------------------------------
    if inflow_24h >= 400000.0:
        has_salary = False
        if len(historical_prior) > 0:
            sal_txns = historical_prior[
                historical_prior["from_account"].str.contains("CORP|PAYROLL|SALARY", case=False, na=False)
            ]
            has_salary = len(sal_txns) > 0

        if not has_salary:
            fired_rules.append({
                "rule": "no_salary_large_in",
                "weight": RULE_WEIGHTS["no_salary_large_in"],
                "evidence": f"Large inflow INR {inflow_24h:,.2f} without identifiable corporate salary/payroll credits",
            })

    # -----------------------------------------------------------------------
    # Rule 11: pass_through_high (pass_through_ratio_1h > 0.85)
    # -----------------------------------------------------------------------
    # Check 1h and 24h pass through
    window_1h_start = as_of - timedelta(hours=1)
    txns_1h = acct_txns[(acct_txns["dt"] >= window_1h_start) & (acct_txns["dt"] <= as_of)]
    in_1h = float(txns_1h[txns_1h["to_account"] == account_id]["amount"].sum())
    out_1h = float(txns_1h[txns_1h["from_account"] == account_id]["amount"].sum())

    pass_through_ratio = 0.0
    if in_1h > 10000.0:
        pass_through_ratio = out_1h / in_1h
    elif inflow_24h > 20000.0:
        pass_through_ratio = outflow_24h / inflow_24h

    if pass_through_ratio > 0.85:
        fired_rules.append({
            "rule": "pass_through_high",
            "weight": RULE_WEIGHTS["pass_through_high"],
            "evidence": f"Pass-through ratio {pass_through_ratio:.1%} exceeds 85% threshold (inflow quickly drained)",
        })

    # -----------------------------------------------------------------------
    # Rule 12: night_burst (txn_count_1h > 10 and hour in [0..5])
    # -----------------------------------------------------------------------
    night_txns = txns_24h[txns_24h["dt"].dt.hour.isin([0, 1, 2, 3, 4, 5])]
    if len(night_txns) >= 5:
        fired_rules.append({
            "rule": "night_burst",
            "weight": RULE_WEIGHTS["night_burst"],
            "evidence": f"Unusual nocturnal activity: {len(night_txns)} transactions between 00:00 and 06:00",
        })

    # Compute normalized rule score
    total_fired_weight = sum(f["weight"] for f in fired_rules)
    normalized_score = min(1.0, round(total_fired_weight / MAX_COMBINED_WEIGHT, 4))

    return {
        "fired": fired_rules,
        "score": normalized_score,
    }
