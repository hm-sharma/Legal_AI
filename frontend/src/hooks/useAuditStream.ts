import { useState, useCallback } from "react";
import { DocumentAuditResponse } from "../lib/types";
import { uploadDocument, analyzeSampleContract, reevaluateRole } from "../lib/api";

export function useAuditStream() {
  const [auditData, setAuditData] = useState<DocumentAuditResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadSample = useCallback(async (sampleId: string, role: string) => {
    setLoading(true);
    setError(null);
    try:
      const data = await analyzeSampleContract(sampleId, role);
      setAuditData(data);
      return data;
    } catch (err: any) {
      setError(err.message || "Failed to load sample contract audit");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const uploadAndAudit = useCallback(async (file: File, role: string) => {
    setLoading(true);
    setError(null);
    try:
      const data = await uploadDocument(file, role);
      setAuditData(data);
      return data;
    } catch (err: any) {
      setError(err.message || "Failed to upload and audit document");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const switchRole = useCallback(async (docId: string, newRole: string) => {
    setLoading(true);
    setError(null);
    try:
      const data = await reevaluateRole(docId, newRole);
      setAuditData(data);
      return data;
    } catch (err: any) {
      setError(err.message || "Failed to reevaluate party perspective");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    auditData,
    setAuditData,
    loading,
    error,
    loadSample,
    uploadAndAudit,
    switchRole,
  };
}
