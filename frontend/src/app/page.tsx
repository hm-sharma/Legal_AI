"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileText, ArrowRight, ShieldCheck, Zap } from "lucide-react";
import { fetchSampleContracts, uploadDocument, analyzeSampleContract } from "../lib/api";
import { SampleContractInfo } from "../lib/types";

export default function HomePage() {
  const router = useRouter();
  const [samples, setSamples] = useState<SampleContractInfo[]>([]);
  const [selectedRole, setSelectedRole] = useState<string>("Service Provider");
  const [loading, setLoading] = useState<boolean>(false);
  const [dragOver, setDragOver] = useState<boolean>(false);

  useEffect(() => {
    fetchSampleContracts()
      .then((data) => setSamples(data))
      .catch((err) => console.error("Failed to load sample contracts:", err));
  }, []);

  const handleFileUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Please upload a valid PDF document.");
      return;
    }
    setLoading(true);
    try {
      const res = await uploadDocument(file, selectedRole);
      router.push(`/document/${res.document_id}`);
    } catch (err: any) {
      alert(err.message || "Failed to upload document");
      setLoading(false);
    }
  };

  const handleSampleClick = async (sampleId: string) => {
    setLoading(true);
    try {
      const res = await analyzeSampleContract(sampleId, selectedRole);
      router.push(`/document/${res.document_id}`);
    } catch (err: any) {
      alert(err.message || "Failed to load sample contract");
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-[#090D16] p-8 max-w-6xl mx-auto flex flex-col justify-center space-y-10">
      {/* Hero Header */}
      <div className="text-center space-y-3">
        <h2 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          Dual-Perspective Commercial Contract Audit
        </h2>
        <p className="text-slate-400 text-base max-w-2xl mx-auto leading-relaxed">
          Instantly detect predatory terms, unilateral burdens, and ambiguity traps in vector PDFs. Visual bounding box coordinates mapped directly to your contract pages.
        </p>
      </div>

      {/* Role Selection & Upload Section */}
      <div className="bg-[#111827] border border-[#1F293D] rounded-2xl p-6 shadow-2xl space-y-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-4 border-b border-[#1F293D]">
          <div>
            <label className="text-sm font-bold text-white block">Select Your Contract Role Perspective:</label>
            <p className="text-xs text-slate-400">Risk scoring dynamically adjusts based on your bargaining position.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {["Service Provider", "Client / Buyer", "Disclosing Party", "Receiving Party"].map((role) => (
              <button
                key={role}
                onClick={() => setSelectedRole(role)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  selectedRole === role
                    ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/25"
                    : "bg-[#090D16] border-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                {role}
              </button>
            ))}
          </div>
        </div>

        {/* Dropzone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
              handleFileUpload(e.dataTransfer.files[0]);
            }
          }}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
            dragOver ? "border-blue-500 bg-blue-500/10" : "border-[#1F293D] hover:border-slate-700 bg-[#090D16]"
          }`}
        >
          <input
            type="file"
            accept=".pdf"
            className="hidden"
            id="pdf-upload-input"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) handleFileUpload(e.target.files[0]);
            }}
          />
          <label htmlFor="pdf-upload-input" className="cursor-pointer flex flex-col items-center space-y-3">
            <div className="p-4 bg-blue-600/10 rounded-full border border-blue-500/20 text-blue-400">
              <Upload size={32} />
            </div>
            <div>
              <span className="text-sm font-semibold text-white">Click to upload PDF contract</span>
              <span className="text-xs text-slate-400 block mt-1">or drag and drop vector PDF document here</span>
            </div>
          </label>
        </div>
      </div>

      {/* Preset Samples Loader */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Zap size={16} className="text-amber-400" /> Or Launch Instant Benchmark Sample Audit:
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {samples.map((sample) => (
            <div
              key={sample.sample_id}
              onClick={() => handleSampleClick(sample.sample_id)}
              className="bg-[#111827] border border-[#1F293D] rounded-xl p-5 hover:border-blue-500/50 cursor-pointer transition-all duration-200 group flex items-start justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <FileText className="text-blue-400" size={20} />
                  <h4 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors">
                    {sample.title}
                  </h4>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed max-w-md">{sample.description}</p>
                <div className="flex gap-2 pt-1">
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                    {sample.contract_type}
                  </span>
                </div>
              </div>
              <ArrowRight size={18} className="text-slate-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all mt-1" />
            </div>
          ))}
        </div>
      </div>

      {loading && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
          <h3 className="text-lg font-bold">Analyzing Legal Contract...</h3>
          <p className="text-xs text-slate-400 mt-1">Executing coordinate mapper & dual-perspective risk evaluation...</p>
        </div>
      )}
    </div>
  );
}
