"use client";

import { useState } from "react";
import { Search, TrendingUp, BarChart3, ShieldCheck } from "lucide-react";
import ETFTable from "@/components/dashboard/ETFTable";

export default function ETFsPage() {
  const [search, setSearch] = useState("");

  return (
    <main className="min-h-screen bg-[#050a18] text-white">

      <div className="mx-auto max-w-[1500px] space-y-10 px-6 py-10 lg:px-10">

        {/* =====================================================
            HEADER
        ====================================================== */}
        <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#111b35] via-[#0c152b] to-[#071021] p-8 shadow-2xl">

          {/* Glow */}
          <div className="pointer-events-none absolute -right-32 -top-32 h-80 w-80 rounded-full bg-blue-500/10 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-32 left-1/3 h-80 w-80 rounded-full bg-cyan-500/5 blur-3xl" />

          <div className="relative">

            <div className="flex flex-col justify-between gap-8 lg:flex-row lg:items-end">

              <div>
                <div className="flex items-center gap-3">
                  <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
                    Market Funds
                  </span>

                  <span className="flex items-center gap-2 text-xs text-emerald-400">
                    <span className="h-2 w-2 rounded-full bg-emerald-400" />
                    Live Market
                  </span>
                </div>

                <h1 className="mt-5 text-4xl font-extrabold tracking-tight md:text-5xl">
                  ETF Explorer
                </h1>

                <p className="mt-3 max-w-2xl text-base leading-7 text-slate-400">
                  Discover, compare and track exchange-traded funds
                  across major Indian market segments.
                </p>
              </div>

              <div className="grid grid-cols-3 gap-3">

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-4">
                  <BarChart3 className="mb-2 h-5 w-5 text-blue-400" />
                  <p className="text-xs text-slate-500">
                    ETFs
                  </p>
                  <p className="mt-1 text-xl font-bold">
                    4
                  </p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-4">
                  <TrendingUp className="mb-2 h-5 w-5 text-emerald-400" />
                  <p className="text-xs text-slate-500">
                    Gainers
                  </p>
                  <p className="mt-1 text-xl font-bold text-emerald-400">
                    3
                  </p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-4">
                  <ShieldCheck className="mb-2 h-5 w-5 text-cyan-400" />
                  <p className="text-xs text-slate-500">
                    Tracked
                  </p>
                  <p className="mt-1 text-xl font-bold">
                    0
                  </p>
                </div>

              </div>
            </div>

          </div>
        </section>


        {/* =====================================================
            SEARCH
        ====================================================== */}
        <section className="rounded-3xl border border-white/10 bg-[#0d162b] p-6 shadow-xl">

          <div className="mb-5">
            <h2 className="text-xl font-bold">
              Find an ETF
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Search your favorite ETF and add it to your watchlist.
            </p>
          </div>

          <div className="relative">

            <Search className="absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />

            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search ETFs, sectors or symbols..."
              className="
                w-full
                rounded-2xl
                border
                border-white/10
                bg-[#080f20]
                py-4
                pl-14
                pr-5
                text-white
                outline-none
                transition
                placeholder:text-slate-600
                focus:border-blue-500/50
                focus:ring-2
                focus:ring-blue-500/10
              "
            />

          </div>

        </section>


        {/* =====================================================
            ETF TABLE
        ====================================================== */}
        <section className="overflow-hidden rounded-3xl border border-white/10 bg-[#0d162b] shadow-2xl">

          <div className="border-b border-white/10 px-7 py-6">

            <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-2xl font-bold">
                    ETF Watchlist
                  </h2>

                  <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-400">
                    NSE
                  </span>
                </div>

                <p className="mt-1 text-sm text-slate-400">
                  Track your favorite exchange-traded funds.
                </p>
              </div>

              <button
                type="button"
                className="
                  rounded-xl
                  border
                  border-blue-500/20
                  bg-blue-600
                  px-5
                  py-3
                  text-sm
                  font-semibold
                  transition
                  hover:bg-blue-500
                  hover:shadow-lg
                  hover:shadow-blue-500/20
                "
              >
                Explore ETFs
              </button>

            </div>

          </div>

          <div className="p-5">
            <ETFTable searchQuery={search} />
          </div>

        </section>


        {/* =====================================================
            CATEGORIES
        ====================================================== */}
        <section>

          <div className="mb-5">
            <h2 className="text-2xl font-bold">
              Explore by Category
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Quickly discover ETFs by market segment.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {[
              {
                name: "Nifty 50",
                description: "Large-cap Indian equities",
                icon: "📊",
              },
              {
                name: "Banking",
                description: "Indian banking sector",
                icon: "🏦",
              },
              {
                name: "Gold",
                description: "Gold-linked ETFs",
                icon: "🪙",
              },
              {
                name: "Information Technology",
                description: "Technology sector",
                icon: "💻",
              },
            ].map((category) => (
              <button
                key={category.name}
                type="button"
                className="
                  group
                  rounded-2xl
                  border
                  border-white/10
                  bg-[#0d162b]
                  p-5
                  text-left
                  transition
                  hover:-translate-y-1
                  hover:border-blue-500/30
                  hover:bg-[#111d38]
                "
              >

                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-xl">
                  {category.icon}
                </div>

                <h3 className="mt-4 font-semibold text-white">
                  {category.name}
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  {category.description}
                </p>

                <div className="mt-4 text-xs font-medium text-blue-400 opacity-0 transition group-hover:opacity-100">
                  Explore →
                </div>

              </button>
            ))}

          </div>

        </section>

      </div>

    </main>
  );
}