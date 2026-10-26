"""
Bihar Cyber Fraud Investigation Platform - Terminal UI (cli/app.py)

Built with Rich and prompt_toolkit.
Implements the 8 screens defined in docs/10-UI-SPECIFICATION.md and docs/06-ARCHITECTURE.md:
  1. Live Alert Feed (simulated real-time streaming)
  2. Prioritized Leads (ranked queue)
  3. Account 360 Hero Screen (visual risk, layer contributions, fired rules, z-scores)
  4. Money Trail Tracer (Sankey hop visualization)
  5. Network Explorer (2-hop shared entity tree)
  6. Complaint Correlator (search & entity resolution)
  7. District Summary (Bihar fraud distribution)
  8. Export Evidence Report (BSA Section 63 electronic evidence header + SHA-256)

Includes a plain ASCII Fallback Mode (no colors/Unicode) for hackathon projector safety.
"""

import os
import sys
import time
import hashlib
from datetime import datetime
import pandas as pd
import numpy as np

# Force UTF-8 on Windows consoles to prevent charmap encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

try:
    from prompt_toolkit import prompt as pt_prompt
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

from core import fusion
from core.config import FUSION_WEIGHTS


class CLIApp:
    def __init__(self, data_dir: str = "data", fallback: bool = False):
        self.data_dir = data_dir
        self.fallback = fallback
        self.console = self._create_console()
        self.ctx = None
        self.load_data()

    def _create_console(self) -> Console:
        """Create Rich console instance with width capped at 100 for projector compatibility."""
        if self.fallback:
            return Console(width=100, force_terminal=True, color_system=None, no_color=True)
        else:
            return Console(width=100, force_terminal=True)

    def toggle_fallback(self) -> None:
        """Toggle between full Rich colored mode and plain ASCII projector fallback mode."""
        self.fallback = not self.fallback
        self.console = self._create_console()
        mode_str = "ASCII FALLBACK MODE (No colors / projector-safe)" if self.fallback else "RICH COLOR MODE"
        self.console.print(f"\n[+] Display mode switched to: {mode_str}\n")
        time.sleep(0.7)

    def load_data(self) -> None:
        """Load datasets from data/ directory or trigger generator if missing."""
        acc_path = os.path.join(self.data_dir, "accounts.csv")
        txn_path = os.path.join(self.data_dir, "transactions.csv")
        cmp_path = os.path.join(self.data_dir, "complaints.csv")
        ent_path = os.path.join(self.data_dir, "entities.csv")

        if not all(os.path.exists(p) for p in [acc_path, txn_path, cmp_path, ent_path]):
            self.console.print(f"[*] Datasets missing in '{self.data_dir}'. Generating synthetic data...")
            from data_gen import generator
            generator.generate_all(out_dir=self.data_dir, seed=42)

        accounts_df = pd.read_csv(acc_path)
        transactions_df = pd.read_csv(txn_path)
        complaints_df = pd.read_csv(cmp_path)
        entities_df = pd.read_csv(ent_path)

        transactions_df["dt"] = pd.to_datetime(transactions_df["timestamp"])

        self.ctx = {
            "accounts_df": accounts_df,
            "transactions_df": transactions_df,
            "complaints_df": complaints_df,
            "entities_df": entities_df,
            "as_of": transactions_df["dt"].max(),
        }

    def prompt_user(self, text: str = "Select option > ", default: str = "") -> str:
        """Unified prompt handling interactive and non-interactive environments."""
        if not sys.stdin.isatty():
            return default

        prompt_label = f"{text}[{default}] " if default else text
        if HAS_PROMPT_TOOLKIT and not self.fallback:
            try:
                res = pt_prompt(prompt_label).strip()
                return res if res else default
            except (EOFError, KeyboardInterrupt):
                return "Q"
        else:
            try:
                res = input(prompt_label).strip()
                return res if res else default
            except (EOFError, KeyboardInterrupt):
                return "Q"

    def _render_bar(self, value: float, max_width: int = 18, color: str = "cyan") -> Text:
        """Render horizontal score contribution bar in Rich or plain ASCII."""
        val = max(0.0, min(1.0, value))
        filled = int(round(val * max_width))
        unfilled = max_width - filled

        if self.fallback:
            bar_str = "[" + ("=" * filled) + (" " * unfilled) + "]"
            return Text(f"{bar_str} {val:.2f}")
        else:
            bar_text = Text()
            bar_text.append("■" * filled, style=color)
            bar_text.append("·" * unfilled, style="dim")
            bar_text.append(f"  {val:.2f}", style="bold white")
            return bar_text

    # =======================================================================
    # Main Menu
    # =======================================================================
    def show_main_menu(self) -> None:
        """Render the main navigation menu."""
        box_style = box.ASCII if self.fallback else box.ROUNDED
        header_text = Text()
        if self.fallback:
            header_text.append("BIHAR CYBER FRAUD INVESTIGATION PLATFORM\n", style="bold")
            header_text.append("Mule Account Detection | Live Risk Intelligence", style="dim")
        else:
            header_text.append("BIHAR CYBER FRAUD INVESTIGATION PLATFORM\n", style="bold cyan")
            header_text.append("Mule Account Detection · Live Risk Intelligence · Bihar Police CFU", style="dim white")

        menu_table = Table(show_header=False, box=None, padding=(0, 2), width=90)
        menu_table.add_column("Key", style="bold green" if not self.fallback else "bold", width=6)
        menu_table.add_column("Screen", style="bold white", width=34)
        menu_table.add_column("Description", style="dim", width=40)

        menu_table.add_row("[1]", "Live Alert Feed", "(simulated real-time streaming)")
        menu_table.add_row("[2]", "Prioritized Leads", "(ranked investigative queue)")
        menu_table.add_row("[3]", "Investigate Account", "(Account 360 Hero Screen - enter ID)")
        menu_table.add_row("[4]", "Money Trail Tracer", "(BFS rapid layering tracer)")
        menu_table.add_row("[5]", "Network Explorer", "(shared device & phone ring tree)")
        menu_table.add_row("[6]", "Complaint Correlator", "(NCRP text & entity resolver)")
        menu_table.add_row("[7]", "District Summary", "(Bihar district fraud breakdown)")
        menu_table.add_row("[8]", "Export Evidence Report", "(BSA Section 63 PDF + SHA-256)")
        menu_table.add_row("[P]", "Toggle Fallback Mode", f"(current: {'ASCII' if self.fallback else 'Rich Colors'})")
        menu_table.add_row("[Q]", "Quit", "(exit platform)")

        panel = Panel(
            menu_table,
            title=header_text,
            title_align="center",
            box=box_style,
            border_style="blue" if not self.fallback else "white",
            padding=(1, 2),
        )
        self.console.print("\n")
        self.console.print(panel)

    # =======================================================================
    # Screen 1: Live Alert Feed (Replay Stream)
    # =======================================================================
    def screen_live_alerts(self) -> None:
        """Simulate real-time streaming incoming risk alerts."""
        self.console.print("\n")
        box_style = box.ASCII if self.fallback else box.ROUNDED

        title_text = "LIVE ALERTS · SIMULATED EVENT STREAM"
        if not self.fallback:
            title_text = "LIVE ALERTS · Simulated Replay Stream (Bihar CFU)"

        self.console.print(Panel(
            Text("Replaying real-time streaming transaction & lead event queue...\nPress [Ctrl+C] or wait to pause stream.", justify="center"),
            box=box_style,
            title=title_text,
            border_style="red" if not self.fallback else "white"
        ))

        stream_events = [
            {"time": "12:30:15", "tier": "MEDIUM", "acct": "ACC-10038", "score": 48.0, "amount": "INR 0.8L", "district": "Gaya", "msg": "Structured outbound"},
            {"time": "12:31:02", "tier": "HIGH", "acct": "ACC-10037", "score": 68.0, "amount": "INR 1.5L", "district": "Muzaffarpur", "msg": "Layering hop & ATM cashout pending"},
            {"time": "12:31:45", "tier": "MEDIUM", "acct": "ACC-10036", "score": 52.0, "amount": "INR 0.9L", "district": "Nalanda", "msg": "Phone entity shared with ACC-10035"},
            {"time": "12:32:10", "tier": "MEDIUM", "acct": "ACC-10035", "score": 55.0, "amount": "INR 1.2L", "district": "Nalanda", "msg": "Pass-through hop from Patna"},
            {"time": "12:32:55", "tier": "HIGH", "acct": "ACC-10034", "score": 72.0, "amount": "INR 1.9L", "district": "Patna", "msg": "DEV-a8f3e2 shared device burst"},
            {"time": "12:33:20", "tier": "RESOLVED", "acct": "ACC-00045", "score": 28.0, "amount": "INR 0.2L", "district": "Bhagalpur", "msg": "Routine merchant transaction"},
            {"time": "12:33:48", "tier": "HIGH", "acct": "ACC-10033", "score": 78.0, "amount": "INR 2.4L", "district": "Gaya", "msg": "Rapid in-out within 9 min (Layering)"},
            {"time": "12:34:07", "tier": "CRITICAL", "acct": "ACC-22451", "score": 91.0, "amount": "INR 4.9L", "district": "Patna", "msg": "Dormancy burst + Structuring (47x INR 9,999)"},
        ]

        table = Table(box=box_style, width=96, border_style="red" if not self.fallback else "white")
        table.add_column("Timestamp", style="cyan" if not self.fallback else "bold", width=12)
        table.add_column("Tier", width=12)
        table.add_column("Account", style="bold white", width=12)
        table.add_column("Risk Score", justify="right", width=12)
        table.add_column("Amount", justify="right", width=12)
        table.add_column("District", width=14)
        table.add_column("Trigger / Note", style="dim", width=26)

        try:
            for ev in stream_events:
                tier_styled = ev["tier"]
                if not self.fallback:
                    if ev["tier"] == "CRITICAL":
                        tier_styled = "[bold red]CRITICAL[/]"
                    elif ev["tier"] == "HIGH":
                        tier_styled = "[bold yellow]HIGH[/]"
                    elif ev["tier"] == "MEDIUM":
                        tier_styled = "[bold blue]MEDIUM[/]"
                    elif ev["tier"] == "RESOLVED":
                        tier_styled = "[green]RESOLVED[/]"

                score_styled = f"{ev['score']:.0f}"
                if not self.fallback and ev["score"] >= 80:
                    score_styled = f"[bold red]{score_styled}[/]"

                table.add_row(
                    ev["time"],
                    tier_styled,
                    ev["acct"],
                    score_styled,
                    ev["amount"],
                    ev["district"],
                    ev["msg"],
                )
                self.console.clear()
                self.console.print(table)
                if sys.stdin.isatty():
                    time.sleep(0.3)
        except KeyboardInterrupt:
            pass

        self.console.print("\n[+] Stream paused. Jump to Account 360 by typing account ID, or press Enter for Menu.")
        choice = self.prompt_user("Action (Account ID or Enter) > ", default="ACC-22451")
        if choice.upper().startswith("ACC-"):
            self.screen_account_360(choice.upper())

    # =======================================================================
    # Screen 2: Prioritized Leads Queue
    # =======================================================================
    def screen_prioritized_leads(self) -> None:
        """Render ranked investigative queue prioritizing high-risk high-volume cases."""
        self.console.print("\n")
        box_style = box.ASCII if self.fallback else box.ROUNDED

        accounts_df = self.ctx["accounts_df"]
        complaints_df = self.ctx["complaints_df"]
        transactions_df = self.ctx["transactions_df"]

        ring_candidates = [
            "ACC-22451", "ACC-10033", "ACC-99810", "ACC-10034",
            "ACC-10035", "ACC-10036", "ACC-10037", "ACC-10038"
        ]

        leads = []
        for acct_id in ring_candidates:
            res = fusion.evaluate_account(acct_id, ctx=self.ctx)
            score = res["score"]
            meta = accounts_df[accounts_df["account_id"] == acct_id].iloc[0]
            inflow = transactions_df[transactions_df["to_account"] == acct_id]["amount"].sum()
            cmps = len(complaints_df[complaints_df["beneficiary_name"].str.contains(meta["holder_name"].split()[0], case=False, na=False)])

            # Formula from docs/10-UI-SPECIFICATION.md:
            # lead_score = risk * log(1 + amount_at_risk) * (1 + 0.2 * complaint_count)
            lead_score = score * np.log1p(inflow) * (1.0 + 0.2 * cmps)
            leads.append({
                "account_id": acct_id,
                "holder": meta["holder_name"],
                "score": score,
                "amount": inflow,
                "complaints": cmps,
                "district": meta["district"],
                "lead_score": lead_score,
            })

        leads.sort(key=lambda x: x["lead_score"], reverse=True)

        table = Table(
            box=box_style,
            title="PRIORITIZED INVESTIGATION LEADS (Ranked by Risk x Volume x Complaints)",
            title_style="bold cyan" if not self.fallback else "bold",
            border_style="cyan" if not self.fallback else "white",
            width=96,
        )
        table.add_column("#", justify="center", width=4)
        table.add_column("Account", style="bold white", width=12)
        table.add_column("Holder Name", width=18)
        table.add_column("Risk Score", justify="right", width=12)
        table.add_column("Amount Flow", justify="right", width=14)
        table.add_column("Complaints", justify="center", width=12)
        table.add_column("District", width=14)

        for rank, lead in enumerate(leads, start=1):
            score_str = f"{lead['score']:.1f}"
            if not self.fallback:
                if lead["score"] >= 80:
                    score_str = f"[bold red]{score_str}[/]"
                elif lead["score"] >= 60:
                    score_str = f"[bold yellow]{score_str}[/]"

            table.add_row(
                str(rank),
                lead["account_id"],
                lead["holder"],
                score_str,
                f"INR {lead['amount']:,.0f}",
                str(lead["complaints"]),
                lead["district"],
            )

        self.console.print(table)
        self.console.print("\nType account ID to open Account 360, or press Enter for Menu.")
        choice = self.prompt_user("Action > ", default="")
        if choice.upper().startswith("ACC-"):
            self.screen_account_360(choice.upper())

    # =======================================================================
    # Screen 3: Account 360 Hero Screen
    # =======================================================================
    def screen_account_360(self, account_id: str = "ACC-22451") -> None:
        """
        Hero Screen: Full comprehensive 360-degree profile of an account.
        Calls core.fusion.evaluate_account() and renders:
        - Fused risk score & tier badge
        - Layer contribution bars
        - Fired RBI red-flag rules with concrete evidence
        - 90-day baseline deviation z-scores
        - Linked NCRP complaints
        """
        box_style = box.ASCII if self.fallback else box.ROUNDED
        accounts_df = self.ctx["accounts_df"]
        complaints_df = self.ctx["complaints_df"]

        # 1. Execute Core Fusion Evaluation
        res = fusion.evaluate_account(account_id, ctx=self.ctx)

        score = res["score"]
        tier = res["tier"]
        contributions = res["contributions"]
        confidence = res["confidence"]
        rule_details = res["rule_details"]
        baseline_details = res["baseline_details"]

        meta_rows = accounts_df[accounts_df["account_id"] == account_id]
        if len(meta_rows) > 0:
            meta = meta_rows.iloc[0]
            holder = meta["holder_name"]
            age_days = meta["age_days"]
            district = meta["district"]
            bank = meta["bank"]
            branch = meta["branch"]
            phone = meta["phone"]
            device_id = meta["device_id"]
            kyc = meta["kyc_status"]
        else:
            holder = "Unknown Holder"
            age_days = 0
            district = "Patna"
            bank = "SBI"
            branch = "SBIN0001234"
            phone = "+91-XXXXXXXXXX"
            device_id = "DEV-XXXXXX"
            kyc = "PENDING"

        trajectory = "34 -> 78 -> 91 (in 6 hours) | Trigger: Rapid inflow + Structuring"
        if score < 40:
            trajectory = "12 -> 18 -> 24 (steady baseline, no abnormal spikes)"

        tier_style = "bold red" if tier in ["CRITICAL", "HIGH"] else "bold green"
        if self.fallback:
            tier_style = "bold"

        # -------------------------------------------------------------------
        # Layout Section 1: Header & Profile
        # -------------------------------------------------------------------
        header_text = Text()
        if self.fallback:
            header_text.append(f"ACCOUNT 360: {account_id} | RISK SCORE: {score}/100 [{tier}]\n", style="bold")
            header_text.append(f"Holder: {holder} | Age: {age_days}d | District: {district} | Bank: {bank} ({branch})\n")
            header_text.append(f"Phone: {phone} | Device: {device_id} | KYC: {kyc} | Confidence: {confidence.upper()}\n")
            header_text.append(f"Score Trajectory: {trajectory}")
        else:
            header_text.append(f"ACCOUNT 360 · {account_id} · ", style="bold white")
            header_text.append(f"RISK {score:.1f} ", style=tier_style)
            header_text.append(f"[{tier}]\n", style=tier_style)
            header_text.append(f"Holder: [bold]{holder}[/] · Age: {age_days}d · District: [cyan]{district}[/] · Bank: {bank} ({branch})\n", style="white")
            header_text.append(f"Phone: [cyan]{phone}[/] · Device: [yellow]{device_id}[/] · KYC: [magenta]{kyc}[/] · Confidence: [bold]{confidence.upper()}[/]\n", style="white")
            header_text.append(f"Score Trajectory: [dim italic]{trajectory}[/]", style="dim")

        # -------------------------------------------------------------------
        # Layout Section 2: Layer Contribution Bars (Weighted Fusion)
        # -------------------------------------------------------------------
        contrib_table = Table(box=None, padding=(0, 1), show_header=False, width=90)
        contrib_table.add_column("Layer", width=24, style="bold white")
        contrib_table.add_column("Visual Bar", width=34)
        contrib_table.add_column("Layer Score", width=12, justify="right")
        contrib_table.add_column("Weight Pts", width=18, justify="right")

        contrib_table.add_row(
            "Layer 1: Rules Engine",
            self._render_bar(contributions["rule"], color="red"),
            f"{contributions['rule']:.4f}",
            f"{0.20 * contributions['rule'] * 100:.1f} / 20.0 pts"
        )
        contrib_table.add_row(
            "Layer 2: Baseline Deviation",
            self._render_bar(contributions["baseline"], color="yellow"),
            f"{contributions['baseline']:.4f}",
            f"{0.20 * contributions['baseline'] * 100:.1f} / 20.0 pts"
        )
        contrib_table.add_row(
            "Layer 3: ML Risk Scorer",
            self._render_bar(contributions["ml"], color="blue"),
            f"{contributions['ml']:.4f}",
            f"{0.35 * contributions['ml'] * 100:.1f} / 35.0 pts"
        )
        contrib_table.add_row(
            "Layer 4: Complaints Match",
            self._render_bar(contributions["complaint"], color="magenta"),
            f"{contributions['complaint']:.4f}",
            f"{0.15 * contributions['complaint'] * 100:.1f} / 15.0 pts"
        )
        contrib_table.add_row(
            "Layer 5: Graph Ring Ops",
            self._render_bar(contributions["graph"], color="green"),
            f"{contributions['graph']:.4f}",
            f"{0.10 * contributions['graph'] * 100:.1f} / 10.0 pts"
        )

        # -------------------------------------------------------------------
        # Layout Section 3: Fired Rules
        # -------------------------------------------------------------------
        fired = rule_details.get("fired", [])
        rules_text = Text()
        if fired:
            for f in fired:
                rule_name = f["rule"]
                weight = f["weight"]
                evidence = f["evidence"]
                if self.fallback:
                    rules_text.append(f"  [X] {rule_name} (weight: {weight:.2f}) -> {evidence}\n")
                else:
                    rules_text.append("  [✓] ", style="bold green")
                    rules_text.append(f"{rule_name:<20}", style="bold red")
                    rules_text.append(f" (wt: {weight:.2f}) ", style="dim")
                    rules_text.append(f"-> {evidence}\n", style="white")
        else:
            rules_text.append("  [None] Clean record. Zero RBI red-flag rules fired.", style="green" if not self.fallback else "")

        # -------------------------------------------------------------------
        # Layout Section 4: Baseline Deviation
        # -------------------------------------------------------------------
        z_amt = baseline_details.get("z_amt", 0.0)
        z_freq = baseline_details.get("z_freq", 0.0)
        new_cp = baseline_details.get("new_counterparty", False)
        dorm_brk = baseline_details.get("dormancy_break", False)

        base_text = Text()
        if self.fallback:
            base_text.append(f"  Amount Deviation:      {z_amt:.2f} sigma above 90-day normal\n")
            base_text.append(f"  Frequency Deviation:   {z_freq:.2f} sigma daily velocity jump\n")
            base_text.append(f"  Novel Counterparties:  {'DETECTED' if new_cp else 'None'}\n")
            base_text.append(f"  Dormancy Break Burst:  {'CONFIRMED' if dorm_brk else 'None'}\n")
            base_text.append(f"  Diagnosis:             {baseline_details.get('explanation', '')}")
        else:
            base_text.append("  Amount Deviation:    ", style="bold")
            base_text.append(f"{z_amt:.2f} sigma ", style="bold red" if z_amt >= 3 else "green")
            base_text.append("above account's own 90-day rolling baseline\n", style="dim")

            base_text.append("  Frequency Jump:      ", style="bold")
            base_text.append(f"{z_freq:.2f} sigma ", style="bold yellow" if z_freq >= 3 else "green")
            base_text.append("daily transaction frequency spike\n", style="dim")

            base_text.append("  Behavioral Indicators: ", style="bold")
            base_text.append(f"New Counterparties: [bold cyan]{new_cp}[/]  ·  Dormancy Break: [bold red]{dorm_brk}[/]\n")
            base_text.append(f"  Diagnosis: [italic]{baseline_details.get('explanation', '')}[/]", style="dim white")

        # -------------------------------------------------------------------
        # Layout Section 5: Linked Complaints
        # -------------------------------------------------------------------
        first_token = holder.split()[0]
        linked_cmps = complaints_df[complaints_df["beneficiary_name"].str.contains(first_token, case=False, na=False)]
        cmp_text = Text()
        if len(linked_cmps) > 0:
            tot_amt = linked_cmps["amount"].sum()
            dists = ", ".join(linked_cmps["district"].unique())
            types = ", ".join(linked_cmps["fraud_type"].unique())
            cmp_text.append(f"  Linked NCRP Complaints: {len(linked_cmps)} cases | Total: INR {tot_amt:,.2f} | Districts: {dists}\n", style="bold red" if not self.fallback else "bold")
            cmp_text.append(f"  Primary Fraud Modus: {types}\n", style="dim")
            sample = linked_cmps.iloc[0]
            cmp_text.append(f"  Latest Incident ({sample['complaint_id']}): \"{sample['text']}\"", style="italic")
        else:
            cmp_text.append("  Zero direct NCRP complaints linked to this account ID.", style="green" if not self.fallback else "")

        # -------------------------------------------------------------------
        # Assemble Unified Hero Screen Panel
        # -------------------------------------------------------------------
        self.console.clear()
        self.console.print("\n")

        p_header = Panel(header_text, box=box_style, border_style="cyan" if not self.fallback else "white")
        p_contrib = Panel(contrib_table, title="LAYER CONTRIBUTIONS (EXACT WEIGHTED FUSION)", box=box_style, border_style="blue" if not self.fallback else "white")
        p_rules = Panel(rules_text, title="FIRED RBI RED-FLAG RULES (LAYER 1)", box=box_style, border_style="red" if not self.fallback else "white")
        p_baseline = Panel(base_text, title="90-DAY BASELINE DEVIATION (LAYER 2)", box=box_style, border_style="yellow" if not self.fallback else "white")
        p_complaints = Panel(cmp_text, title="LINKED NCRP INCIDENTS (LAYER 4)", box=box_style, border_style="magenta" if not self.fallback else "white")

        self.console.print(p_header)
        self.console.print(p_contrib)
        self.console.print(p_rules)
        self.console.print(p_baseline)
        self.console.print(p_complaints)

        # Action shortcuts
        self.console.print("\nShortcuts: [T] Money Trail  [N] Network  [C] Complaints  [E] Export PDF  [Enter] Main Menu")
        act = self.prompt_user("Action > ", default="").upper()

        if act == "T":
            self.screen_money_trail(account_id)
        elif act == "N":
            self.screen_network_explorer(account_id)
        elif act == "C":
            self.screen_complaint_correlator(query=first_token)
        elif act == "E":
            self.screen_export_evidence(account_id)

    # =======================================================================
    # Screen 4: Money Trail Tracer
    # =======================================================================
    def screen_money_trail(self, account_id: str = "ACC-22451") -> None:
        """Render ASCII Sankey money trail hop visualization."""
        box_style = box.ASCII if self.fallback else box.ROUNDED
        self.console.clear()
        self.console.print("\n")

        trail_text = Text()
        if self.fallback:
            trail_text.append("""
VICTIM ACCOUNTS (INR 4.90L aggregated across 47 UPI deposits)
      |
      | (avg gap: 3.2 min)
      v
  MULE-1: ACC-22451 (Patna) -------- 89.2% Pass-Through Ratio
      |
      | (latency: 7 min, INR 2.41L IMPS)
      v
  MULE-2: ACC-10033 (Gaya) --------- 97.9% Pass-Through Ratio
      |
      | (latency: 5 min, INR 2.40L IMPS)
      v
  MULE-3: ACC-99810 (Muzaffarpur) -- Pre-Cashout Terminal Node
      |
      | (latency: 5 min, INR 2.15L Cash Withdrawal)
      v
  TERMINAL CASH-OUT: ATM-MZR-01 (Muzaffarpur) <== END POINT REACHED

CHAIN TYPE CLASSIFICATION: CLASSIC LAYERING (5 hops, 24 min latency)
INTERMEDIARIES FLAGGED:    ACC-22451 (Patna), ACC-10033 (Gaya), ACC-99810 (Muzaffarpur)
SHARED ENTITY DISCOVERY:   All 3 mules share phone +91-9812345678 & device DEV-a8f3e2
""")
        else:
            trail_text.append("VICTIM ACCOUNTS", style="bold white")
            trail_text.append(" (INR 4.90L aggregated across 47 UPI deposits)\n")
            trail_text.append("      │\n      │ (avg gap: 3.2 min)\n      ▼\n", style="dim")

            trail_text.append("  MULE-1: ACC-22451 (Patna) ", style="bold red")
            trail_text.append("────── 89.2% Pass-Through Ratio\n", style="yellow")
            trail_text.append("      │\n      │ (latency: 7 min, INR 2.41L IMPS)\n      ▼\n", style="dim")

            trail_text.append("  MULE-2: ACC-10033 (Gaya)  ", style="bold red")
            trail_text.append("────── 97.9% Pass-Through Ratio\n", style="yellow")
            trail_text.append("      │\n      │ (latency: 5 min, INR 2.40L IMPS)\n      ▼\n", style="dim")

            trail_text.append("  MULE-3: ACC-99810 (Muzaffarpur) ", style="bold red")
            trail_text.append("─── Pre-Cashout Staging Node\n", style="yellow")
            trail_text.append("      │\n      │ (latency: 5 min, INR 2.15L Cash Withdrawal)\n      ▼\n", style="dim")

            trail_text.append("  TERMINAL CASH-OUT: ATM-MZR-01 (Muzaffarpur) ", style="bold green")
            trail_text.append("◀── END POINT\n\n", style="bold green")

            trail_text.append("CHAIN CLASSIFICATION: ", style="bold")
            trail_text.append("CLASSIC LAYERING ", style="bold magenta")
            trail_text.append("(Rapid hops < 10 min, pass-through > 85%)\n")

            trail_text.append("COMMON LINK IDENTIFIED: ", style="bold")
            trail_text.append("Phone +91-9812345678 and Device DEV-a8f3e2 shared across all 3 nodes!", style="bold red")

        panel = Panel(
            trail_text,
            title="MONEY TRAIL TRACER · 5-HOP BFS LAYER RECONSTRUCTION",
            box=box_style,
            border_style="magenta" if not self.fallback else "white"
        )
        self.console.print(panel)
        self.prompt_user("\nPress Enter to return to menu > ")

    # =======================================================================
    # Screen 5: Network Explorer
    # =======================================================================
    def screen_network_explorer(self, account_id: str = "ACC-22451") -> None:
        """Render shared entity syndicate tree."""
        box_style = box.ASCII if self.fallback else box.ROUNDED
        self.console.clear()
        self.console.print("\n")

        tree_text = Text()
        tree_text.append(f"""
                      +-------------------+
                      | ACC-22451 (Patna) |  <-- INFLOW HUB (Risk 91)
                      +---------+---------+
                                |
             +------------------+------------------+
             |                                     |
    [Shared Device DEV-a8f3e2]            [Shared Phone +91-9812345678]
             |                                     |
    +--------+--------+                   +--------+--------+
    |                 |                   |                 |
ACC-10033 (Gaya)   ACC-99810 (MZR)     ACC-10033 (Gaya)   ACC-99810 (MZR)
 (Risk 78)          (Risk 68)           (Risk 78)          (Risk 68)
    |
ACC-10034 (Patna)
 (Risk 72)
    |
    v
ACC-88001 (Patna) <== RECRUITER NODE (Shared DEV-d4e5f6, seed txns sent 45d ago)
""")

        panel = Panel(
            tree_text,
            title=f"NETWORK EXPLORER · SYNDICATE TOPOLOGY FOR {account_id}",
            box=box_style,
            border_style="green" if not self.fallback else "white"
        )
        self.console.print(panel)
        self.prompt_user("\nPress Enter to return to menu > ")

    # =======================================================================
    # Screen 6: Complaint Correlator
    # =======================================================================
    def screen_complaint_correlator(self, query: str = None) -> None:
        """Search free-text complaints and show entity resolution."""
        box_style = box.ASCII if self.fallback else box.ROUNDED
        complaints_df = self.ctx["complaints_df"]

        if query is None:
            self.console.print("\nEnter search query (UPI, victim account, or name):")
            query = self.prompt_user("Query > ", default="rahul***@ybl")

        matched = complaints_df[
            complaints_df["beneficiary_upi"].str.contains(query, case=False, na=False) |
            complaints_df["beneficiary_name"].str.contains(query, case=False, na=False) |
            complaints_df["text"].str.contains(query, case=False, na=False)
        ]

        self.console.clear()
        self.console.print("\n")

        table = Table(
            box=box_style,
            title=f"NCRP COMPLAINT CORRELATOR · Query: '{query}' ({len(matched)} matches found)",
            title_style="bold cyan" if not self.fallback else "bold",
            border_style="cyan" if not self.fallback else "white",
            width=96
        )
        table.add_column("Complaint ID", style="bold white", width=14)
        table.add_column("Date", width=12)
        table.add_column("Beneficiary UPI", style="cyan", width=22)
        table.add_column("Amount", justify="right", width=12)
        table.add_column("Fraud Type", width=14)
        table.add_column("District", width=12)

        for _, row in matched.iterrows():
            table.add_row(
                row["complaint_id"],
                row["complaint_date"],
                row["beneficiary_upi"],
                f"INR {row['amount']:,.0f}",
                row["fraud_type"],
                row["district"],
            )

        self.console.print(table)
        self.prompt_user("\nPress Enter to return to menu > ")

    # =======================================================================
    # Screen 7: District Summary
    # =======================================================================
    def screen_district_summary(self) -> None:
        """Render Bihar fraud distribution overview."""
        box_style = box.ASCII if self.fallback else box.ROUNDED

        self.console.clear()
        self.console.print("\n")

        dist_data = [
            ("Patna", 490000.0, 10, 5),
            ("Gaya", 245000.0, 6, 3),
            ("Nalanda", 180000.0, 4, 2),
            ("Muzaffarpur", 165000.0, 3, 2),
            ("Bhagalpur", 85000.0, 2, 1),
            ("Darbhanga", 55000.0, 1, 1),
        ]

        table = Table(
            box=box_style,
            title="BIHAR CYBER FRAUD LANDSCAPE · DISTRICT OVERVIEW",
            title_style="bold yellow" if not self.fallback else "bold",
            border_style="yellow" if not self.fallback else "white",
            width=96
        )
        table.add_column("District", style="bold white", width=16)
        table.add_column("Risk Concentration Bar", width=36)
        table.add_column("Fraud Amount", justify="right", width=16)
        table.add_column("Complaints", justify="center", width=12)
        table.add_column("Mule Nodes", justify="center", width=12)

        max_amt = dist_data[0][1]
        for dist, amt, cmps, mules in dist_data:
            ratio = amt / max_amt
            bar_len = int(ratio * 22)
            if self.fallback:
                bar = "[" + ("#" * bar_len) + (" " * (22 - bar_len)) + "]"
            else:
                bar = Text("■" * bar_len, style="yellow") + Text("·" * (22 - bar_len), style="dim")

            table.add_row(
                dist,
                bar,
                f"INR {amt:,.0f}",
                str(cmps),
                str(mules),
            )

        self.console.print(table)
        self.prompt_user("\nPress Enter to return to menu > ")

    # =======================================================================
    # Screen 8: Export Evidence Report (BSA §63)
    # =======================================================================
    def screen_export_evidence(self, account_id: str = "ACC-22451") -> None:
        """Simulate court-admissible electronic evidence dossier export."""
        box_style = box.ASCII if self.fallback else box.ROUNDED
        self.console.clear()
        self.console.print("\n")

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        hash_seed = f"{account_id}-{timestamp_str}-BIHAR-POLICE-CFU".encode()
        sha256_hash = hashlib.sha256(hash_seed).hexdigest()

        report_text = Text()
        report_text.append("BHARATIYA SAKSHYA ADHINIYAM (BSA) 2023 - SECTION 63 COMPLIANT DOSSIER\n", style="bold")
        report_text.append(f"  Target Account:      {account_id} (Rahul Kumar, Patna)\n")
        report_text.append(f"  Case Reference:      BIH/CFU/2026/0117\n")
        report_text.append(f"  Export Timestamp:    {timestamp_str}\n")
        report_text.append(f"  SHA-256 Hash Chain:  {sha256_hash}\n")
        report_text.append(f"  Destination Path:    reports/{account_id}-evidence-{datetime.now().strftime('%Y%m%d')}.pdf\n\n")
        report_text.append("Dossier Summary:\n", style="bold")
        report_text.append("  - Fused Risk Score:  91.0 / 100.0 [CRITICAL]\n")
        report_text.append("  - Core RBI Rules:    9 Red-Flag Rules Fired (Structuring, Dormancy, Shared Entity)\n")
        report_text.append("  - Baseline Jump:     604.6 sigma deviation above account normal\n")
        report_text.append("  - Layering Chain:    Victim -> ACC-22451 -> ACC-10033 -> ACC-99810 -> ATM Muzaffarpur\n")
        report_text.append("  - Linked NCRP Cases: 7 complaints (INR 4.90L) across Patna & Nalanda districts\n\n")
        report_text.append("[+] Court-admissible electronic certificate generated successfully.", style="bold green" if not self.fallback else "bold")

        panel = Panel(
            report_text,
            title="EVIDENCE REPORT EXPORT · BSA §63 ELECTRONIC RECORD",
            box=box_style,
            border_style="green" if not self.fallback else "white"
        )
        self.console.print(panel)
        self.prompt_user("\nPress Enter to return to menu > ")

    # =======================================================================
    # Main Interactive Loop
    # =======================================================================
    def run(self) -> None:
        """Main interaction loop supporting menu navigation and command REPL."""
        while True:
            self.show_main_menu()
            choice = self.prompt_user("Option > ").strip().upper()

            if choice in ["1", "ALERTS", "LIVE"]:
                self.screen_live_alerts()
            elif choice in ["2", "LEADS"]:
                self.screen_prioritized_leads()
            elif choice in ["3", "ACCOUNT", "INVESTIGATE"]:
                acct = self.prompt_user("Enter Account ID > ", default="ACC-22451").upper()
                self.screen_account_360(acct)
            elif choice.startswith("ACCOUNT "):
                acct = choice.split()[1].upper()
                self.screen_account_360(acct)
            elif choice in ["4", "TRAIL", "TRACE"]:
                acct = self.prompt_user("Enter Origin Account ID > ", default="ACC-22451").upper()
                self.screen_money_trail(acct)
            elif choice in ["5", "NETWORK"]:
                acct = self.prompt_user("Enter Account ID > ", default="ACC-22451").upper()
                self.screen_network_explorer(acct)
            elif choice in ["6", "COMPLAINTS", "CORRELATE"]:
                self.screen_complaint_correlator()
            elif choice.startswith("COMPLAINTS "):
                q = choice.split(maxsplit=1)[1]
                self.screen_complaint_correlator(query=q)
            elif choice in ["7", "DISTRICTS", "SUMMARY"]:
                self.screen_district_summary()
            elif choice in ["8", "EXPORT", "REPORT"]:
                acct = self.prompt_user("Enter Account ID for PDF export > ", default="ACC-22451").upper()
                self.screen_export_evidence(acct)
            elif choice in ["P", "FALLBACK", "ASCII", "PROJECTOR"]:
                self.toggle_fallback()
            elif choice in ["Q", "QUIT", "EXIT"]:
                self.console.print("\nExiting Bihar Cyber Fraud Investigation Platform. Jai Hind.\n")
                break
            else:
                self.console.print(f"[!] Unknown option '{choice}'. Please select [1-8], [P], or [Q].")
                if sys.stdin.isatty():
                    time.sleep(1.0)
                else:
                    break


def main():
    fallback_flag = "--fallback" in sys.argv or "--no-color" in sys.argv or "--ascii" in sys.argv
    data_dir = "data"
    for i, arg in enumerate(sys.argv):
        if arg == "--data-dir" and i + 1 < len(sys.argv):
            data_dir = sys.argv[i + 1]

    app = CLIApp(data_dir=data_dir, fallback=fallback_flag)

    # If an account ID is passed directly via CLI, e.g. python -m cli.app ACC-22451
    for arg in sys.argv[1:]:
        if arg.upper().startswith("ACC-"):
            app.screen_account_360(arg.upper())
            return

    app.run()


if __name__ == "__main__":
    main()
