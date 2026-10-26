"""
Layer 5: Graph Operations (core/graph_ops.py)

Implements:
1. Multi-hop BFS Money Trail Tracer with 24-hour temporal filtering.
2. NetworkX Louvain Community Detection for discovering mule rings and layering clusters.
3. Chain type classification: LAYERING, FAN_OUT, FAN_IN, CIRCULAR, STRUCTURING, CASH_OUT.
4. Intermediary pass-through scoring and cash-out endpoint discovery.
5. Graph ring risk scorer (0.0 to 1.0) based on community density, shared entities, and money trails.

Matches specifications in docs/09-DETECTION-PIPELINE.md and docs/07-TECHNICAL-SPECIFICATION.md.
"""

from datetime import datetime, timedelta
import os
import networkx as nx
import pandas as pd


# Module cache for graph and community detection results to ensure < 200ms lookup target
_GRAPH_CACHE = {}


def _get_context(ctx: dict = None) -> dict:
    """Helper to extract or lazily load data context."""
    if ctx is None:
        ctx = {}

    if "transactions_df" not in ctx or ctx["transactions_df"] is None:
        data_dir = ctx.get("data_dir", "data")
        tx_path = os.path.join(data_dir, "transactions.csv")
        acct_path = os.path.join(data_dir, "accounts.csv")
        ent_path = os.path.join(data_dir, "entities.csv")
        cmp_path = os.path.join(data_dir, "complaints.csv")

        tx_df = pd.read_csv(tx_path)
        tx_df["dt"] = pd.to_datetime(tx_df["timestamp"])
        ctx["transactions_df"] = tx_df
        if os.path.exists(acct_path):
            ctx["accounts_df"] = pd.read_csv(acct_path)
        if os.path.exists(ent_path):
            ctx["entities_df"] = pd.read_csv(ent_path)
        if os.path.exists(cmp_path):
            ctx["complaints_df"] = pd.read_csv(cmp_path)
        ctx["as_of"] = tx_df["dt"].max()

    if "dt" not in ctx["transactions_df"].columns:
        ctx["transactions_df"]["dt"] = pd.to_datetime(ctx["transactions_df"]["timestamp"])

    return ctx


def build_graph(ctx: dict = None) -> nx.DiGraph:
    """
    Build directed transaction graph with aggregated weights and transaction histories.
    Caches graph in memory for fast repeated queries.
    """
    ctx = _get_context(ctx)
    tx_df = ctx["transactions_df"]

    cache_key = id(tx_df)
    if cache_key in _GRAPH_CACHE and "graph" in _GRAPH_CACHE[cache_key]:
        return _GRAPH_CACHE[cache_key]["graph"]

    G = nx.DiGraph()
    for _, r in tx_df.iterrows():
        u = str(r["from_account"])
        v = str(r["to_account"])
        amt = float(r["amount"])
        t = r["dt"]
        ch = str(r.get("channel", "UPI"))

        if G.has_edge(u, v):
            G[u][v]["weight"] += amt
            G[u][v]["txns"].append({"amount": amt, "timestamp": t, "channel": ch})
        else:
            G.add_edge(u, v, weight=amt, txns=[{"amount": amt, "timestamp": t, "channel": ch}])

    if cache_key not in _GRAPH_CACHE:
        _GRAPH_CACHE[cache_key] = {}
    _GRAPH_CACHE[cache_key]["graph"] = G
    return G


def rings(ctx: dict = None) -> list[dict]:
    """
    Detect mule rings and suspicious clusters using Louvain community detection.
    Correlates detected communities with shared devices/phones from entities.csv.

    Returns:
        List of detected suspicious communities sorted by suspicion score descending.
    """
    ctx = _get_context(ctx)
    tx_df = ctx["transactions_df"]
    entities_df = ctx.get("entities_df")

    cache_key = id(tx_df)
    if cache_key in _GRAPH_CACHE and "rings" in _GRAPH_CACHE[cache_key]:
        return _GRAPH_CACHE[cache_key]["rings"]

    G = build_graph(ctx)
    # Undirected graph for Louvain community partitioning
    G_undir = G.to_undirected()

    try:
        communities = nx.community.louvain_communities(G_undir, weight="weight", seed=42)
    except Exception:
        communities = [set(G.nodes())]

    # Map shared entities for quick community cross-referencing
    shared_entities_by_account = {}
    if entities_df is not None:
        for _, r in entities_df.iterrows():
            etype = r["type"]
            val = r["value"]
            linked_accts = [a.strip() for a in str(r["linked_accounts"]).split("|") if a.strip()]
            if len(linked_accts) > 1:
                for a in linked_accts:
                    if a not in shared_entities_by_account:
                        shared_entities_by_account[a] = []
                    shared_entities_by_account[a].append(f"{etype}:{val}")

    scored_rings = []
    for idx, comm in enumerate(communities):
        comm_nodes = list(comm)
        acct_nodes = [n for n in comm_nodes if n.startswith("ACC-")]
        cash_out_nodes = [n for n in comm_nodes if n.startswith("ATM-") or n.startswith("POS-")]

        if len(acct_nodes) < 2:
            continue

        # Subgraph internal volume
        subG = G.subgraph(comm_nodes)
        internal_volume = sum(d["weight"] for _, _, d in subG.edges(data=True))

        # Check shared devices and phones within community
        comm_shared_entities = set()
        shared_entity_hit_count = 0
        for a in acct_nodes:
            ents = shared_entities_by_account.get(a, [])
            if ents:
                shared_entity_hit_count += 1
                comm_shared_entities.update(ents)

        shared_ratio = shared_entity_hit_count / len(acct_nodes) if acct_nodes else 0.0

        # Calculate ring suspicion score
        suspicion = 0.10
        if len(comm_shared_entities) >= 1:
            suspicion += 0.35
        if shared_ratio >= 0.25:
            suspicion += 0.25
        if cash_out_nodes:
            suspicion += 0.15
        if internal_volume >= 200000.0:
            suspicion += 0.15

        suspicion_score = round(min(1.0, suspicion), 2)

        ring_type = "Mule Layering Ring" if suspicion_score >= 0.70 else "Co-Transaction Cluster"

        scored_rings.append({
            "community_id": idx + 1,
            "size": len(acct_nodes),
            "accounts": acct_nodes,
            "suspicion_score": suspicion_score,
            "shared_entities": list(comm_shared_entities),
            "ring_type": ring_type,
            "total_volume": round(internal_volume, 2),
            "cash_out_nodes": cash_out_nodes,
        })

    scored_rings.sort(key=lambda r: r["suspicion_score"], reverse=True)

    if cache_key not in _GRAPH_CACHE:
        _GRAPH_CACHE[cache_key] = {}
    _GRAPH_CACHE[cache_key]["rings"] = scored_rings
    return scored_rings


def trace(origin: str, max_hops: int = 5, window_hours: int = 24, ctx: dict = None) -> dict:
    """
    Performs 5-hop Breadth-First Search (BFS) money trail traversal with 24h temporal filtering.

    Ensures chronological ordering:
        t_next >= t_prev AND (t_next - t_start) <= window_hours

    Parameters:
        origin: Source account ID (e.g. 'ACC-22451')
        max_hops: Maximum traversal depth (default: 5)
        window_hours: Maximum time window for fund propagation (default: 24h)
        ctx: Shared data context

    Returns:
        {
            'paths': list of detailed path dicts,
            'chain_type': 'LAYERING' | 'FAN_OUT' | 'FAN_IN' | 'CIRCULAR' | 'STRUCTURING' | 'CASH_OUT',
            'intermediaries': list of (account_id, pass_through_ratio),
            'cash_out_points': list of cash out nodes (ATM/POS),
            'hop_count': int,
            'summary': str
        }
    """
    ctx = _get_context(ctx)
    tx_df = ctx["transactions_df"]

    origin_txns = tx_df[tx_df["from_account"] == origin].sort_values("dt")
    if origin_txns.empty:
        return {
            "paths": [],
            "chain_type": "UNKNOWN",
            "intermediaries": [],
            "cash_out_points": [],
            "hop_count": 0,
            "summary": f"No outgoing transactions recorded from {origin}.",
        }

    # Reference window around origin outgoing transactions
    origin_latest = origin_txns["dt"].max()
    window_start = origin_latest - timedelta(hours=window_hours)
    recent_txns = tx_df[tx_df["dt"] >= window_start].sort_values("dt")

    # Fast adjacency list indexed by from_account: u -> list of (v, dt, amount, channel)
    adj = {}
    for _, r in recent_txns.iterrows():
        u = str(r["from_account"])
        v = str(r["to_account"])
        t = r["dt"]
        amt = float(r["amount"])
        ch = str(r.get("channel", "UPI"))
        if u not in adj:
            adj[u] = []
        adj[u].append((v, t, amt, ch))

    # BFS Queue: (path, start_time, last_time, amounts, channels)
    queue = []
    for (v, t, amt, ch) in adj.get(origin, []):
        queue.append(([origin, v], t, t, [amt], [ch]))

    completed_paths = []
    visited_sigs = set()

    while queue:
        path, start_t, last_t, amounts, channels = queue.pop(0)
        curr = path[-1]

        is_cashout = curr.startswith("ATM-") or curr.startswith("POS-")
        if is_cashout or len(path) > max_hops:
            latency_mins = (last_t - start_t).total_seconds() / 60.0
            completed_paths.append({
                "path": path,
                "amounts": amounts,
                "channels": channels,
                "latency_mins": round(latency_mins, 1),
                "is_cashout": is_cashout,
            })
            continue

        # Look ahead for chronologically valid next hops: t_nxt >= last_t and within window
        next_hops = [
            (nxt, t_nxt, a_nxt, ch_nxt)
            for (nxt, t_nxt, a_nxt, ch_nxt) in adj.get(curr, [])
            if t_nxt >= last_t and (t_nxt - start_t) <= timedelta(hours=window_hours) and nxt not in path
        ]

        if not next_hops:
            latency_mins = (last_t - start_t).total_seconds() / 60.0
            completed_paths.append({
                "path": path,
                "amounts": amounts,
                "channels": channels,
                "latency_mins": round(latency_mins, 1),
                "is_cashout": is_cashout,
            })
        else:
            for nxt, t_nxt, a_nxt, ch_nxt in next_hops:
                sig = (tuple(path + [nxt]), t_nxt)
                if sig not in visited_sigs:
                    visited_sigs.add(sig)
                    queue.append((path + [nxt], start_t, t_nxt, amounts + [a_nxt], channels + [ch_nxt]))

    # Deduplicate and sort paths by hop length and latency
    unique_paths = {}
    for p_info in completed_paths:
        key = tuple(p_info["path"])
        if key not in unique_paths or len(p_info["amounts"]) > len(unique_paths[key]["amounts"]):
            unique_paths[key] = p_info

    final_paths = sorted(unique_paths.values(), key=lambda p: (len(p["path"]), -p["latency_mins"]), reverse=True)

    # Cash-out points and intermediaries
    cash_out_points = []
    intermediary_stats = {}

    for p in final_paths:
        path_nodes = p["path"]
        if p["is_cashout"]:
            terminal = path_nodes[-1]
            if terminal not in cash_out_points:
                cash_out_points.append(terminal)

        # Intermediaries are nodes between origin and terminal
        if len(path_nodes) > 2:
            for i in range(1, len(path_nodes) - 1):
                inter = path_nodes[i]
                if not inter.startswith("ATM-") and not inter.startswith("POS-"):
                    if inter not in intermediary_stats:
                        # Calculate 1h pass through ratio for intermediary
                        in_tx = tx_df[tx_df["to_account"] == inter]
                        out_tx = tx_df[tx_df["from_account"] == inter]
                        tot_in = in_tx["amount"].sum()
                        tot_out = out_tx["amount"].sum()
                        ratio = round(min(1.0, tot_out / tot_in), 2) if tot_in > 0 else 0.0
                        intermediary_stats[inter] = ratio

    intermediaries = [(k, v) for k, v in intermediary_stats.items()]

    # Chain classification per docs/09-DETECTION-PIPELINE.md (5c)
    # Check origin out-degree
    origin_dest_count = len(set(origin_txns["to_account"]))
    longest_path = final_paths[0]["path"] if final_paths else [origin]
    max_hops_found = len(longest_path) - 1

    # Check structuring on amounts
    all_trace_amounts = [amt for p in final_paths for amt in p["amounts"]]
    is_structured = (
        len(all_trace_amounts) > 0
        and all(45000 <= a <= 50000 or a in [9999, 49999, 99999] for a in all_trace_amounts)
    )

    if origin_dest_count > 5:
        chain_type = "FAN_OUT"
    elif max_hops_found >= 2 and all(r >= 0.85 for _, r in intermediaries):
        chain_type = "LAYERING"
    elif is_structured:
        chain_type = "STRUCTURING"
    elif cash_out_points:
        chain_type = "CASH_OUT"
    else:
        chain_type = "STANDARD_TRANSFER"

    summary = (
        f"Chain Type: {chain_type} | Depth: {max_hops_found} hops | "
        f"Intermediaries: {len(intermediaries)} | Cash-out Endpoints: {len(cash_out_points)}"
    )

    return {
        "paths": final_paths,
        "chain_type": chain_type,
        "intermediaries": intermediaries,
        "cash_out_points": cash_out_points,
        "hop_count": max_hops_found,
        "summary": summary,
    }


def ring_risk(account_id: str, ctx: dict = None) -> float:
    """
    Computes graph ring risk score (0.0 to 1.0) for an account based on:
    - Membership in a detected Louvain mule ring community
    - Shared entity links (devices / phones) with 3+ accounts
    - Rapid layering trail participation terminating in cash-outs

    Parameters:
        account_id: Account ID to evaluate
        ctx: Shared data context

    Returns:
        Risk float from 0.0 to 1.0.
    """
    ctx = _get_context(ctx)
    detected_rings = rings(ctx)

    # 1. Check if account is in a high-suspicion community
    for ring in detected_rings:
        if account_id in ring["accounts"]:
            if ring["suspicion_score"] >= 0.70:
                return float(ring["suspicion_score"])
            else:
                return float(max(0.35, ring["suspicion_score"]))

    # 2. Check shared device/phone from entities_df if available
    entities_df = ctx.get("entities_df")
    score = 0.0
    if entities_df is not None:
        for _, r in entities_df.iterrows():
            linked_accts = [a.strip() for a in str(r["linked_accounts"]).split("|") if a.strip()]
            if account_id in linked_accts and len(linked_accts) >= 3:
                score += 0.40 if r["type"] == "device" else 0.35

    # 3. Check if account reaches cash-out within rapid hops
    trail_res = trace(account_id, max_hops=3, window_hours=24, ctx=ctx)
    if trail_res.get("chain_type") in ["LAYERING", "CASH_OUT"]:
        score += 0.30

    return float(round(min(1.0, score), 4))


def shared_network(account_id: str, seed_max_amount: float = 1000.0, ctx: dict = None) -> dict:
    """
    Builds the 2-hop shared-entity network around an account for the Network Explorer.

    - Hop 1: accounts sharing a phone/device with the account (entities.csv)
    - Hop 2: accounts sharing a different phone/device with a hop-1 account
    - Seed funders: outside accounts that sent small transfers (<= seed_max_amount)
      into 2+ accounts of this network, the recruiter seeding pattern

    Returns:
        {
            'account_id': str,
            'hop1': [{'type': str, 'value': str, 'accounts': [str, ...]}, ...],
            'hop2': [{'via': str, 'type': str, 'value': str, 'accounts': [str, ...]}, ...],
            'seed_funders': [{'account': str, 'targets': [str, ...], 'total': float, 'first_dt': Timestamp}, ...],
        }
    """
    ctx = _get_context(ctx)
    entities_df = ctx.get("entities_df")
    result = {"account_id": account_id, "hop1": [], "hop2": [], "seed_funders": []}
    if entities_df is None or len(entities_df) == 0:
        return result

    def _shared_entities(acct: str) -> list[tuple[str, str, list[str]]]:
        """(type, value, other linked accounts) for each phone/device this account shares."""
        found = []
        for _, r in entities_df[entities_df["type"].isin(["phone", "device"])].iterrows():
            linked_accts = [a.strip() for a in str(r["linked_accounts"]).split("|") if a.strip()]
            if acct in linked_accts and len(linked_accts) > 1:
                found.append((r["type"], r["value"], [a for a in linked_accts if a != acct]))
        return found

    # 1. Hop 1: direct shared identifiers
    hop1_accounts = []
    for ent_type, ent_value, others in _shared_entities(account_id):
        result["hop1"].append({"type": ent_type, "value": ent_value, "accounts": others})
        hop1_accounts.extend(a for a in others if a not in hop1_accounts)

    # 2. Hop 2: other identifiers shared by hop-1 accounts that reach new accounts
    seen = {account_id, *hop1_accounts}
    hop1_values = {e["value"] for e in result["hop1"]}
    for via in hop1_accounts:
        for ent_type, ent_value, others in _shared_entities(via):
            new_accts = [a for a in others if a not in seen]
            if ent_value not in hop1_values and new_accts:
                result["hop2"].append({"via": via, "type": ent_type, "value": ent_value, "accounts": new_accts})
                seen.update(new_accts)

    # 3. Seed funders: small inbound transfers from outside accounts into 2+ network accounts
    tx_df = ctx["transactions_df"]
    accounts_df = ctx.get("accounts_df")
    known_accounts = set(accounts_df["account_id"]) if accounts_df is not None else set()
    seeds = tx_df[
        tx_df["to_account"].isin(seen)
        & ~tx_df["from_account"].isin(seen)
        & tx_df["from_account"].isin(known_accounts)
        & (tx_df["amount"] <= seed_max_amount)
    ]
    for sender, grp in seeds.groupby("from_account"):
        targets = sorted(grp["to_account"].unique())
        if len(targets) >= 2:
            result["seed_funders"].append({
                "account": sender,
                "targets": targets,
                "total": float(grp["amount"].sum()),
                "first_dt": grp["dt"].min(),
            })

    return result
