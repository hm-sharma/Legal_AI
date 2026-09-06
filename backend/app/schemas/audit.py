from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    page: int = Field(..., description="1-indexed page number")
    x0: float = Field(..., description="Left coordinate in PDF points")
    y0: float = Field(..., description="Top coordinate in PDF points")
    x1: float = Field(..., description="Right coordinate in PDF points")
    y1: float = Field(..., description="Bottom coordinate in PDF points")
    page_width: float = Field(default=612.0, description="Original page width in points")
    page_height: float = Field(default=792.0, description="Original page height in points")

class IdentifiedSpan(BaseModel):
    span_id: str
    target_text: str
    start_char_idx: Optional[int] = 0
    end_char_idx: Optional[int] = 0
    bbox: BoundingBox
    risk_score_pct: int = Field(..., ge=0, le=100, description="0-100 hazard index score")
    risk_level: str = Field(..., description="Low, Medium, High, Critical")
    category: str = Field(..., description="Ambiguity Trap, Unilateral Burden, Enforceability Issue, Missing Qualifier")
    rationale: str
    suggested_replacement: str

class ClauseAudit(BaseModel):
    clause_id: str
    clause_title: str
    raw_text: str
    page_number: int
    party_perspective: str
    impact: str = Field(..., description="Favorable, Neutral, Unfavorable, Predatory")
    strategic_takeaway: str
    missing_protections: List[str] = Field(default_factory=list)
    identified_spans: List[IdentifiedSpan] = Field(default_factory=list)

class DocumentAuditResponse(BaseModel):
    document_id: str
    filename: str
    contract_type: str
    selected_role: str
    overall_contract_score: int = Field(..., ge=0, le=100, description="0-100 overall contract safety score")
    summary_of_findings: str
    clauses: List[ClauseAudit] = Field(default_factory=list)
    total_spans_count: int = 0
    high_risk_count: int = 0

class DocumentStatusResponse(BaseModel):
    document_id: str
    status: str = Field(..., description="PENDING, PARSING, ANALYZING, COMPLETED, FAILED")
    message: Optional[str] = None
    progress_pct: int = 0

class SampleContractInfo(BaseModel):
    sample_id: str
    title: str
    description: str
    contract_type: str
    recommended_roles: List[str]
    filename: str

class AnalyzeSampleRequest(BaseModel):
    sample_id: str
    role: str
    contract_type: Optional[str] = None

class ReevaluateRoleRequest(BaseModel):
    document_id: str
    role: str
    contract_type: Optional[str] = None

