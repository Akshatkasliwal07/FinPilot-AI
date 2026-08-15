"use client";

import { Sparkles } from "lucide-react";

export default function HeroBadge() {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-5 py-2 text-sm text-blue-300">
      <Sparkles className="h-4 w-4" />
      AI-Powered Financial Research Platform
    </div>
  );
}