"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { fetchDocumentAudit, reevaluateRole } from "../../../lib/api";
import { DocumentAuditResponse, IdentifiedSpan } from "../../../lib/types";
import { PdfViewer } from "../../../components/viewer/PdfViewer";
import { AnalysisSidebar } from "../../../components/analysis/AnalysisSidebar";
import { usePdfViewer } from "../../../hooks/usePdfViewer";

export default function DocumentAuditPage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params?.id as string;

  const [auditData, setAuditData] = useState<DocumentAuditResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadingRole, setLoadingRole] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const {
    currentPage,
    setCurrentPage,
    zoomScale,
    zoomIn,
    zoomOut,
    resetZoom,
    activeSpan,
    selectSpan,
  } = usePdfViewer();

  useEffect(() => {
    if (!documentId) return;
    setLoading(true);
    fetchDocumentAudit(documentId)
      .then((data) => {
        setAuditData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load document audit");
        setLoading(false);
      });
  }, [documentId]);

  const handleRoleSwitch = async (newRole: string) => {
    if (!documentId || !auditData) return;
    setLoadingRole(true);
    try {
      const updated = await reevaluateRole(documentId, newRole);
      setAuditData(updated);
    } catch (err: any) {
      alert(err.message || "Failed to reevaluate perspective");
    } finally {
      setLoadingRole(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#090D16] text-white">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-sm text-slate-300 font-medium">Loading Document Workbench...</p>
      </div>
    );
  }

  if (error || !auditData) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#090D16] text-white p-6">
        <p className="text-red-400 text-sm font-semibold mb-4">{error || "Document not found"}</p>
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-xs font-semibold hover:bg-blue-500 transition-colors"
        >
          <ArrowLeft size={16} /> Return to Dashboard
        </button>
      </div>
    );
  }

  const allSpans = auditData.clauses.flatMap((c) => c.identified_spans);

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Back Button Bar */}
      <div className="fixed bottom-4 left-4 z-40">
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-2 px-3 py-2 bg-[#111827]/90 backdrop-blur border border-[#1F293D] rounded-lg text-xs text-slate-300 hover:text-white shadow-xl transition-all"
        >
          <ArrowLeft size={14} /> Back to Dashboard
        </button>
      </div>

      {/* Left Pane: Interactive PDF Viewer Canvas */}
      <div className="w-7/12 h-full">
        <PdfViewer
          documentId={documentId}
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          zoomScale={zoomScale}
          onZoomIn={zoomIn}
          onZoomOut={zoomOut}
          onResetZoom={resetZoom}
          spans={allSpans}
          activeSpan={activeSpan}
          onSelectSpan={selectSpan}
        />
      </div>

      {/* Right Pane: Strategic Analysis & Risk Sidebar */}
      <div className="w-5/12 h-full">
        <AnalysisSidebar
          auditData={auditData}
          activeSpan={activeSpan}
          onSelectSpan={selectSpan}
          onRoleSwitch={handleRoleSwitch}
          loadingRoleSwitch={loadingRole}
        />
      </div>
    </div>
  );
}
