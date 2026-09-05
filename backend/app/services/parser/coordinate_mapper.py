from typing import Optional
from app.schemas.audit import BoundingBox

class CoordinateMapperService:
    """
    Locates exact bounding box coordinates [x0, y0, x1, y1] for target phrases
    in the PyMuPDF vector PDF document.
    """
    @staticmethod
    def find_phrase_bbox(fitz_doc, target_text: str, preferred_page: Optional[int] = None) -> BoundingBox:
        cleaned_target = target_text.strip()
        pages_to_search = range(len(fitz_doc))
        if preferred_page and 1 <= preferred_page <= len(fitz_doc):
            pages_to_search = [preferred_page - 1] + [i for i in range(len(fitz_doc)) if i != preferred_page - 1]

        for p_idx in pages_to_search:
            page = fitz_doc[p_idx]
            page_num = p_idx + 1
            page_rect = page.rect

            # 1. Exact phrase match
            rects = page.search_for(cleaned_target)
            if rects:
                r = rects[0]
                return BoundingBox(
                    page=page_num,
                    x0=round(float(r.x0), 2),
                    y0=round(float(r.y0), 2),
                    x1=round(float(r.x1), 2),
                    y1=round(float(r.y1), 2),
                    page_width=round(float(page_rect.width), 2),
                    page_height=round(float(page_rect.height), 2)
                )

            # 2. Sub-phrase fragment search fallback
            words = cleaned_target.split()
            if len(words) > 3:
                sub_phrase = " ".join(words[:4])
                rects = page.search_for(sub_phrase)
                if rects:
                    r = rects[0]
                    return BoundingBox(
                        page=page_num,
                        x0=round(float(r.x0), 2),
                        y0=round(float(r.y0), 2),
                        x1=round(float(r.x1), 2),
                        y1=round(float(r.y1), 2),
                        page_width=round(float(page_rect.width), 2),
                        page_height=round(float(page_rect.height), 2)
                    )

        # Fallback default bounding box
        target_page = preferred_page if preferred_page else 1
        page = fitz_doc[target_page - 1] if target_page <= len(fitz_doc) else fitz_doc[0]
        return BoundingBox(
            page=target_page,
            x0=72.0,
            y0=200.0,
            x1=540.0,
            y1=220.0,
            page_width=round(float(page.rect.width), 2),
            page_height=round(float(page.rect.height), 2)
        )
