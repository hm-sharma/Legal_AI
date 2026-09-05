import { useState, useCallback } from "react";
import { IdentifiedSpan } from "../lib/types";

export function usePdfViewer() {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [zoomScale, setZoomScale] = useState<number>(1.2);
  const [activeSpan, setActiveSpan] = useState<IdentifiedSpan | null>(null);

  const zoomIn = useCallback(() => setZoomScale((prev) => Math.min(prev + 0.2, 2.5)), []);
  const zoomOut = useCallback(() => setZoomScale((prev) => Math.max(prev - 0.2, 0.6)), []);
  const resetZoom = useCallback(() => setZoomScale(1.2), []);

  const selectSpan = useCallback((span: IdentifiedSpan | null) => {
    setActiveSpan(span);
    if (span && span.bbox) {
      setCurrentPage(span.bbox.page);
    }
  }, []);

  return {
    currentPage,
    setCurrentPage,
    zoomScale,
    zoomIn,
    zoomOut,
    resetZoom,
    activeSpan,
    selectSpan,
  };
}
