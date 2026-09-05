import React, { useEffect, useState } from "react";
import { ZoomIn, ZoomOut, RotateCcw, ChevronLeft, ChevronRight } from "lucide-react";
import { IdentifiedSpan } from "../../lib/types";
import { fetchPageImage } from "../../lib/api";
import { HighlightLayer } from "./HighlightLayer";

interface PdfViewerProps {
  documentId: string;
  currentPage: number;
  onPageChange: (page: number) => void;
  zoomScale: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
  spans: IdentifiedSpan[];
  activeSpan: IdentifiedSpan | null;
  onSelectSpan: (span: IdentifiedSpan) => void;
}

export const PdfViewer: React.FC<PdfViewerProps> = ({
  documentId,
  currentPage,
  onPageChange,
  zoomScale,
  onZoomIn,
  onZoomOut,
  onResetZoom,
  spans,
  activeSpan,
  onSelectSpan,
}) => {
  const [imageDataUrl, setImageDataUrl] = useState<string | null>(null);
  const [pageMeta, setPageMeta] = useState<{ width: number; height: number }>({ width: 612, height: 792 });
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchPageImage(documentId, currentPage)
      .then((res) => {
        if (isMounted) {
          setImageDataUrl(res.image_data_url);
          setPageMeta({ width: res.width, height: res.height });
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [documentId, currentPage]);

  return (
    <div className="flex flex-col h-full bg-[#090D16] border-r border-[#1F293D] overflow-hidden">
      {/* Top Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#111827] border-b border-[#1F293D]">
        <div className="flex items-center space-x-2 text-sm text-slate-300">
          <button
            onClick={() => onPageChange(Math.max(currentPage - 1, 1))}
            disabled={currentPage <= 1}
            className="p-1 rounded hover:bg-slate-800 disabled:opacity-40 transition-colors"
          >
            <ChevronLeft size={18} />
          </button>
          <span>
            Page <span className="font-semibold text-white">{currentPage}</span>
          </span>
          <button
            onClick={() => onPageChange(currentPage + 1)}
            className="p-1 rounded hover:bg-slate-800 transition-colors"
          >
            <ChevronRight size={18} />
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <button onClick={onZoomOut} className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors" title="Zoom Out">
            <ZoomOut size={16} />
          </button>
          <span className="text-xs text-slate-400 font-mono">{Math.round(zoomScale * 100)}%</span>
          <button onClick={onZoomIn} className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors" title="Zoom In">
            <ZoomIn size={16} />
          </button>
          <button onClick={onResetZoom} className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors" title="Reset Zoom">
            <RotateCcw size={16} />
          </button>
        </div>
      </div>

      {/* Canvas / Page Scroll Container */}
      <div className="flex-1 overflow-auto flex justify-center items-start p-6 bg-[#090D16]">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
            <p className="text-sm">Rendering high-res PDF canvas...</p>
          </div>
        ) : imageDataUrl ? (
          <div
            className="relative shadow-2xl rounded-sm border border-slate-800 bg-white transition-transform duration-150 origin-top"
            style={{
              width: pageMeta.width * zoomScale,
              height: pageMeta.height * zoomScale,
            }}
          >
            <img
              src={imageDataUrl}
              alt={`PDF Page ${currentPage}`}
              className="w-full h-full object-contain pointer-events-none"
            />
            <HighlightLayer
              spans={spans}
              currentPage={currentPage}
              activeSpan={activeSpan}
              onSelectSpan={onSelectSpan}
              pageWidth={pageMeta.width}
              pageHeight={pageMeta.height}
            />
          </div>
        ) : (
          <div className="text-slate-400 text-sm py-12">Failed to render PDF page.</div>
        )}
      </div>
    </div>
  );
};
