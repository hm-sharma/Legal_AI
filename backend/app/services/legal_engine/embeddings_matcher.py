import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Standard CUAD Legal Risk Archetypes for Semantic Similarity Search
CUAD_RISK_ARCHETYPES = [
    {
        "category": "Unilateral Burden",
        "archetype": "Service provider shall indemnify, defend, and hold harmless client from all damages unbounded uncapped",
        "risk_type": "Indemnification & Defense Obligations"
    },
    {
        "category": "Ambiguity Trap",
        "archetype": "Client may withhold payment if client subjectively determines services do not meet satisfaction within 90 days",
        "risk_type": "Payment Terms & Fee Withholding"
    },
    {
        "category": "Unilateral Burden",
        "archetype": "Total aggregate liability shall be limited to 500 dollars no liability cap applies to vendor",
        "risk_type": "Limitation of Liability"
    },
    {
        "category": "Enforceability Issue",
        "archetype": "Irrevocably assigns all right title interest including pre-existing background IP owned prior to effective date",
        "risk_type": "Intellectual Property Rights"
    },
    {
        "category": "Enforceability Issue",
        "archetype": "Shall not directly or indirectly provide services for five years worldwide",
        "risk_type": "Restrictive Covenants & Non-Compete"
    }
]

class EmbeddingsMatcherService:
    """
    Computes semantic similarity embeddings between contract text and standard CUAD legal risk categories.
    Lazy-loads sentence-transformers if available.
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
            logger.info("SentenceTransformers model initialized successfully.")
        except Exception as e:
            logger.warning(f"SentenceTransformers not loaded, falling back to substring/jaccard matcher: {e}")
            self.model = None
            self._initialized = True

    def find_matching_archetype(self, clause_text: str) -> Optional[Dict[str, Any]]:
        self._lazy_init()
        if not clause_text.strip():
            return None

        if self.model:
            try:
                from sentence_transformers import util
                clause_emb = self.model.encode(clause_text, convert_to_tensor=True)
                archetype_texts = [a["archetype"] for a in CUAD_RISK_ARCHETYPES]
                archetype_embs = self.model.encode(archetype_texts, convert_to_tensor=True)
                
                cosine_scores = util.cos_sim(clause_emb, archetype_embs)[0]
                best_idx = int(cosine_scores.argmax())
                best_score = float(cosine_scores[best_idx])
                
                if best_score > 0.45:
                    match = CUAD_RISK_ARCHETYPES[best_idx].copy()
                    match["similarity_score"] = best_score
                    return match
            except Exception as e:
                logger.error(f"Embedding computation error: {e}")

        # Fallback keyword match
        clause_lower = clause_text.lower()
        for archetype in CUAD_RISK_ARCHETYPES:
            keywords = archetype["archetype"].split()
            matches = sum(1 for kw in keywords if kw in clause_lower)
            if matches >= 3:
                match = archetype.copy()
                match["similarity_score"] = 0.5
                return match

        return None
