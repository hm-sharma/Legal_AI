import React, { useState } from "react";
import { Copy, Check, AlertTriangle, ShieldAlert, X } from "lucide-react";
import { IdentifiedSpan } from "../../lib/types";

interface SpanInspectorProps {
  span: IdentifiedSpan | null;
  onClose: () => void;
}

export const SpanInspector: React.FC<SpanInspectorProps> = ({ span, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!span) return null;

  const copyRedline = () => {
    navigator.clipboard.writeText(span.suggested_replacement);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case "Critical":
        return "bg-red-500/10 text-red-400 border-red-500/30";
      case "High":
        return "bg-orange-500/10 text-orange-400 border-orange-500/30";
      case "Medium":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      default:
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
    }
  };

  return (
    <div className="bg-[#111827] border border-[#1F293D] rounded-lg p-4 shadow-xl mb-4 relative">
      <button
        onClick={onClose}
        className="absolute top-3 right-3 text-slate-400 hover:text-white transition-colors"
      >
        <X size={16} />
      </button>

      <div className="flex items-center space-x-2 mb-2">
        <ShieldAlert className="text-red-400" size={18} />
        <span className="text-sm font-semibold text-slate-200">Span Inspector</span>
        <span className={`text-xs px-2 py-0.5 rounded border font-medium ${getRiskBadge(span.risk_level)}`}>
          {span.risk_level} ({span.risk_score_pct}% Hazard)
        </span>
      </div>

      <div className="space-y-3 text-xs">
        <div>
          <span className="text-slate-400 font-medium block mb-1">Flagged Text Excerpt:</span>
          <p className="bg-[#090D16] p-2.5 rounded border border-red-500/20 text-red-200 font-mono">
            "{span.target_text}"
          </p>
        </div>

        <div>
          <span className="text-slate-400 font-medium block mb-1">Attorney Risk Rationale:</span>
          <p className="text-slate-300 leading-relaxed bg-[#090D16]/50 p-2.5 rounded border border-[#1F293D]">
            {span.rationale}
          </p>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-emerald-400 font-medium flex items-center gap-1">
              <AlertTriangle size={13} /> Suggested Redline Replacement:
            </span>
            <button
              onClick={copyRedline}
              className="flex items-center gap-1 text-[11px] bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded transition-colors"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              {copied ? "Copied!" : "Copy Redline"}
            </button>
          </div>
          <p className="bg-emerald-950/20 border border-emerald-500/30 p-2.5 rounded text-emerald-200 font-mono">
            {span.suggested_replacement}
          </p>
        </div>
      </div>
    </div>
  );
};
