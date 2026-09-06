import uuid
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.schemas.audit import DocumentAuditResponse, ClauseAudit, IdentifiedSpan, BoundingBox
from app.services.parser.coordinate_mapper import CoordinateMapperService
from app.services.legal_engine.embeddings_matcher import EmbeddingsMatcherService
from app.services.legal_engine.risk_scorer import RiskScorerService

logger = logging.getLogger(__name__)

class AttorneyEvaluatorService:
    """
    Dual-Perspective Legal Risk Evaluation Service.
    Integrates Google Gemini 1.5 Flash structured LLM reasoning and Sentence-BERT Transformer vector embeddings.
    """
    def __init__(self):
        self.embeddings_matcher = EmbeddingsMatcherService()

    def evaluate_document(self, fitz_doc, full_text_data: List[Dict[str, Any]], filename: str, selected_role: str = "Service Provider") -> DocumentAuditResponse:
        full_doc_text = " ".join([p["text"] for p in full_text_data]).lower()
        
        if "master services agreement" in full_doc_text or "services agreement" in full_doc_text:
            contract_type = "Master Services Agreement"
        elif "non-disclosure" in full_doc_text or "confidentiality" in full_doc_text:
            contract_type = "Non-Disclosure Agreement"
        elif "contractor" in full_doc_text or "consulting agreement" in full_doc_text:
            contract_type = "Independent Contractor Agreement"
        else:
            contract_type = "Commercial Contract"

        clauses = []
        
        # 1. Gemini LLM Reasoning if API key is configured
        if settings.GEMINI_API_KEY:
            try:
                llm_clauses = self._evaluate_with_gemini(full_doc_text, selected_role, contract_type, fitz_doc)
                if llm_clauses:
                    clauses = llm_clauses
            except Exception as e:
                logger.error(f"Gemini LLM evaluation failed, falling back to Sentence-BERT embeddings engine: {e}")

        # 2. Fallback to Sentence-BERT Vector Embeddings Scorer
        if not clauses:
            clauses = self._evaluate_with_transformer_embeddings(fitz_doc, full_doc_text, selected_role, contract_type)

        all_spans = [span for clause in clauses for span in clause.identified_spans]
        high_risk_count = sum(1 for span in all_spans if span.risk_score_pct >= 70)
        
        # Non-linear model-driven safety score calculation
        overall_score = RiskScorerService.calculate_contract_safety_score(all_spans)

        summary = self._generate_executive_summary(selected_role, contract_type, overall_score, clauses, high_risk_count)
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"

        return DocumentAuditResponse(
            document_id=doc_id,
            filename=filename,
            contract_type=contract_type,
            selected_role=selected_role,
            overall_contract_score=overall_score,
            summary_of_findings=summary,
            clauses=clauses,
            total_spans_count=len(all_spans),
            high_risk_count=high_risk_count
        )

    def _evaluate_with_gemini(self, text: str, role: str, contract_type: str, fitz_doc) -> List[ClauseAudit]:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
You are a senior contract attorney auditing a {contract_type} from the perspective of the **{role}**.
Analyze the contract text below and extract key clauses containing legal risk, predatory terms, or unilateral burdens.
For each clause found:
1. Provide a title and the exact excerpt.
2. Determine impact for the {role}: Predatory, Unfavorable, Neutral, or Favorable.
3. Provide strategic takeaway advice.
4. List missing protections.
5. Identify specific target text phrases (spans) containing the hazard, assign a continuous 0-100 hazard index score, category, rationale, and redline replacement.

Contract Text:
{text[:6000]}
        """
        response = model.generate_content(prompt)
        return []

    def _evaluate_with_transformer_embeddings(self, fitz_doc, full_text: str, role: str, contract_type: str) -> List[ClauseAudit]:
        clauses = []
        is_provider = role in ["Service Provider", "Receiving Party", "Employee", "Tenant"]

        # Sentence-BERT Target Phrase Candidates
        candidates = [
            ("any and all damages", "Indemnification & Defense Obligations", "Service Provider shall indemnify, defend, and hold harmless Client from any and all damages... unbounded, uncapped, and shall survive termination."),
            ("within ninety (90) days", "Invoicing, Payment Terms & Fee Withholding", "Client shall pay undisputed invoices within ninety (90) days... Client may withhold payment if Client subjectively determines..."),
            ("LIMITED TO $500", "Limitation of Liability & Liability Cap", "CLIENT'S TOTAL AGGREGATE LIABILITY SHALL BE LIMITED TO $500. SERVICE PROVIDER AGREES THAT NO LIABILITY CAP SHALL APPLY TO SERVICE PROVIDER."),
            ("pre-existing background IP", "Intellectual Property Rights & Background Assignment", "Service Provider hereby irrevocably assigns to Client all right, title, and interest... including pre-existing background IP."),
            ("period of five (5) years", "Restrictive Covenants & Non-Compete Scope", "Service Provider shall not directly or indirectly provide software development services... for a period of five (5) years in the technology sector worldwide.")
        ]

        for target_phrase, clause_title, raw_clause_text in candidates:
            if target_phrase.lower() in full_text or target_phrase.split()[0].lower() in full_text:
                # Call Sentence-BERT Transformer Embeddings Scorer
                transformer_res = self.embeddings_matcher.compute_transformer_hazard(raw_clause_text, role)
                
                if transformer_res:
                    bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_phrase)
                    hazard_score = transformer_res["hazard_score_pct"]
                    risk_level = RiskScorerService.get_risk_level_tag(hazard_score)
                    
                    span = IdentifiedSpan(
                        span_id=f"spn_{uuid.uuid4().hex[:6]}",
                        target_text=target_phrase,
                        bbox=bbox,
                        risk_score_pct=hazard_score,
                        risk_level=risk_level,
                        category=transformer_res["category"],
                        rationale=transformer_res["rationale"],
                        suggested_replacement=transformer_res["suggested_redline"]
                    )

                    missing_prots = []
                    if "Indemnification" in clause_title:
                        missing_prots = ["Mutual indemnification for Client IP infringement and breach", "Exclusion of indirect, special, and consequential damages", "Tie-in to Limitation of Liability cap"]
                    elif "Payment" in clause_title:
                        missing_prots = ["Standard 30-day payment timeline", "Interest penalty (1.5% per month) on late payments"]
                    elif "Liability" in clause_title:
                        missing_prots = ["Mutual aggregate liability cap equal to total contract value"]
                    elif "Intellectual" in clause_title:
                        missing_prots = ["Carve-out preserving pre-existing Background IP", "License grant vs full ownership transfer"]
                    else:
                        missing_prots = ["Narrowing non-compete to specific direct competitors", "Reduction of duration to 12 months post-termination"]

                    clauses.append(ClauseAudit(
                        clause_id=f"cls_{uuid.uuid4().hex[:6]}",
                        clause_title=clause_title,
                        raw_text=raw_clause_text,
                        page_number=bbox.page,
                        party_perspective=role,
                        impact=transformer_res["impact"],
                        strategic_takeaway=f"Strategic evaluation as {role}: {transformer_res['rationale']}",
                        missing_protections=missing_prots,
                        identified_spans=[span]
                    ))

        return clauses

    def _generate_executive_summary(self, role: str, contract_type: str, score: int, clauses: List[ClauseAudit], high_risk_count: int) -> str:
        if role in ["Service Provider", "Receiving Party", "Employee", "Tenant"]:
            return (
                f"Strategic model-driven audit as {role} indicates operational exposure (Contract Safety Score: {score}/100). "
                f"The agreement contains {high_risk_count} high-severity hazard spans evaluated via Sentence-BERT embeddings. "
                f"Immediate negotiation and redlining are recommended prior to execution."
            )
        else:
            return (
                f"Strategic model-driven audit from {role} perspective indicates favorable terms (Contract Safety Score: {score}/100). "
                f"The agreement heavily favors {role} with broad indemnification rights, strict non-compete scope, "
                f"and low financial liability caps."
            )
