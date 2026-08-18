"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import DashboardCards from "@/components/dashboard/DashboardCards";
import PortfolioChart from "@/components/dashboard/PortfolioChart";
import Watchlist from "@/components/dashboard/Watchlist";
import PriceAlerts from "@/components/dashboard/PriceAlerts";
import MarketNews from "@/components/dashboard/MarketNews";
import AIAssistant from "@/components/dashboard/AIAssistant";
import ETFTable from "@/components/dashboard/ETFTable";
import PortfolioAllocation from "@/components/dashboard/PortfolioAllocation";
import TopMovers from "@/components/dashboard/TopMovers";
import MarketHeatmap from "@/components/dashboard/MarketHeatmap";
import StockSearch from "@/components/dashboard/StockSearch";

export default function DashboardPage() {
  const router = useRouter();

  const [userName, setUserName] = useState("User");

  const today = new Date();

  const formattedDate = today.toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  function getGreeting() {
    const hour = new Date().getHours();

    if (hour < 12) {
      return "Good Morning";
    }

    if (hour < 17) {
      return "Good Afternoon";
    }

    if (hour < 21) {
      return "Good Evening";
    }

    return "Good Night";
  }

  useEffect(() => {
    const storedName =
      localStorage.getItem("user_name") ||
      localStorage.getItem("name") ||
      localStorage.getItem("username");

    if (storedName?.trim()) {
      setUserName(storedName.trim());
    }
  }, []);

  const greeting = getGreeting();

  return (
    <main className="w-full min-w-0 space-y-8 overflow-x-hidden px-0 sm:space-y-10">
      {/* =====================================================
          HEADER
      ====================================================== */}

      <section className="flex min-w-0 flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
        {/* LEFT */}

        <div className="min-w-0">
          <span className="inline-flex max-w-full items-center rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-400 sm:px-4 sm:text-sm">
            👋 Welcome Back
          </span>

          <h1 className="mt-4 break-words text-3xl font-extrabold tracking-tight sm:text-4xl lg:text-5xl">
            {greeting}, {userName}
          </h1>

          <p className="mt-3 max-w-2xl text-base leading-relaxed text-slate-400 sm:text-lg">
            Here's your financial market overview for today.
          </p>
        </div>

        {/* RIGHT */}

        <div className="w-full min-w-0 rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl sm:p-6 xl:w-auto xl:min-w-[360px]">
          <p className="text-sm text-slate-400">
            Today
          </p>

          <h2 className="mt-2 break-words text-lg font-bold sm:text-xl">
            {formattedDate}
          </h2>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={() => router.push("/stocks")}
              className="w-full rounded-xl bg-blue-600 px-5 py-3 text-center font-medium transition hover:bg-blue-500 sm:w-auto"
            >
              Analyze Stock
            </button>

            <button
              type="button"
              onClick={() => {
                const element =
                  document.getElementById("ai-assistant");

                element?.scrollIntoView({
                  behavior: "smooth",
                  block: "start",
                });
              }}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-center font-medium transition hover:bg-white/10 sm:w-auto"
            >
              AI Report
            </button>
          </div>
        </div>
      </section>

      {/* =====================================================
          DASHBOARD CARDS
      ====================================================== */}

      <section className="min-w-0">
        <DashboardCards />
      </section>

      {/* =====================================================
          PORTFOLIO + WATCHLIST
      ====================================================== */}

      <section className="grid min-w-0 gap-6 lg:gap-8 xl:grid-cols-3">
        <div className="min-w-0 xl:col-span-2">
          <PortfolioChart />
        </div>

        <div className="min-w-0">
          <Watchlist />
        </div>
      </section>

      {/* =====================================================
          PRICE ALERTS
      ====================================================== */}

      <section className="min-w-0">
        <PriceAlerts />
      </section>

      {/* =====================================================
          AI ASSISTANT + STOCK EXPLORER
      ====================================================== */}

      <section
        id="ai-assistant"
        className="grid min-w-0 scroll-mt-24 gap-6 lg:grid-cols-2 lg:gap-8"
      >
        <div className="min-w-0">
          <AIAssistant />
        </div>

        <div className="min-w-0">
          <StockSearch />
        </div>
      </section>

      {/* =====================================================
          MARKET NEWS + TOP MOVERS
      ====================================================== */}

      <section className="grid min-w-0 gap-6 lg:grid-cols-2 lg:gap-8">
        <div className="min-w-0">
          <MarketNews />
        </div>

        <div className="min-w-0">
          <TopMovers />
        </div>
      </section>

      {/* =====================================================
          ETF + PORTFOLIO ALLOCATION
      ====================================================== */}

      <section className="grid min-w-0 gap-6 lg:grid-cols-2 lg:gap-8">
        <div className="min-w-0">
          <ETFTable />
        </div>

        <div className="min-w-0">
          <PortfolioAllocation />
        </div>
      </section>

      {/* =====================================================
          MARKET HEATMAP
      ====================================================== */}

      <section className="min-w-0">
        <MarketHeatmap />
      </section>
    </main>
  );
}