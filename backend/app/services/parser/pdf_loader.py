import fitz  # PyMuPDF
import os
import base64
from typing import List, Dict, Any, Tuple, Optional

class PDFLoaderService:
    """
    Parses vector PDFs using PyMuPDF to extract text blocks, page geometry,
    and high-DPI page images for client-side display.
    """
    def __init__(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    @property
    def page_count(self) -> int:
        return len(self.doc)

    def extract_full_text_with_geometry(self) -> List[Dict[str, Any]]:
        """
        Extracts structured pages with width, height, and text blocks.
        """
        pages_data = []
        for page_idx in range(len(self.doc)):
            page = self.doc[page_idx]
            rect = page.rect
            page_num = page_idx + 1

            text_blocks = []
            raw_blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
            for b in raw_blocks:
                if len(b) >= 5 and b[4].strip():
                    text_blocks.append({
                        "block_no": b[5] if len(b) > 5 else 0,
                        "bbox": {
                            "x0": round(float(b[0]), 2),
                            "y0": round(float(b[1]), 2),
                            "x1": round(float(b[2]), 2),
                            "y1": round(float(b[3]), 2),
                        },
                        "text": b[4].strip()
                    })

            pages_data.append({
                "page_number": page_num,
                "width": round(float(rect.width), 2),
                "height": round(float(rect.height), 2),
                "text": page.get_text("text"),
                "blocks": text_blocks
            })

        return pages_data

    def render_page_image_base64(self, page_num: int, dpi: int = 150) -> Dict[str, Any]:
        """
        Renders a page as PNG base64 string for direct frontend canvas overlay.
        """
        if page_num < 1 or page_num > len(self.doc):
            raise ValueError(f"Invalid page number {page_num}")
        page = self.doc[page_num - 1]
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        base64_str = base64.b64encode(img_bytes).decode("utf-8")
        return {
            "page_number": page_num,
            "width": round(float(page.rect.width), 2),
            "height": round(float(page.rect.height), 2),
            "image_data_url": f"data:image/png;base64,{base64_str}"
        }

    def close(self):
        self.doc.close()
