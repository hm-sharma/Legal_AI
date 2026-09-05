from typing import List
from app.schemas.audit import IdentifiedSpan

class RiskScorerService:
    """
    Computes hazard index scores (0-100), risk levels (Critical, High, Medium, Low),
    and aggregate contract safety scores.
    """
    @staticmethod
    def calculate_contract_safety_score(spans: List[IdentifiedSpan]) -> int:
        if not spans:
            return 85
        high_risk_count = sum(1 for span in spans if span.risk_score_pct >= 70)
        avg_risk = sum(span.risk_score_pct for span in spans) / len(spans)
        overall_score = max(5, int(100 - (avg_risk * 0.65) - (high_risk_count * 4)))
        return overall_score

    @staticmethod
    def get_risk_level_tag(score: int) -> str:
        if score >= 80:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        return "Low"
