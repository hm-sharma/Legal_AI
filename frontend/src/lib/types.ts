export interface BoundingBox {
  page: number;
  x0: number;
  y0: number;
  x1: number;
  y1: number;
  page_width: number;
  page_height: number;
}

export interface IdentifiedSpan {
  span_id: string;
  target_text: string;
  start_char_idx?: number;
  end_char_idx?: number;
  bbox: BoundingBox;
  risk_score_pct: number;
  risk_level: "Low" | "Medium" | "High" | "Critical";
  category: "Ambiguity Trap" | "Unilateral Burden" | "Enforceability Issue" | "Missing Qualifier";
  rationale: string;
  suggested_replacement: string;
}

export interface ClauseAudit {
  clause_id: string;
  clause_title: string;
  raw_text: string;
  page_number: number;
  party_perspective: string;
  impact: "Favorable" | "Neutral" | "Unfavorable" | "Predatory";
  strategic_takeaway: string;
  missing_protections: string[];
  identified_spans: IdentifiedSpan[];
}

export interface DocumentAuditResponse {
  document_id: string;
  filename: string;
  contract_type: string;
  selected_role: string;
  overall_contract_score: number;
  summary_of_findings: string;
  clauses: ClauseAudit[];
  total_spans_count: number;
  high_risk_count: number;
}

export interface SampleContractInfo {
  sample_id: string;
  title: string;
  description: string;
  contract_type: string;
  recommended_roles: string[];
  filename: string;
}
