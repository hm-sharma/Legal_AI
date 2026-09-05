import React from "react";
import type { Metadata } from "next";
import { Scale, FileText, Sparkles } from "lucide-react";
import "../index.css";

export const metadata: Metadata = {
  title: "Legal Document Analyzer - Strategic Dual-Perspective Audit",
  description: "AI-powered commercial contract risk scoring, coordinate mapping, and party-conditioned legal redlining.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090D16] text-slate-100 min-h-screen flex flex-col font-sans antialiased">
        {/* Navigation Header */}
        <header className="h-16 bg-[#111827] border-b border-[#1F293D] px-6 flex items-center justify-between shrink-0 shadow-md">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/30">
              <Scale className="text-blue-400" size={22} />
            </div>
            <div>
              <h1 className="text-base font-bold text-white tracking-wide">Legal AI Analyzer</h1>
              <p className="text-[11px] text-slate-400">Dual-Perspective Coordinate Mapping Engine</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1.5 text-xs bg-blue-500/10 border border-blue-500/20 px-3 py-1.5 rounded-full text-blue-400 font-medium">
              <Sparkles size={14} />
              <span>Gemini & SentenceTransformers Engine</span>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 flex overflow-hidden">{children}</main>
      </body>
    </html>
  );
}
