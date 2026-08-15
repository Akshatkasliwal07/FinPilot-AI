"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function HeroButtons() {
  return (
    <div className="mt-10 flex flex-wrap gap-4">
      <Link
       href="/sign-up"
        className="group rounded-2xl bg-blue-600 px-8 py-4 font-semibold transition hover:bg-blue-500"
      >
        Start Free
        <ArrowRight className="ml-2 inline h-5 w-5 transition group-hover:translate-x-1" />
      </Link>

      <Link
        href="/dashboard"
        className="rounded-2xl border border-white/10 bg-white/5 px-8 py-4 font-semibold backdrop-blur-xl transition hover:bg-white/10"
      >
        Live Demo
      </Link>
    </div>
  );
}