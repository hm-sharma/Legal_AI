import fitz
from app.workers.celery_app import celery_app
from app.services.parser.pdf_loader import PDFLoaderService
from app.services.legal_engine.attorney_evaluator import AttorneyEvaluatorService

@celery_app.task(name="analyze_document_async")
def analyze_document_async(pdf_path: str, filename: str, selected_role: str):
    """
    Celery background task for parsing vector PDF and computing legal audit results.
    """
    loader = PDFLoaderService(pdf_path)
    fitz_doc = loader.doc
    full_text_data = loader.extract_full_text_with_geometry()
    
    evaluator = AttorneyEvaluatorService()
    audit_res = evaluator.evaluate_document(fitz_doc, full_text_data, filename, selected_role)
    loader.close()
    
    return audit_res.dict()
