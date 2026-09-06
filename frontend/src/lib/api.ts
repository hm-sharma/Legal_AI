import { DocumentAuditResponse, SampleContractInfo } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchSampleContracts(): Promise<SampleContractInfo[]> {
  const res = await fetch(`${API_BASE}/documents/samples`);
  if (!res.ok) throw new Error("Failed to fetch sample contracts");
  return res.json();
}

export async function uploadDocument(file: File, role: string, contractType?: string): Promise<DocumentAuditResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("role", role);
  if (contractType) formData.append("contract_type", contractType);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Document upload and analysis failed");
  return res.json();
}

export async function analyzeSampleContract(sampleId: string, role: string, contractType?: string): Promise<DocumentAuditResponse> {
  const res = await fetch(`${API_BASE}/documents/analyze-sample`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sample_id: sampleId, role, contract_type: contractType }),
  });
  if (!res.ok) throw new Error("Sample analysis failed");
  return res.json();
}

export async function reevaluateRole(documentId: string, role: string, contractType?: string): Promise<DocumentAuditResponse> {
  const res = await fetch(`${API_BASE}/documents/reevaluate-role`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, role, contract_type: contractType }),
  });
  if (!res.ok) throw new Error("Role re-evaluation failed");
  return res.json();
}

export async function fetchDocumentAudit(documentId: string): Promise<DocumentAuditResponse> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/audit`);
  if (!res.ok) throw new Error("Failed to fetch document audit");
  return res.json();
}

export async function fetchPageImage(documentId: string, pageNum: number): Promise<{ page_number: number; width: number; height: number; image_data_url: string }> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/pages/${pageNum}/image`);
  if (!res.ok) throw new Error(`Failed to fetch page ${pageNum} image`);
  return res.json();
}

export function getPdfUrl(documentId: string): string {
  return `${API_BASE}/documents/${documentId}/pdf`;
}
