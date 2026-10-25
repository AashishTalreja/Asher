"""
Test Script: Bihar Cyber Fraud Detection Fusion Engine (main.py)

Loads dataset from data/ folder, runs target accounts through the multi-layer
fusion engine, and outputs the final 0-100 risk score, tier, and breakdown.
"""

import os
import sys
import pandas as pd
from core import fusion


def load_dataset(data_dir: str = "data") -> dict:
    """Load the four core CSVs into memory."""
    accounts_path = os.path.join(data_dir, "accounts.csv")
    txns_path = os.path.join(data_dir, "transactions.csv")
    complaints_path = os.path.join(data_dir, "complaints.csv")
    entities_path = os.path.join(data_dir, "entities.csv")

    if not all(os.path.exists(p) for p in [accounts_path, txns_path, complaints_path, entities_path]):
        print(f"[*] CSVs not found in '{data_dir}'. Generating dataset using data_gen...")
        from data_gen import generator
        generator.generate_all(out_dir=data_dir, seed=42)

    print(f"[*] Loading CSV datasets from '{data_dir}'...")
    accounts_df = pd.read_csv(accounts_path)
    transactions_df = pd.read_csv(txns_path)
    complaints_df = pd.read_csv(complaints_path)
    entities_df = pd.read_csv(entities_path)

    # Convert timestamps to datetime
    transactions_df["dt"] = pd.to_datetime(transactions_df["timestamp"])

    print(f"[+] Loaded {len(accounts_df):,d} accounts, {len(transactions_df):,d} transactions, {len(complaints_df):,d} complaints, {len(entities_df):,d} entities.\n")

    return {
        "accounts_df": accounts_df,
        "transactions_df": transactions_df,
        "complaints_df": complaints_df,
        "entities_df": entities_df,
    }


def print_account_evaluation(account_id: str, ctx: dict) -> None:
    """Run an account through the fusion engine and display a detailed report."""
    accounts_df = ctx["accounts_df"]
    meta_row = accounts_df[accounts_df["account_id"] == account_id]
    holder_name = meta_row.iloc[0]["holder_name"] if len(meta_row) > 0 else "Unknown"
    district = meta_row.iloc[0]["district"] if len(meta_row) > 0 else "Unknown"
    bank = meta_row.iloc[0]["bank"] if len(meta_row) > 0 else "Unknown"

    result = fusion.score(account_id, ctx=ctx)

    score = result["score"]
    tier = result["tier"]
    contributions = result["contributions"]
    confidence = result["confidence"]
    rule_details = result["rule_details"]
    baseline_details = result["baseline_details"]

    print("=" * 65)
    print(f"  INVESTIGATION REPORT: {account_id} ({holder_name})")
    print("=" * 65)
    print(f"  Holder:      {holder_name}")
    print(f"  District:    {district} | Bank: {bank}")
    print(f"  Risk Score:  {score} / 100.0  -->  [{tier}]")
    print(f"  Confidence:  {confidence.upper()}")
    print("-" * 65)
    print("  LAYER CONTRIBUTIONS (WEIGHTED FUSION):")
    print(f"    - Layer 1 (Rules)     [20%]:  {contributions['rule']:.4f}  (Weighted: {0.20 * contributions['rule'] * 100:.1f} pts)")
    print(f"    - Layer 2 (Baseline)  [20%]:  {contributions['baseline']:.4f}  (Weighted: {0.20 * contributions['baseline'] * 100:.1f} pts)")
    print(f"    - Layer 3 (ML)        [35%]:  {contributions['ml']:.4f}  (Weighted: {0.35 * contributions['ml'] * 100:.1f} pts) [MOCK]")
    print(f"    - Layer 4 (Complaint) [15%]:  {contributions['complaint']:.4f}  (Weighted: {0.15 * contributions['complaint'] * 100:.1f} pts) [MOCK]")
    print(f"    - Layer 5 (Graph)     [10%]:  {contributions['graph']:.4f}  (Weighted: {0.10 * contributions['graph'] * 100:.1f} pts) [MOCK]")
    print("-" * 65)
    print("  FIRED RBI RED-FLAG RULES:")
    fired = rule_details.get("fired", [])
    if fired:
        for f in fired:
            print(f"    [X] {f['rule']:<20} (Weight: {f['weight']:.2f}) -> {f['evidence']}")
    else:
        print("    [None] No red-flag rules fired.")

    print("-" * 65)
    print("  BASELINE DEVIATION METRICS:")
    print(f"    - Amount Z-Score:      {baseline_details.get('z_amt', 0.0):.2f} sigma")
    print(f"    - Frequency Z-Score:   {baseline_details.get('z_freq', 0.0):.2f} sigma")
    print(f"    - New Counterparty:    {baseline_details.get('new_counterparty', False)}")
    print(f"    - Dormancy Break:      {baseline_details.get('dormancy_break', False)}")
    print(f"    - Explanation:         {baseline_details.get('explanation', '')}")
    print("-" * 65)
    print(f"  SUMMARY EXPLANATION:\n    {result['explanation']}")
    print("=" * 65 + "\n")


def main():
    target_account = sys.argv[1] if len(sys.argv) > 1 else "ACC-22451"
    ctx = load_dataset("data")

    # Evaluate target account (ACC-22451)
    print_account_evaluation(target_account, ctx)

    # Also evaluate a normal background account for contrast
    if target_account == "ACC-22451":
        print_account_evaluation("ACC-00005", ctx)


if __name__ == "__main__":
    main()
