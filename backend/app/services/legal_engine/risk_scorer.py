import math
from typing import List
from app.schemas.audit import IdentifiedSpan

class RiskScorerService:
    """
    Model-driven non-linear Risk Scorer.
    Uses exponential decay functions to prevent score dilution and accurately weight critical hazards.
    """
    @staticmethod
    def calculate_contract_safety_score(spans: List[IdentifiedSpan]) -> int:
        if not spans:
            return 90

        # Weighted hazard accumulation:
        # Critical hazards (>=70%) carry higher weight (2.5x) to prevent score dilution by minor clauses
        total_weighted_hazard = 0.0
        total_weights = 0.0

        for span in spans:
            hazard = float(span.risk_score_pct)
            weight = 2.5 if hazard >= 70.0 else (1.5 if hazard >= 40.0 else 1.0)
            total_weighted_hazard += hazard * weight
            total_weights += weight

        if total_weights == 0:
            return 85

        effective_hazard = total_weighted_hazard / total_weights
        critical_count = sum(1 for span in spans if span.risk_score_pct >= 70)

        # Exponential decay formula for Contract Safety (100 = perfectly safe, 5 = highly predatory)
        # Safety = 100 * exp(- (EffectiveHazard * 0.008 + CriticalCount * 0.12))
        exponent = (effective_hazard * 0.0085) + (critical_count * 0.14)
        safety_score = int(round(100.0 * math.exp(-exponent)))

        return max(5, min(99, safety_score))

    @staticmethod
    def get_risk_level_tag(score_pct: int) -> str:
        if score_pct >= 80:
            return "Critical"
        elif score_pct >= 60:
            return "High"
        elif score_pct >= 40:
            return "Medium"
        return "Low"
