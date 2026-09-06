import uuid
import json
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

    def evaluate_document(self, fitz_doc, full_text_data: List[Dict[str, Any]], filename: str, selected_role: str = "Service Provider", user_contract_type: Optional[str] = None) -> DocumentAuditResponse:
        full_doc_text = " ".join([p["text"] for p in full_text_data]).lower()
        
        # 1. Determine or override contract_type
        if user_contract_type and user_contract_type != "Auto-Detect":
            contract_type = user_contract_type
        elif "lease" in full_doc_text or "rent" in full_doc_text or "landlord" in full_doc_text or "tenant" in full_doc_text:
            contract_type = "Lease Agreement"
        elif "master services agreement" in full_doc_text or "services agreement" in full_doc_text:
            contract_type = "Master Services Agreement"
        elif "non-disclosure" in full_doc_text or "confidentiality" in full_doc_text:
            contract_type = "Non-Disclosure Agreement"
        elif "contractor" in full_doc_text or "consulting agreement" in full_doc_text or "employment" in full_doc_text:
            contract_type = "Employment Agreement"
        else:
            contract_type = "Commercial Contract"

        clauses = []
        gemini_summary = None
        
        # 2. Gemini LLM Reasoning if API key is configured
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_KEY_HERE":
            try:
                llm_res = self._evaluate_with_gemini(full_doc_text, selected_role, contract_type, fitz_doc)
                if llm_res and llm_res.get("clauses"):
                    clauses = llm_res["clauses"]
                    gemini_summary = llm_res.get("summary_of_findings")
                    logger.info("Successfully evaluated document using Google Gemini LLM.")
            except Exception as e:
                logger.error(f"Gemini LLM evaluation failed, falling back to Sentence-BERT embeddings engine: {e}")

        # 3. Fallback to Sentence-BERT Vector Embeddings Scorer
        if not clauses:
            clauses = self._evaluate_with_transformer_embeddings(fitz_doc, full_doc_text, full_text_data, selected_role, contract_type)

        all_spans = [span for clause in clauses for span in clause.identified_spans]
        high_risk_count = sum(1 for span in all_spans if span.risk_score_pct >= 70)
        
        overall_score = RiskScorerService.calculate_contract_safety_score(all_spans)
        
        if not gemini_summary:
            summary = self._generate_executive_summary(selected_role, contract_type, overall_score, clauses, high_risk_count)
        else:
            summary = gemini_summary

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

    def _evaluate_with_gemini(self, text: str, role: str, contract_type: str, fitz_doc) -> Dict[str, Any]:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
You are a senior contract attorney auditing a {contract_type} from the perspective of **{role}**.
Analyze the contract text below and return a JSON object containing your executive summary and clause risk audits.
Return ONLY valid JSON matching this schema exactly:

{{
  "summary_of_findings": "Comprehensive 2-sentence attorney executive summary explaining the main risks or protections for {role} (Overall Safety Score context).",
  "clauses": [
    {{
      "clause_title": "Indemnification & Defense Obligations",
      "raw_text": "Exact text excerpt of the clause from the contract",
      "impact": "Predatory",
      "strategic_takeaway": "Specific strategic legal advice for {role}",
      "missing_protections": ["Protection 1", "Protection 2"],
      "identified_spans": [
        {{
          "target_text": "exact sub-phrase quoted from the text",
          "risk_score_pct": 92,
          "risk_level": "Critical",
          "category": "Unilateral Burden",
          "rationale": "Legal rationale why this phrase is hazardous",
          "suggested_replacement": "Proposed redline replacement text"
        }}
      ]
    }}
  ]
}}

Contract Text Excerpt:
{text[:8000]}
"""
        response = model.generate_content(prompt)
        res_text = response.text.strip()
        if res_text.startswith("```json"):
            res_text = res_text[7:]
        if res_text.startswith("```"):
            res_text = res_text[3:]
        if res_text.endswith("```"):
            res_text = res_text[:-3]
        res_text = res_text.strip()

        parsed = json.loads(res_text)
        clauses = []

        for item in parsed.get("clauses", []):
            spans = []
            for span_data in item.get("identified_spans", []):
                target_text = span_data.get("target_text", "").strip()
                if not target_text:
                    continue
                bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_text)
                spans.append(IdentifiedSpan(
                    span_id=f"spn_{uuid.uuid4().hex[:6]}",
                    target_text=target_text,
                    bbox=bbox,
                    risk_score_pct=int(span_data.get("risk_score_pct", 75)),
                    risk_level=span_data.get("risk_level", "High"),
                    category=span_data.get("category", "Unilateral Burden"),
                    rationale=span_data.get("rationale", ""),
                    suggested_replacement=span_data.get("suggested_replacement", "")
                ))

            if spans or item.get("raw_text"):
                page_num = spans[0].bbox.page if spans else 1
                clauses.append(ClauseAudit(
                    clause_id=f"cls_{uuid.uuid4().hex[:6]}",
                    clause_title=item.get("clause_title", "Contract Provision"),
                    raw_text=item.get("raw_text", ""),
                    page_number=page_num,
                    party_perspective=role,
                    impact=item.get("impact", "Unfavorable"),
                    strategic_takeaway=item.get("strategic_takeaway", ""),
                    missing_protections=item.get("missing_protections", []),
                    identified_spans=spans
                ))

        return {
            "summary_of_findings": parsed.get("summary_of_findings", ""),
            "clauses": clauses
        }

    def _evaluate_with_transformer_embeddings(self, fitz_doc, full_text: str, full_text_data: List[Dict[str, Any]], role: str, contract_type: str) -> List[ClauseAudit]:
        clauses = []

        # 1. Scan text blocks from PyMuPDF
        text_blocks = []
        for page in full_text_data:
            for b in page.get("blocks", []):
                txt = b.get("text", "").strip()
                if len(txt) > 30:
                    text_blocks.append((txt, page.get("page_number", 1)))

        # 2. Key phrase candidates for coordinate search
        candidates = [
            ("any and all damages", "Indemnification & Defense Obligations"),
            ("within ninety (90) days", "Invoicing, Payment Terms & Fee Withholding"),
            ("LIMITED TO $500", "Limitation of Liability & Liability Cap"),
            ("pre-existing background IP", "Intellectual Property Rights & Background Assignment"),
            ("period of five (5) years", "Restrictive Covenants & Non-Compete Scope"),
            ("retain the entire security deposit", "Security Deposit & Forfeiture Terms"),
            ("solely responsible for all routine and structural repairs", "Property Maintenance & Structural Repair Duties"),
            ("enter the premises at any time without prior written notice", "Unilateral Entry & Short Eviction Notice")
        ]

        # First evaluate text blocks dynamically
        seen_titles = set()

        for raw_block_text, p_num in text_blocks:
            transformer_res = self.embeddings_matcher.compute_transformer_hazard(raw_block_text, role)
            if transformer_res and transformer_res["clause_type"] not in seen_titles:
                clause_title = transformer_res["clause_type"]
                seen_titles.add(clause_title)
                
                # Find matching target phrase snippet
                target_phrase = raw_block_text[:40]
                for kw, title in candidates:
                    if kw.lower() in raw_block_text.lower():
                        target_phrase = kw
                        break

                bbox = CoordinateMapperService.find_phrase_bbox(fitz_doc, target_phrase, preferred_page=p_num)
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
                    missing_prots = ["Mutual indemnification for Client IP infringement and breach", "Exclusion of indirect damages"]
                elif "Payment" in clause_title:
                    missing_prots = ["Standard 30-day payment timeline", "Late payment interest penalty"]
                elif "Liability" in clause_title:
                    missing_prots = ["Mutual aggregate liability cap equal to total contract value"]
                elif "Intellectual" in clause_title:
                    missing_prots = ["Carve-out preserving pre-existing Background IP"]
                elif "Security Deposit" in clause_title:
                    missing_prots = ["Statutory 30-day return window", "Mandatory itemized receipt accounting"]
                elif "Maintenance" in clause_title:
                    missing_prots = ["Landlord statutory obligation for structural repairs"]
                elif "Entry" in clause_title:
                    missing_prots = ["Mandatory 24-hour advance written notice prior to entry"]
                else:
                    missing_prots = ["Narrowing non-compete to specific direct competitors"]

                clauses.append(ClauseAudit(
                    clause_id=f"cls_{uuid.uuid4().hex[:6]}",
                    clause_title=clause_title,
                    raw_text=raw_block_text[:300],
                    page_number=p_num,
                    party_perspective=role,
                    impact=transformer_res["impact"],
                    strategic_takeaway=f"As {role}: {transformer_res['rationale']}",
                    missing_protections=missing_prots,
                    identified_spans=[span]
                ))

        return clauses

    def _generate_executive_summary(self, role: str, contract_type: str, score: int, clauses: List[ClauseAudit], high_risk_count: int) -> str:
        if role in ["Service Provider", "Receiving Party", "Employee", "Tenant"]:
            if high_risk_count > 0:
                return (
                    f"Contract review of this {contract_type} from your perspective as {role} reveals significant legal exposure "
                    f"(Overall Safety Score: {score}/100). The agreement contains {high_risk_count} critical risk provisions that require redlining prior to execution."
                )
            else:
                return (
                    f"Contract review of this {contract_type} from your perspective as {role} indicates moderate protection "
                    f"(Overall Safety Score: {score}/100). Essential terms are mostly balanced, but minor ambiguities should be clarified."
                )
        else:
            return (
                f"Contract review of this {contract_type} from your perspective as {role} indicates favorable terms "
                f"(Overall Safety Score: {score}/100). The agreement strongly protects your interests."
            )
