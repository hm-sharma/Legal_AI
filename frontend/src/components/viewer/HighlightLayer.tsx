import React from "react";
import { IdentifiedSpan } from "../../lib/types";

interface HighlightLayerProps {
  spans: IdentifiedSpan[];
  currentPage: number;
  activeSpan: IdentifiedSpan | null;
  onSelectSpan: (span: IdentifiedSpan) => void;
  pageWidth: number;
  pageHeight: number;
}

export const HighlightLayer: React.FC<HighlightLayerProps> = ({
  spans,
  currentPage,
  activeSpan,
  onSelectSpan,
  pageWidth = 612,
  pageHeight = 792,
}) => {
  const pageSpans = spans.filter((s) => s.bbox && s.bbox.page === currentPage);

  const getBorderColor = (level: string, isActive: boolean) => {
    if (isActive) return "stroke-white stroke-[3px] filter drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]";
    switch (level) {
      case "Critical":
        return "stroke-red-500 fill-red-500/25";
      case "High":
        return "stroke-orange-500 fill-orange-500/25";
      case "Medium":
        return "stroke-amber-500 fill-amber-500/25";
      case "Low":
      default:
        return "stroke-blue-500 fill-blue-500/25";
    }
  };

  return (
    <svg
      className="absolute top-0 left-0 w-full h-full pointer-events-none z-10"
      viewBox={`0 0 ${pageWidth} ${pageHeight}`}
      preserveAspectRatio="none"
    >
      {pageSpans.map((span) => {
        const bbox = span.bbox;
        const width = Math.max(bbox.x1 - bbox.x0, 20);
        const height = Math.max(bbox.y1 - bbox.y0, 14);
        const isActive = activeSpan?.span_id === span.span_id;

        return (
          <g key={span.span_id} className="pointer-events-auto cursor-pointer" onClick={() => onSelectSpan(span)}>
            <rect
              x={bbox.x0}
              y={bbox.y0}
              width={width}
              height={height}
              rx={3}
              className={`transition-all duration-200 ${getBorderColor(span.risk_level, isActive)}`}
              strokeWidth={isActive ? 3 : 1.5}
            />
            {isActive && (
              <text
                x={bbox.x0}
                y={Math.max(bbox.y0 - 6, 12)}
                fill="#ffffff"
                fontSize={10}
                fontWeight="bold"
                className="select-none filter drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]"
              >
                {span.category} ({span.risk_score_pct}%)
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
};
