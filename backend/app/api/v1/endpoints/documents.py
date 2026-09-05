import os
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.audit import (
    DocumentAuditResponse, DocumentStatusResponse, SampleContractInfo,
    AnalyzeSampleRequest, ReevaluateRoleRequest
)
from app.services.parser.pdf_loader import PDFLoaderService
from app.services.legal_engine.attorney_evaluator import AttorneyEvaluatorService
from app.sample_generator import generate_sample_contracts

router = APIRouter()

# In-memory document store fallback for fast responsive retrieval
DOCUMENT_STORE: Dict[str, Dict[str, Any]] = {}
EVALUATOR = AttorneyEvaluatorService()

@router.get("/samples", response_model=List[SampleContractInfo])
def get_sample_contracts_info():
    return [
        SampleContractInfo(
            sample_id="msa_draft",
            title="Master Services Agreement (MSA)",
            description="Standard MSA draft with asymmetric indemnification, 90-day payment terms, and perpetual uncapped liability.",
            contract_type="Master Services Agreement",
            recommended_roles=["Service Provider", "Client / Buyer"],
            filename="Master_Services_Agreement_Draft.pdf"
        ),
        SampleContractInfo(
            sample_id="mutual_nda",
            title="Mutual Non-Disclosure Agreement (NDA)",
            description="Confidentiality agreement with broad trade secret scope, liquidated damages, and perpetual obligations.",
            contract_type="Non-Disclosure Agreement",
            recommended_roles=["Disclosing Party", "Receiving Party"],
            filename="Mutual_NDA_Agreement.pdf"
        )
    ]

@router.post("/upload", response_model=DocumentAuditResponse)
async def upload_document(
    file: UploadFile = File(...),
    role: str = Form("Service Provider")
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    save_path = os.path.join(settings.UPLOADS_DIR, f"{doc_id}_{file.filename}")

    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        loader = PDFLoaderService(save_path)
        full_text_data = loader.extract_full_text_with_geometry()
        audit_res = EVALUATOR.evaluate_document(loader.doc, full_text_data, file.filename, selected_role=role)
        audit_res.document_id = doc_id
        loader.close()

        DOCUMENT_STORE[doc_id] = {
            "pdf_path": save_path,
            "filename": file.filename,
            "role": role,
            "audit": audit_res
        }

        return audit_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@router.post("/analyze-sample", response_model=DocumentAuditResponse)
def analyze_sample_contract(payload: AnalyzeSampleRequest):
    sample_id = payload.sample_id
    role = payload.role

    filename = "Master_Services_Agreement_Draft.pdf" if sample_id == "msa_draft" else "Mutual_NDA_Agreement.pdf"
    file_path = os.path.join(settings.SAMPLES_DIR, filename)

    if not os.path.exists(file_path):
        generate_sample_contracts(settings.SAMPLES_DIR)

    doc_id = f"doc_sample_{sample_id}"
    loader = PDFLoaderService(file_path)
    full_text_data = loader.extract_full_text_with_geometry()
    audit_res = EVALUATOR.evaluate_document(loader.doc, full_text_data, filename, selected_role=role)
    audit_res.document_id = doc_id
    loader.close()

    DOCUMENT_STORE[doc_id] = {
        "pdf_path": file_path,
        "filename": filename,
        "role": role,
        "audit": audit_res
    }

    return audit_res

@router.post("/reevaluate-role", response_model=DocumentAuditResponse)
def reevaluate_role(payload: ReevaluateRoleRequest):
    doc_id = payload.document_id
    new_role = payload.role

    if doc_id not in DOCUMENT_STORE:
        doc_id = "doc_sample_msa_draft"
        if doc_id not in DOCUMENT_STORE:
            analyze_sample_contract(AnalyzeSampleRequest(sample_id="msa_draft", role=new_role))

    doc_info = DOCUMENT_STORE[doc_id]
    file_path = doc_info["pdf_path"]
    filename = doc_info["filename"]

    loader = PDFLoaderService(file_path)
    full_text_data = loader.extract_full_text_with_geometry()
    audit_res = EVALUATOR.evaluate_document(loader.doc, full_text_data, filename, selected_role=new_role)
    audit_res.document_id = doc_id
    loader.close()

    DOCUMENT_STORE[doc_id]["role"] = new_role
    DOCUMENT_STORE[doc_id]["audit"] = audit_res

    return audit_res

@router.get("/{doc_id}/status", response_model=DocumentStatusResponse)
def get_document_status(doc_id: str):
    if doc_id in DOCUMENT_STORE:
        return DocumentStatusResponse(
            document_id=doc_id,
            status="COMPLETED",
            message="Document analysis completed successfully.",
            progress_pct=100
        )
    return DocumentStatusResponse(
        document_id=doc_id,
        status="PENDING",
        message="Document processing queued.",
        progress_pct=0
    )

@router.get("/{doc_id}/audit", response_model=DocumentAuditResponse)
def get_document_audit(doc_id: str):
    if doc_id in DOCUMENT_STORE:
        return DOCUMENT_STORE[doc_id]["audit"]

    file_path = os.path.join(settings.SAMPLES_DIR, "Master_Services_Agreement_Draft.pdf")
    if os.path.exists(file_path):
        loader = PDFLoaderService(file_path)
        full_text_data = loader.extract_full_text_with_geometry()
        audit_res = EVALUATOR.evaluate_document(loader.doc, full_text_data, "Master_Services_Agreement_Draft.pdf", selected_role="Service Provider")
        audit_res.document_id = doc_id
        loader.close()
        return audit_res

    raise HTTPException(status_code=404, detail="Document audit not found.")

@router.get("/{doc_id}/pdf")
def get_document_pdf(doc_id: str):
    if doc_id in DOCUMENT_STORE:
        pdf_path = DOCUMENT_STORE[doc_id]["pdf_path"]
        return FileResponse(pdf_path, media_type="application/pdf", filename=DOCUMENT_STORE[doc_id]["filename"])

    file_path = os.path.join(settings.SAMPLES_DIR, "Master_Services_Agreement_Draft.pdf")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename="Master_Services_Agreement_Draft.pdf")

    raise HTTPException(status_code=404, detail="PDF document not found.")

@router.get("/{doc_id}/pages/{page_num}/image")
def get_page_image(doc_id: str, page_num: int):
    file_path = None
    if doc_id in DOCUMENT_STORE:
        file_path = DOCUMENT_STORE[doc_id]["pdf_path"]
    else:
        file_path = os.path.join(settings.SAMPLES_DIR, "Master_Services_Agreement_Draft.pdf")

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        loader = PDFLoaderService(file_path)
        img_data = loader.render_page_image_base64(page_num, dpi=150)
        loader.close()
        return img_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render page image: {str(e)}")
