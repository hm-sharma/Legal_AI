"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileText, ArrowRight, ShieldCheck, Zap, Layers } from "lucide-react";
import { fetchSampleContracts, uploadDocument, analyzeSampleContract } from "../lib/api";
import { SampleContractInfo } from "../lib/types";

const DOCUMENT_TYPE_ROLE_MAP: Record<string, { label: string; roles: string[]; defaultRole: string }> = {
  "Lease Agreement": {
    label: "Residential / Commercial Lease Agreement",
    roles: ["Tenant", "Landlord / Owner"],
    defaultRole: "Tenant",
  },
  "Master Services Agreement": {
    label: "Master Services Agreement (MSA)",
    roles: ["Service Provider", "Client / Buyer"],
    defaultRole: "Service Provider",
  },
  "Non-Disclosure Agreement": {
    label: "Non-Disclosure Agreement (NDA)",
    roles: ["Receiving Party", "Disclosing Party"],
    defaultRole: "Receiving Party",
  },
  "Employment Agreement": {
    label: "Employment / Consulting Agreement",
    roles: ["Employee / Consultant", "Employer / Client"],
    defaultRole: "Employee / Consultant",
  },
  "Commercial Contract": {
    label: "General Commercial Contract",
    roles: ["Service Provider", "Client / Buyer"],
    defaultRole: "Service Provider",
  },
  "Auto-Detect": {
    label: "Auto-Detect from Document Text",
    roles: ["Service Provider", "Client / Buyer", "Tenant", "Landlord / Owner"],
    defaultRole: "Service Provider",
  },
};

export default function HomePage() {
  const router = useRouter();
  const [samples, setSamples] = useState<SampleContractInfo[]>([]);
  const [contractType, setContractType] = useState<string>("Lease Agreement");
  const [selectedRole, setSelectedRole] = useState<string>("Tenant");
  const [loading, setLoading] = useState<boolean>(false);
  const [dragOver, setDragOver] = useState<boolean>(false);

  useEffect(() => {
    fetchSampleContracts()
      .then((data) => setSamples(data))
      .catch((err) => console.error("Failed to load sample contracts:", err));
  }, []);

  const handleContractTypeChange = (type: string) => {
    setContractType(type);
    const config = DOCUMENT_TYPE_ROLE_MAP[type];
    if (config) {
      setSelectedRole(config.defaultRole);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Please upload a valid PDF document.");
      return;
    }
    setLoading(true);
    try {
      const res = await uploadDocument(file, selectedRole, contractType);
      router.push(`/document/${res.document_id}`);
    } catch (err: any) {
      alert(err.message || "Failed to upload document");
      setLoading(false);
    }
  };

  const handleSampleClick = async (sample: SampleContractInfo) => {
    setLoading(true);
    try {
      const defaultRole = sample.recommended_roles[0] || selectedRole;
      const res = await analyzeSampleContract(sample.sample_id, defaultRole, sample.contract_type);
      router.push(`/document/${res.document_id}`);
    } catch (err: any) {
      alert(err.message || "Failed to load sample contract");
      setLoading(false);
    }
  };

  const currentRoleOptions = DOCUMENT_TYPE_ROLE_MAP[contractType]?.roles || ["Service Provider", "Client / Buyer"];

  return (
    <div className="flex-1 overflow-y-auto bg-[#090D16] p-8 max-w-6xl mx-auto flex flex-col justify-center space-y-10">
      {/* Hero Header */}
      <div className="text-center space-y-3">
        <h2 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          Context-Aware Legal Document Audit
        </h2>
        <p className="text-slate-400 text-base max-w-2xl mx-auto leading-relaxed">
          Select your agreement type and party role to inspect predatory terms, unilateral burdens, and liability caps with visual PDF coordinate highlights.
        </p>
      </div>

      {/* Document Type & Role Selection Workbench */}
      <div className="bg-[#111827] border border-[#1F293D] rounded-2xl p-6 shadow-2xl space-y-6">
        
        {/* Step 1: Document Type Selector */}
        <div className="space-y-2 pb-4 border-b border-[#1F293D]">
          <label className="text-sm font-bold text-white flex items-center gap-2">
            <Layers size={16} className="text-blue-400" /> Step 1: Select Legal Document Type
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {Object.keys(DOCUMENT_TYPE_ROLE_MAP).map((typeKey) => (
              <button
                key={typeKey}
                onClick={() => handleContractTypeChange(typeKey)}
                className={`p-2.5 rounded-lg text-xs font-medium border text-left transition-all ${
                  contractType === typeKey
                    ? "bg-blue-600/20 border-blue-500 text-blue-300 ring-1 ring-blue-500 font-semibold"
                    : "bg-[#090D16] border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                }`}
              >
                {DOCUMENT_TYPE_ROLE_MAP[typeKey].label}
              </button>
            ))}
          </div>
        </div>

        {/* Step 2: Context-Aware Role Perspective Selector */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-4 border-b border-[#1F293D]">
          <div>
            <label className="text-sm font-bold text-white block">Step 2: Select Bargaining Perspective:</label>
            <p className="text-xs text-slate-400">Risk scoring dynamically adapts to your bargaining position.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {currentRoleOptions.map((role) => (
              <button
                key={role}
                onClick={() => setSelectedRole(role)}
                className={`px-4 py-2 rounded-lg text-xs font-semibold border transition-all ${
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

        {/* Step 3: PDF Upload Dropzone */}
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
              <span className="text-xs text-slate-400 block mt-1">
                Auditing as <span className="text-blue-400 font-bold">{selectedRole}</span> under <span className="text-blue-400 font-bold">{DOCUMENT_TYPE_ROLE_MAP[contractType]?.label}</span>
              </span>
            </div>
          </label>
        </div>
      </div>

      {/* Benchmark Samples Launcher */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Zap size={16} className="text-amber-400" /> Or Launch Instant Benchmark Sample Audit:
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {samples.map((sample) => (
            <div
              key={sample.sample_id}
              onClick={() => handleSampleClick(sample)}
              className="bg-[#111827] border border-[#1F293D] rounded-xl p-4 hover:border-blue-500/50 cursor-pointer transition-all duration-200 group flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <FileText className="text-blue-400" size={18} />
                  <h4 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors">
                    {sample.title}
                  </h4>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{sample.description}</p>
              </div>
              <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 mt-3">
                <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono">
                  {sample.contract_type}
                </span>
                <ArrowRight size={16} className="text-slate-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {loading && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
          <h3 className="text-lg font-bold">Auditing Legal Contract...</h3>
          <p className="text-xs text-slate-400 mt-1">Executing coordinate mapping & role-conditioned evaluation...</p>
        </div>
      )}
    </div>
  );
}
