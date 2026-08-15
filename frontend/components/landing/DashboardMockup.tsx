"use client";

import MiniChart from "./MiniChart";

export default function DashboardMockup() {
  return (
    <div className="rounded-[32px] border border-white/10 bg-slate-900/80 p-8 shadow-2xl backdrop-blur-xl">

      <div className="mb-8 flex items-center justify-between">

        <div>
          <h2 className="text-xl font-bold">
            Portfolio Overview
          </h2>

          <p className="mt-2 text-slate-400">
            AI powered analytics
          </p>
        </div>

        <div className="rounded-xl bg-green-500/20 px-4 py-2 text-green-400">
          +8.25%
        </div>

      </div>

      <h1 className="text-5xl font-extrabold">
        $126,700
      </h1>

      <MiniChart />

    </div>
  );
}