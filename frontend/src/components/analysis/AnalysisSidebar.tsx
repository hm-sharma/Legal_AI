import React, { useState } from "react";
import { ShieldCheck, ShieldAlert, RefreshCw, Filter, FileCheck } from "lucide-react";
import { DocumentAuditResponse, IdentifiedSpan } from "../../lib/types";
import { ClauseCard } from "./ClauseCard";
import { SpanInspector } from "./SpanInspector";

interface AnalysisSidebarProps {
  auditData: DocumentAuditResponse;
  activeSpan: IdentifiedSpan | null;
  onSelectSpan: (span: IdentifiedSpan | null) => void;
  onRoleSwitch: (newRole: string) => void;
  loadingRoleSwitch: boolean;
}

export const AnalysisSidebar: React.FC<AnalysisSidebarProps> = ({
  auditData,
  activeSpan,
  onSelectSpan,
  onRoleSwitch,
  loadingRoleSwitch,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>("ALL");

  // Determine context-aware role options based on contract type
  const getRolesForContractType = (type: string): string[] => {
    const lower = type.toLowerCase();
    if (lower.includes("lease") || lower.includes("rent")) {
      return ["Tenant", "Landlord / Owner"];
    } else if (lower.includes("nda") || lower.includes("confidential")) {
      return ["Receiving Party", "Disclosing Party"];
    } else if (lower.includes("employment") || lower.includes("consultant")) {
      return ["Employee / Consultant", "Employer / Client"];
    } else {
      return ["Service Provider", "Client / Buyer"];
    }
  };

  const rolesOptions = getRolesForContractType(auditData.contract_type);

  const getScoreColor = (score: number) => {
    if (score >= 70) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (score >= 40) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    return "text-red-400 border-red-500/30 bg-red-500/10";
  };

  const filteredClauses = auditData.clauses.filter((clause) => {
    if (filterCategory === "ALL") return true;
    return clause.identified_spans.some((s) => s.category === filterCategory);
  });

  return (
    <div className="w-full h-full flex flex-col bg-[#090D16] border-l border-[#1F293D] overflow-hidden">
      {/* Header & Score Gauge */}
      <div className="p-5 bg-[#111827] border-b border-[#1F293D] space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white tracking-wide">{auditData.filename}</h2>
            <span className="text-xs text-slate-400">{auditData.contract_type}</span>
          </div>

          <div className={`flex flex-col items-center px-4 py-2 rounded-xl border ${getScoreColor(auditData.overall_contract_score)}`}>
            <span className="text-2xl font-black">{auditData.overall_contract_score}</span>
            <span className="text-[10px] uppercase font-bold tracking-wider opacity-80">Safety Score</span>
          </div>
        </div>

        {/* Perspective Switcher */}
        <div className="flex flex-col space-y-1.5 pt-2 border-t border-slate-800">
          <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
            <span>Evaluating Perspective:</span>
            {loadingRoleSwitch && <span className="text-[11px] text-blue-400 animate-pulse">Re-evaluating...</span>}
          </label>
          <div className="grid grid-cols-2 gap-1.5">
            {rolesOptions.map((role) => (
              <button
                key={role}
                onClick={() => onRoleSwitch(role)}
                disabled={loadingRoleSwitch}
                className={`py-1.5 px-2 rounded text-xs font-medium border transition-all ${
                  auditData.selected_role === role
                    ? "bg-blue-600 border-blue-500 text-white shadow-md shadow-blue-500/20"
                    : "bg-[#090D16] border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                }`}
              >
                {role}
              </button>
            ))}
          </div>
        </div>

        {/* Executive Summary */}
        <div className="bg-[#090D16] p-3 rounded-lg border border-slate-800 text-xs text-slate-300 space-y-1">
          <span className="font-semibold text-blue-400 block">Attorney Executive Summary:</span>
          <p className="leading-relaxed opacity-90">{auditData.summary_of_findings}</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="px-4 py-2 bg-[#090D16] border-b border-[#1F293D] flex items-center space-x-2 overflow-x-auto">
        <Filter size={14} className="text-slate-400 shrink-0" />
        {["ALL", "Unilateral Burden", "Ambiguity Trap", "Enforceability Issue"].map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`text-xs px-2.5 py-1 rounded-full whitespace-nowrap border transition-colors ${
              filterCategory === cat
                ? "bg-blue-500/20 text-blue-400 border-blue-500/40 font-medium"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Clause Cards List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Active Span Inspector Drawer */}
        {activeSpan && <SpanInspector span={activeSpan} onClose={() => onSelectSpan(null)} />}

        {filteredClauses.length > 0 ? (
          filteredClauses.map((clause) => (
            <ClauseCard
              key={clause.clause_id}
              clause={clause}
              activeSpan={activeSpan}
              onSelectSpan={onSelectSpan}
            />
          ))
        ) : (
          <div className="text-center py-12 text-slate-500 text-xs">
            No clauses match the selected category filter.
          </div>
        )}
      </div>
    </div>
  );
};
