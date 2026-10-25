"""
Layer 4: Complaint Correlator (core/complaints.py)

Mock implementation for initial pipeline testing.
Returns a default complaint risk contribution of 0.5.
"""


def score(account_id: str, ctx: dict = None) -> float:
    """
    Returns normalized complaint risk score (0.0 to 1.0) for an account.
    """
    return 0.5


def linked(account_id: str, ctx: dict = None) -> list[dict]:
    """
    Returns list of complaints linked to this account.
    """
    return []


def resolve(query: str, ctx: dict = None) -> list[dict]:
    """
    Returns matched accounts with confidence scores.
    """
    return []


def clusters(ctx: dict = None) -> list[dict]:
    """
    Returns incident clusters sharing beneficiaries, devices, or UPI roots.
    """
    return []
