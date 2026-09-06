import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Standard CUAD Legal Risk Archetypes for Sentence-BERT Semantic Vector Matching
CUAD_RISK_ARCHETYPES = [
    {
        "clause_type": "Indemnification & Defense Obligations",
        "category": "Unilateral Burden",
        "archetype": "Service provider shall indemnify, defend, and hold harmless client from any and all damages unbounded uncapped surviving perpetually",
        "base_severity": 0.96,
        "burdened_roles": ["Service Provider", "Receiving Party", "Employee", "Tenant"],
        "beneficiary_roles": ["Client / Buyer", "Disclosing Party", "Employer", "Landlord"],
        "default_rationale": "Exposes party to consequential, punitive, and indirect damages without aggregate limitation.",
        "suggested_redline": "direct damages awarded by a court of competent jurisdiction, subject to Limitation of Liability cap"
    },
    {
        "clause_type": "Invoicing, Payment Terms & Fee Withholding",
        "category": "Ambiguity Trap",
        "archetype": "Client shall pay invoices within ninety days and may withhold payment if client subjectively determines services do not meet satisfaction",
        "base_severity": 0.85,
        "burdened_roles": ["Service Provider", "Receiving Party", "Employee", "Tenant"],
        "beneficiary_roles": ["Client / Buyer", "Disclosing Party", "Employer", "Landlord"],
        "default_rationale": "Extended payment window combined with subjective withholding rights strains operational cash flow.",
        "suggested_redline": "within thirty (30) days based on objective written acceptance criteria"
    },
    {
        "clause_type": "Limitation of Liability & Liability Cap",
        "category": "Unilateral Burden",
        "archetype": "Client total aggregate liability shall be limited to five hundred dollars no liability cap applies to vendor",
        "base_severity": 0.92,
        "burdened_roles": ["Service Provider", "Receiving Party", "Employee", "Tenant"],
        "beneficiary_roles": ["Client / Buyer", "Disclosing Party", "Employer", "Landlord"],
        "default_rationale": "Asymmetric liability cap virtually eliminates Client accountability while leaving Provider liabilities uncapped.",
        "suggested_redline": "LIMITED TO THE TOTAL FEES PAID IN THE 12 MONTHS PRECEDING THE CLAIM"
    },
    {
        "clause_type": "Intellectual Property Rights & Background Assignment",
        "category": "Enforceability Issue",
        "archetype": "Irrevocably assigns all right title interest in deliverables work product including pre-existing background IP owned prior to contract",
        "base_severity": 0.95,
        "burdened_roles": ["Service Provider", "Receiving Party", "Employee", "Tenant"],
        "beneficiary_roles": ["Client / Buyer", "Disclosing Party", "Employer", "Landlord"],
        "default_rationale": "Forfeits foundational software tools, pre-existing code libraries, and background trade secrets.",
        "suggested_redline": "excluding Service Provider's pre-existing Background IP, for which Service Provider grants a non-exclusive license"
    },
    {
        "clause_type": "Restrictive Covenants & Non-Compete Scope",
        "category": "Enforceability Issue",
        "archetype": "Shall not directly or indirectly provide software development services for five years worldwide in technology sector",
        "base_severity": 0.88,
        "burdened_roles": ["Service Provider", "Receiving Party", "Employee", "Tenant"],
        "beneficiary_roles": ["Client / Buyer", "Disclosing Party", "Employer", "Landlord"],
        "default_rationale": "Unreasonable multi-year duration and global geographic scope function as an illegal restraint on trade.",
        "suggested_redline": "for a period of twelve (12) months limited to direct named competitors in North America"
    }
]

class EmbeddingsMatcherService:
    """
    Sentence-BERT / Legal-BERT Transformer Scoring Engine.
    Encodes contract text into vector embeddings and dynamically computes semantic hazard scores.
    """
    def __init__(self):
        self.model = None
        self._initialized = False

    def _lazy_init(self):
        if self._initialized:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self._initialized = True
            logger.info("SentenceTransformers vector embeddings model initialized.")
        except Exception as e:
            logger.warning(f"SentenceTransformers fallback to keyword matrix matcher: {e}")
            self.model = None
            self._initialized = True

    def compute_transformer_hazard(self, clause_text: str, role: str) -> Optional[Dict[str, Any]]:
        self._lazy_init()
        if not clause_text.strip():
            return None

        best_match = None
        highest_sim = 0.0

        if self.model:
            try:
                from sentence_transformers import util
                clause_emb = self.model.encode(clause_text, convert_to_tensor=True)
                archetype_texts = [a["archetype"] for a in CUAD_RISK_ARCHETYPES]
                archetype_embs = self.model.encode(archetype_texts, convert_to_tensor=True)
                
                cosine_scores = util.cos_sim(clause_emb, archetype_embs)[0]
                best_idx = int(cosine_scores.argmax())
                highest_sim = float(cosine_scores[best_idx])
                
                if highest_sim > 0.40:
                    best_match = CUAD_RISK_ARCHETYPES[best_idx].copy()
            except Exception as e:
                logger.error(f"Transformer embedding error: {e}")

        # Fallback to lexical similarity if transformer pipeline unavailable
        if not best_match:
            clause_lower = clause_text.lower()
            for archetype in CUAD_RISK_ARCHETYPES:
                keywords = archetype["archetype"].split()
                matches = sum(1 for kw in keywords if kw in clause_lower)
                sim = matches / len(keywords)
                if sim > highest_sim and matches >= 3:
                    highest_sim = sim
                    best_match = archetype.copy()

        if not best_match or highest_sim < 0.25:
            return None

        # DYNAMIC TRANSFORMER HAZARD SCORE FORMULA
        # 1. Base semantic hazard = Similarity * BaseSeverity * 100
        raw_hazard = min(99.0, max(15.0, highest_sim * best_match["base_severity"] * 120.0))

        # 2. Party Perspective Conditioning Matrix
        if role in best_match["burdened_roles"]:
            dynamic_hazard = int(round(raw_hazard))
            impact = "Predatory" if dynamic_hazard >= 85 else "Unfavorable"
        else:
            # Beneficiary party receives low hazard for favorable terms
            dynamic_hazard = max(10, int(round(raw_hazard * 0.22)))
            impact = "Favorable"

        return {
            "clause_type": best_match["clause_type"],
            "category": best_match["category"],
            "similarity_score": round(highest_sim, 3),
            "hazard_score_pct": dynamic_hazard,
            "impact": impact,
            "rationale": best_match["default_rationale"],
            "suggested_redline": best_match["suggested_redline"]
        }
