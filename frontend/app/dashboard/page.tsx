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
    <div className="space-y-10">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">

        {/* LEFT */}
        <div>
          <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-1 text-sm text-blue-400">
            👋 Welcome Back
          </span>

          <h1 className="mt-4 text-5xl font-extrabold tracking-tight">
            {greeting}, {userName}
          </h1>

          <p className="mt-3 text-lg text-slate-400">
            Here's your financial market overview for today.
          </p>
        </div>

        {/* RIGHT */}
        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">

          <p className="text-sm text-slate-400">
            Today
          </p>

          <h2 className="mt-2 text-xl font-bold">
            {formattedDate}
          </h2>

          <div className="mt-5 flex flex-wrap gap-3">

            <button
              type="button"
              onClick={() => router.push("/stocks")}
              className="rounded-xl bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500"
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
              className="rounded-xl border border-white/10 bg-white/5 px-5 py-3 font-medium transition hover:bg-white/10"
            >
              AI Report
            </button>

          </div>
        </div>

      </div>

      {/* =====================================================
          DASHBOARD CARDS
      ====================================================== */}

      <DashboardCards />

      {/* =====================================================
          PORTFOLIO + WATCHLIST
      ====================================================== */}

      <div className="grid gap-8 xl:grid-cols-3">

        <div className="xl:col-span-2">
          <PortfolioChart />
        </div>

        <Watchlist />

      </div>

      {/* =====================================================
          PRICE ALERTS
      ====================================================== */}

      <PriceAlerts />

      {/* =====================================================
          AI ASSISTANT + STOCK EXPLORER
      ====================================================== */}

      <div
        id="ai-assistant"
        className="grid gap-8 scroll-mt-24 lg:grid-cols-2"
      >
        <AIAssistant />
        <StockSearch />
      </div>

      {/* =====================================================
          MARKET NEWS + TOP MOVERS
      ====================================================== */}

      <div className="grid gap-8 lg:grid-cols-2">

        <MarketNews />

        <TopMovers />

      </div>

      {/* =====================================================
          ETF + PORTFOLIO ALLOCATION
      ====================================================== */}

      <div className="grid gap-8 lg:grid-cols-2">

        <ETFTable />

        <PortfolioAllocation />

      </div>

      {/* =====================================================
          MARKET HEATMAP
      ====================================================== */}

      <MarketHeatmap />

    </div>
  );
}