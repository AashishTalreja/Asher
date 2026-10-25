"""
Layer 5: Graph Operations (core/graph_ops.py)

Mock implementation for initial pipeline testing.
Returns a default graph ring risk contribution of 0.5.
"""


def ring_risk(account_id: str, ctx: dict = None) -> float:
    """
    Returns graph ring risk score (0.0 to 1.0) for an account based on
    community density, shared entities, and money trails.
    """
    return 0.5


def trace(origin: str, max_hops: int = 5, window_hours: int = 24, ctx: dict = None) -> dict:
    """
    Traces 5-hop BFS money trail from origin account.
    """
    return {
        "paths": [],
        "chain_type": "LAYERING",
        "intermediaries": [],
        "cash_out_points": [],
    }


def rings(ctx: dict = None) -> list[dict]:
    """
    Returns detected communities and rings.
    """
    return []
