"""
Layer 3: ML Risk Scorer (core/ml.py)

Mock implementation for initial pipeline testing.
Returns a default risk probability of 0.5.
"""


def predict(account_id: str, ctx: dict = None) -> dict:
    """
    Predict risk probability for an account using ML features.

    Returns:
        {
            'score': float,  # probability 0..1
            'top_features': [(str, float), ...],
            'confidence': 'low' | 'normal'
        }
    """
    return {
        "score": 0.5,
        "top_features": [
            ("txn_count_24h", 0.42),
            ("in_out_ratio_24h", 0.28),
            ("shared_device_count", 0.18),
        ],
        "confidence": "normal",
    }
