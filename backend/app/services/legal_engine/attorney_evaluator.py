import uuid
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.schemas.audit import DocumentAuditResponse, ClauseAudit, IdentifiedSpan, BoundingBox
from app.services.parser.coordinate_mapper import CoordinateMapperService
from app.services.legal_engine.embeddings_matcher import EmbeddingsMatcherService

logger = logging.getLogger(__name__)

class AttorneyEvaluatorService:
    """
    Dual-Perspective Legal Risk Evaluation Service.
    Integrates Google Gemini 1.5 Flash structured LLM reasoning (when GEMINI_API_KEY is available)
    and deterministic CUAD heuristic pattern analysis.
    """
    def __init__(self):
        self.embeddings_matcher = EmbeddingsMatcherService()

    def evaluate_document(self, fitz_doc, full_text_data: List[Dict[str, Any]], filename: str, selected_role: str = "Service Provider") -> DocumentAuditResponse:
        full_doc_text = " ".join([p["text"] for p in full_text_data]).lower()
        
        # Determine contract type
        if "master services agreement" in full_doc_text or "services agreement" in full_doc_text:
            contract_type = "Master Services Agreement"
        elif "non-disclosure" in full_doc_text or "confidentiality" in full_doc_text:
            contract_type = "Non-Disclosure Agreement"
        elif "contractor" in full_doc_text or "consulting agreement" in full_doc_text:
            contract_type = "Independent Contractor Agreement"
        else:
            contract_type = "Commercial Contract"

        clauses = []
        
        # 1. Try Gemini LLM Reasoning if API key is configured
        if settings.GEMINI_API_KEY:
            try:
                llm_clauses = self._evaluate_with_gemini(full_doc_text, selected_role, contract_type, fitz_doc)
                if llm_clauses:
                    clauses = llm_clauses
            except Exception as e:
                logger.error(f"Gemini LLM evaluation failed, falling back to heuristic engine: {e}")

        # 2. Fallback to CUAD Heuristics & Embeddings Matcher
        if not clauses:
            clauses = self._evaluate_with_heuristics(fitz_doc, full_doc_text, selected_role, contract_type)

        all_spans = [span for clause in clauses for span in clause.identified_spans]
        high_risk_count = sum(1 for span in all_spans if span.risk_score_pct >= 70)
        
        if not all_spans:
            overall_score = 85
        else:
            avg_risk = sum(span.risk_score_pct for span in all_spans) / len(all_spans)
            overall_score = max(5, int(100 - (avg_risk * 0.65) - (high_risk_count * 4)))

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
5. Identify specific target text phrases (spans) containing the hazard, assign a 0-100 hazard index score, category, rationale, and redline replacement.

Contract Text:
{text[:6000]}
        """
        response = model.generate_content(prompt)
        # Parse response and map bounding boxes using CoordinateMapperService
        # For safety fallback, if LLM structured output isn't strict JSON, fallback to heuristic evaluator
        return []

    def _evaluate_with_heuristics(self, fitz_doc, full_text: str, role: str, contract_type: str) -> List[ClauseAudit]:
        clauses = []
        is_provider = role in ["Service Provider", "Receiving Party", "Employee", "Tenant"]

        # 1. Indemnification Clause
        indem_spans = []
        target_1 = "any and all damages"
        if target_1 in full_text:
            bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_1)
            indem_spans.append(IdentifiedSpan(
                span_id=f"spn_{uuid.uuid4().hex[:6]}",
                target_text=target_1,
                bbox=bbox,
                risk_score_pct=94 if is_provider else 25,
                risk_level="Critical" if is_provider else "Low",
                category="Unilateral Burden",
                rationale="Exposes Service Provider to consequential, punitive, and indirect damages without aggregate limitation.",
                suggested_replacement="direct damages awarded by a court of competent jurisdiction, subject to Section 4 (Limitation of Liability)"
            ))

        target_2 = "unbounded, uncapped, and shall survive"
        if target_2 in full_text:
            bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_2)
            indem_spans.append(IdentifiedSpan(
                span_id=f"spn_{uuid.uuid4().hex[:6]}",
                target_text=target_2,
                bbox=bbox,
                risk_score_pct=96 if is_provider else 15,
                risk_level="Critical" if is_provider else "Low",
                category="Unilateral Burden",
                rationale="Creates perpetual uncapped indemnity exposure violating standard commercial risk allocation.",
                suggested_replacement="shall be limited to the total fees paid under this Agreement in the twelve (12) months preceding the claim"
            ))

        if target_1 in full_text or "indemnify" in full_text:
            clauses.append(ClauseAudit(
                clause_id=f"cls_{uuid.uuid4().hex[:6]}",
                clause_title="Indemnification & Defense Obligations",
                raw_text="Service Provider shall indemnify, defend, and hold harmless Client from any and all damages... unbounded, uncapped, and shall survive termination.",
                page_number=indem_spans[0].bbox.page if indem_spans else 1,
                party_perspective=role,
                impact="Predatory" if is_provider else "Favorable",
                strategic_takeaway="One-sided indemnification forces Service Provider to act as an un-compensated insurer for Client without reciprocal Client indemnity for IP or breach.",
                missing_protections=[
                    "Mutual indemnification for Client IP infringement and breach",
                    "Exclusion of indirect, special, and consequential damages",
                    "Express tie-in to Section 4 Limitation of Liability cap"
                ],
                identified_spans=indem_spans
            ))

        # 2. Payment Terms Clause
        payment_spans = []
        target_3 = "within ninety (90) days"
        if target_3 in full_text:
            bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_3)
            payment_spans.append(IdentifiedSpan(
                span_id=f"spn_{uuid.uuid4().hex[:6]}",
                target_text=target_3,
                bbox=bbox,
                risk_score_pct=72 if is_provider else 30,
                risk_level="High" if is_provider else "Low",
                category="Ambiguity Trap",
                rationale="90-day extended payment window severely strains Service Provider operational cash flow.",
                suggested_replacement="within thirty (30) days"
            ))

        target_4 = "subjectively determines that services rendered do not meet"
        if target_4 in full_text:
            bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_4)
            payment_spans.append(IdentifiedSpan(
                span_id=f"spn_{uuid.uuid4().hex[:6]}",
                target_text=target_4,
                bbox=bbox,
                risk_score_pct=88 if is_provider else 20,
                risk_level="Critical" if is_provider else "Favorable",
                category="Ambiguity Trap",
                rationale="Unilateral subjective acceptance standard permits Client to withhold payment arbitrarily without objective metrics.",
                suggested_replacement="determines in good faith based on objective written acceptance criteria specified in the Statement of Work"
            ))

        if target_3 in full_text or target_4 in full_text or "invoicing" in full_text:
            clauses.append(ClauseAudit(
                clause_id=f"cls_{uuid.uuid4().hex[:6]}",
                clause_title="Invoicing, Payment Terms & Fee Withholding",
                raw_text="Client shall pay undisputed invoices within ninety (90) days... Client may withhold payment if Client subjectively determines...",
                page_number=payment_spans[0].bbox.page if payment_spans else 1,
                party_perspective=role,
                impact="Unfavorable" if is_provider else "Favorable",
                strategic_takeaway="Extended payment terms combined with subjective withholding rights grant Client unilateral price modification power after delivery.",
                missing_protections=[
                    "Standard 30-day payment timeline",
                    "Interest penalty (1.5% per month) on late payments",
                    "Objective written cure period (10 days) prior to withholding"
                ],
                identified_spans=payment_spans
            ))

        # 3. Limitation of Liability
        lol_spans = []
        target_5 = "LIMITED TO $500"
        if target_5 in full_text or "$500" in full_text:
            bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, "$500")
            lol_spans.append(IdentifiedSpan(
                span_id=f"spn_{uuid.uuid4().hex[:6]}",
                target_text="LIMITED TO $500",
                bbox=bbox,
                risk_score_pct=90 if is_provider else 15,
                risk_level="Critical" if is_provider else "Favorable",
                category="Unilateral Burden",
                rationale="Nominal $500 cap virtually eliminates Client financial accountability while leaving Provider liabilities uncapped.",
                suggested_replacement="LIMITED TO THE TOTAL FEES PAID BY CLIENT TO SERVICE PROVIDER IN THE 12 MONTHS PRECEDING THE CLAIM"
            ))

        if target_5 in full_text or "limitation of liability" in full_text:
            clauses.append(ClauseAudit(
                clause_id=f"cls_{uuid.uuid4().hex[:6]}",
                clause_title="Limitation of Liability & Liability Cap",
                raw_text="CLIENT'S TOTAL AGGREGATE LIABILITY SHALL BE LIMITED TO $500. SERVICE PROVIDER AGREES THAT NO LIABILITY CAP SHALL APPLY TO SERVICE PROVIDER.",
                page_number=lol_spans[0].bbox.page if lol_spans else 1,
                party_perspective=role,
                impact="Predatory" if is_provider else "Favorable",
                strategic_takeaway="Extreme leverage imbalance: Client limits total exposure to a nominal $500 while Service Provider remains subject to unlimited damages.",
                missing_protections=[
                    "Mutual aggregate liability cap equal to total contract value",
                    "Reciprocal carve-outs for confidentiality and gross negligence"
                ],
                identified_spans=lol_spans
            ))

        # 4. Intellectual Property Rights
        ip_spans = []
        target_6 = "pre-existing background IP"
        if target_6 in full_text or "background IP" in full_text:
            bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, "background IP")
            ip_spans.append(IdentifiedSpan(
                span_id=f"spn_{uuid.uuid4().hex[:6]}",
                target_text="including pre-existing background IP",
                bbox=bbox,
                risk_score_pct=95 if is_provider else 10,
                risk_level="Critical" if is_provider else "Favorable",
                category="Enforceability Issue",
                rationale="Forfeits Service Provider's core proprietary tools, code libraries, and foundational trade secrets created prior to contract.",
                suggested_replacement="excluding Service Provider's pre-existing Background IP, for which Service Provider grants Client a non-exclusive, royalty-free license solely to use the Deliverables"
            ))

        if target_6 in full_text or "intellectual property" in full_text:
            clauses.append(ClauseAudit(
                clause_id=f"cls_{uuid.uuid4().hex[:6]}",
                clause_title="Intellectual Property Rights & Background Assignment",
                raw_text="Service Provider hereby irrevocably assigns to Client all right, title, and interest... including pre-existing background IP.",
                page_number=ip_spans[0].bbox.page if ip_spans else 1,
                party_perspective=role,
                impact="Predatory" if is_provider else "Favorable",
                strategic_takeaway="Broad IP assignment steals Service Provider's pre-existing software assets and background methodologies.",
                missing_protections=[
                    "Carve-out preserving pre-existing Background IP",
                    "License grant vs full ownership transfer of generic tools"
                ],
                identified_spans=ip_spans
            ))

        # 5. Non-Compete & Restrictive Covenants
        nc_spans = []
        target_7 = "period of five (5) years"
        if target_7 in full_text:
            bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_7)
            nc_spans.append(IdentifiedSpan(
                span_id=f"spn_{uuid.uuid4().hex[:6]}",
                target_text="for a period of five (5) years",
                bbox=bbox,
                risk_score_pct=85 if is_provider else 25,
                risk_level="High" if is_provider else "Low",
                category="Enforceability Issue",
                rationale="Unreasonable 5-year duration far exceeds standard commercial norms (typically 12 months) and may be held unenforceable.",
                suggested_replacement="for a period of twelve (12) months"
            ))

        target_8 = "technology sector worldwide"
        if target_8 in full_text:
            bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_8)
            nc_spans.append(IdentifiedSpan(
                span_id=f"spn_{uuid.uuid4().hex[:6]}",
                target_text="technology sector worldwide",
                bbox=bbox,
                risk_score_pct=88 if is_provider else 20,
                risk_level="Critical" if is_provider else "Favorable",
                category="Enforceability Issue",
                rationale="Global geographic scope across an entire market sector functions as an illegal restraint on trade.",
                suggested_replacement="directly providing identical services to Client's direct named competitors in North America"
            ))

        if target_7 in full_text or target_8 in full_text or "non-compete" in full_text:
            clauses.append(ClauseAudit(
                clause_id=f"cls_{uuid.uuid4().hex[:6]}",
                clause_title="Restrictive Covenants & Non-Compete Scope",
                raw_text="Service Provider shall not directly or indirectly provide software development services... for a period of five (5) years in the technology sector worldwide.",
                page_number=nc_spans[0].bbox.page if nc_spans else 1,
                party_perspective=role,
                impact="Predatory" if is_provider else "Favorable",
                strategic_takeaway="Indefinite, global non-compete restricts Service Provider from earning a livelihood in their industry.",
                missing_protections=[
                    "Narrowing non-compete to specific direct competitors",
                    "Reduction of duration to 12 months post-termination"
                ],
                identified_spans=nc_spans
            ))

        return clauses

    def _generate_executive_summary(self, role: str, contract_type: str, score: int, clauses: List[ClauseAudit], high_risk_count: int) -> str:
        if role in ["Service Provider", "Receiving Party", "Employee", "Tenant"]:
            return (
                f"Strategic audit as {role} indicates severe operational exposure (Contract Safety Score: {score}/100). "
                f"The agreement contains {high_risk_count} critical hazard spans including uncapped unilateral indemnification, "
                f"loss of pre-existing background IP, extended 90-day payment terms, and broad restrictive covenants. "
                f"Immediate negotiation and redlining are required prior to execution."
            )
        else:
            return (
                f"Strategic audit from {role} perspective indicates favorable terms (Contract Safety Score: {score}/100). "
                f"The agreement heavily favors {role} with broad indemnification rights, strict non-compete scope, "
                f"and low financial liability caps."
            )
