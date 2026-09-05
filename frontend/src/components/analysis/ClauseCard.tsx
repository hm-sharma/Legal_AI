import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertCircle, ShieldCheck, FileText } from "lucide-react";
import { ClauseAudit, IdentifiedSpan } from "../../lib/types";

interface ClauseCardProps {
  clause: ClauseAudit;
  activeSpan: IdentifiedSpan | null;
  onSelectSpan: (span: IdentifiedSpan) => void;
}

export const ClauseCard: React.FC<ClauseCardProps> = ({ clause, activeSpan, onSelectSpan }) => {
  const [expanded, setExpanded] = useState<boolean>(true);

  const getImpactBadge = (impact: string) => {
    switch (impact) {
      case "Predatory":
        return "bg-red-500/10 text-red-400 border-red-500/30";
      case "Unfavorable":
        return "bg-orange-500/10 text-orange-400 border-orange-500/30";
      case "Neutral":
        return "bg-slate-500/10 text-slate-300 border-slate-500/30";
      case "Favorable":
      default:
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    }
  };

  return (
    <div className="bg-[#111827] border border-[#1F293D] rounded-lg overflow-hidden transition-all duration-200 hover:border-slate-700">
      {/* Header */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="p-3.5 flex items-center justify-between cursor-pointer bg-[#111827] hover:bg-slate-800/50 transition-colors"
      >
        <div className="flex items-center space-x-2.5">
          <FileText className="text-blue-400" size={18} />
          <div>
            <h4 className="text-sm font-semibold text-slate-200">{clause.clause_title}</h4>
            <span className="text-[11px] text-slate-400">Page {clause.page_number}</span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className={`text-xs px-2.5 py-0.5 rounded border font-medium ${getImpactBadge(clause.impact)}`}>
            {clause.impact}
          </span>
          {expanded ? <ChevronUp size={16} className="text-slate-400" /> : <ChevronDown size={16} className="text-slate-400" />}
        </div>
      </div>

      {/* Body */}
      {expanded && (
        <div className="p-4 border-t border-[#1F293D] bg-[#090D16]/40 space-y-3">
          {/* Excerpt */}
          <div className="text-xs text-slate-300 bg-[#090D16] p-3 rounded border border-slate-800 font-mono italic">
            "{clause.raw_text}"
          </div>

          {/* Takeaway */}
          <div className="text-xs space-y-1">
            <span className="text-slate-400 font-medium block">Strategic Takeaway ({clause.party_perspective}):</span>
            <p className="text-slate-300 bg-slate-900/60 p-2.5 rounded border border-slate-800 leading-relaxed">
              {clause.strategic_takeaway}
            </p>
          </div>

          {/* Missing Protections */}
          {clause.missing_protections && clause.missing_protections.length > 0 && (
            <div className="text-xs space-y-1">
              <span className="text-amber-400 font-medium flex items-center gap-1">
                <AlertCircle size={13} /> Missing Critical Protections:
              </span>
              <ul className="list-disc list-inside text-slate-300 space-y-1 pl-1">
                {clause.missing_protections.map((prot, idx) => (
                  <li key={idx} className="text-slate-300">{prot}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Spans */}
          {clause.identified_spans && clause.identified_spans.length > 0 && (
            <div className="pt-2 border-t border-slate-800/80">
              <span className="text-xs text-slate-400 font-medium block mb-2">Flagged Hazard Spans:</span>
              <div className="space-y-1.5">
                {clause.identified_spans.map((span) => {
                  const isSelected = activeSpan?.span_id === span.span_id;
                  return (
                    <button
                      key={span.span_id}
                      onClick={() => onSelectSpan(span)}
                      className={`w-full text-left p-2.5 rounded text-xs transition-all border ${
                        isSelected
                          ? "bg-blue-600/20 border-blue-500 text-white ring-1 ring-blue-500"
                          : "bg-[#090D16] border-slate-800 text-slate-300 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200">{span.category}</span>
                        <span className="text-[10px] text-red-400 font-bold">{span.risk_score_pct}% Risk</span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 truncate">"{span.target_text}"</p>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
