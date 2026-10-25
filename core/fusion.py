"""
Layer 6: Fusion & Risk Scoring Engine (core/fusion.py)

Fuses signals from all 5 detection layers into a unified 0-100 risk score:
    Score = 0.20(Rules) + 0.20(Baseline) + 0.35(ML) + 0.15(Complaint) + 0.10(Graph)

Produces:
- score: float (0.0 to 100.0)
- tier: 'CRITICAL' (>= 80) | 'HIGH' (>= 60) | 'MEDIUM' (>= 40) | 'LOW' (< 40)
- contributions: breakdown of each layer's score (0.0 to 1.0)
- confidence: 'normal' | 'low' (inherited from cold-start baseline)
- explanation: Human-readable composite explanation of primary risk drivers

Matches specifications in docs/09-DETECTION-PIPELINE.md and docs/07-TECHNICAL-SPECIFICATION.md.
"""

from core.config import FUSION_WEIGHTS, TIER_THRESHOLDS
from core import rules
from core import baseline
from core import ml
from core import complaints
from core import graph_ops


def tier_of(final_score: float) -> str:
    """Determine risk tier from final 0-100 score."""
    if final_score >= TIER_THRESHOLDS.get("CRITICAL", 80.0):
        return "CRITICAL"
    elif final_score >= TIER_THRESHOLDS.get("HIGH", 60.0):
        return "HIGH"
    elif final_score >= TIER_THRESHOLDS.get("MEDIUM", 40.0):
        return "MEDIUM"
    return "LOW"


def score(account_id: str, ctx: dict = None) -> dict:
    """
    Compute fused risk score and detailed layer contributions for an account.

    Parameters:
        account_id: Target account ID (e.g. 'ACC-22451')
        ctx: Shared data context containing DataFrames

    Returns:
        {
            'score': float,              # 0.0 to 100.0
            'tier': str,                # 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
            'contributions': {
                'rule': float,
                'baseline': float,
                'ml': float,
                'complaint': float,
                'graph': float
            },
            'confidence': 'normal' | 'low',
            'explanation': str,
            'rule_details': dict,
            'baseline_details': dict
        }
    """
    if ctx is None:
        ctx = {}

    as_of = ctx.get("as_of")

    # 1. Layer 1: Rules Engine (12 RBI Red-Flags)
    rule_res = rules.evaluate(account_id, ctx=ctx)
    rule_score = float(rule_res.get("score", 0.0))

    # 2. Layer 2: Baseline Deviation Engine (90-day z-scores)
    baseline_res = baseline.deviation(account_id, as_of=as_of, ctx=ctx)
    baseline_score = float(baseline_res.get("score", 0.0))
    confidence = baseline_res.get("confidence", "normal")

    # 3. Layer 3: ML Risk Scorer (Mocked / trained model)
    ml_res = ml.predict(account_id, ctx=ctx)
    if isinstance(ml_res, dict):
        ml_score = float(ml_res.get("score", 0.5))
    else:
        ml_score = float(ml_res)

    # 4. Layer 4: Complaint Correlator (Mocked / entity match)
    complaint_res = complaints.score(account_id, ctx=ctx)
    complaint_score = float(complaint_res)

    # 5. Layer 5: Graph Operations (Mocked / BFS & community)
    graph_res = graph_ops.ring_risk(account_id, ctx=ctx)
    graph_score = float(graph_res)

    # Individual normalized contributions (0.0 to 1.0)
    contributions = {
        "rule": round(rule_score, 4),
        "baseline": round(baseline_score, 4),
        "ml": round(ml_score, 4),
        "complaint": round(complaint_score, 4),
        "graph": round(graph_score, 4),
    }

    # Exact weighted fusion formula:
    # Score = 0.20(Rules) + 0.20(Baseline) + 0.35(ML) + 0.15(Complaint) + 0.10(Graph)
    raw_score = sum(FUSION_WEIGHTS[layer] * contributions[layer] for layer in FUSION_WEIGHTS)

    # Scale to 0 - 100
    final_score = round(raw_score * 100.0, 1)
    tier = tier_of(final_score)

    # Construct composite explanation
    fired_rule_names = [f["rule"] for f in rule_res.get("fired", [])]
    explanation_parts = []

    if fired_rule_names:
        explanation_parts.append(f"Rules fired: {', '.join(fired_rule_names[:4])}")
    if baseline_res.get("z_amt", 0.0) >= 3.0 or baseline_res.get("z_freq", 0.0) >= 3.0:
        explanation_parts.append(baseline_res.get("explanation", ""))
    if not explanation_parts:
        explanation_parts.append("Normal activity within baseline boundaries.")

    composite_explanation = " | ".join(filter(None, explanation_parts))

    return {
        "score": final_score,
        "tier": tier,
        "contributions": contributions,
        "confidence": confidence,
        "explanation": composite_explanation,
        "rule_details": rule_res,
        "baseline_details": baseline_res,
    }
