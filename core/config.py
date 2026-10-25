"""
Configuration settings for the Bihar Cyber Fraud Detection Engine.
"""

FUSION_WEIGHTS = {
    "rule": 0.20,
    "baseline": 0.20,
    "ml": 0.35,
    "complaint": 0.15,
    "graph": 0.10,
}

TIER_THRESHOLDS = {
    "CRITICAL": 80.0,
    "HIGH": 60.0,
    "MEDIUM": 40.0,
    "LOW": 0.0,
}

MAX_HOPS = 5
TXN_WINDOW_HOURS = 24
BASELINE_DAYS = 90
