"use client";

import {
  Activity,
  BellRing,
  TrendingDown,
  TrendingUp,
  Eye,
} from "lucide-react";
import CountUp from "react-countup";
import { useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://finpilot-ai-q4nk.onrender.com";

interface MarketIndex {
  symbol: string;
  price: number;
  previous_close: number;
  change: number;
  change_percent: number;
  timestamp: string;
  market_status: string;
  data_source?: string;
}

interface IndicesResponse {
  success: boolean;
  data?: {
    "NIFTY 50"?: MarketIndex;
    SENSEX?: MarketIndex;
  };
  error?: string;
  detail?: string;
  message?: string;
}

interface DashboardResponse {
  success: boolean;
  data?: {
    watchlist_count?: number;
    alerts_count?: number;
  };
  error?: string;
  detail?: string;
  message?: string;
}

interface Card {
  title: string;
  value: number;
  displayValue?: string;
  change: string;
  subtitle: string;
  icon: typeof TrendingUp;
  color: string;
  iconBackground: string;
}

function formatPrice(value: number) {
  return new Intl.NumberFormat("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

export default function DashboardCards() {
  const [nifty, setNifty] =
    useState<MarketIndex | null>(null);

  const [sensex, setSensex] =
    useState<MarketIndex | null>(null);

  const [watchlistCount, setWatchlistCount] =
    useState(0);

  const [alertsCount, setAlertsCount] =
    useState(0);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadDashboardData() {
    try {
      setError("");

      const token =
        localStorage.getItem(
          "access_token"
        );

      const tokenType =
        localStorage.getItem(
          "token_type"
        ) || "bearer";

      /*
       * -------------------------------------------------------
       * LIVE NIFTY + SENSEX
       * -------------------------------------------------------
       */

      const indicesResponse =
        await fetch(
          `${API_BASE_URL}/api/market/live/indices`,
          {
            cache: "no-store",
          }
        );

      const indicesResult =
        (await indicesResponse.json()) as IndicesResponse;

      if (indicesResponse.ok) {
        setNifty(
          indicesResult.data?.["NIFTY 50"] ??
            null
        );

        setSensex(
          indicesResult.data?.SENSEX ??
            null
        );
      }

      /*
       * -------------------------------------------------------
       * USER DASHBOARD DATA
       * -------------------------------------------------------
       */

      if (token) {
        const dashboardResponse =
          await fetch(
            `${API_BASE_URL}/dashboard`,
            {
              cache: "no-store",
              headers: {
                Authorization:
                  `${tokenType} ${token}`,
              },
            }
          );

        const dashboardResult =
          (await dashboardResponse.json()) as DashboardResponse;

        if (dashboardResponse.ok) {
          setWatchlistCount(
            dashboardResult.data
              ?.watchlist_count ?? 0
          );

          setAlertsCount(
            dashboardResult.data
              ?.alerts_count ?? 0
          );
        }
      }
    } catch (err) {
      console.error(
        "Dashboard market cards error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load market overview."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboardData();

    /*
     * Refresh live market values every 60 seconds.
     */
    const interval =
      window.setInterval(
        loadDashboardData,
        60_000
      );

    return () => {
      window.clearInterval(
        interval
      );
    };
  }, []);

  /*
   * ---------------------------------------------------------
   * LOADING STATE
   * ---------------------------------------------------------
   */

  if (loading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map((item) => (
          <div
            key={item}
            className="h-52 animate-pulse rounded-3xl border border-white/10 bg-white/5"
          />
        ))}
      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * MARKET CARDS
   * ---------------------------------------------------------
   */

  const niftyChange =
    nifty?.change_percent ?? 0;

  const sensexChange =
    sensex?.change_percent ?? 0;

  const cards: Card[] = [
    {
      title: "NIFTY 50",
      value: nifty?.price ?? 0,
      displayValue: nifty
        ? formatPrice(nifty.price)
        : "â€”",
      change: nifty
        ? formatPercent(niftyChange)
        : "â€”",
      subtitle: "Live Market Index",
      icon:
        niftyChange >= 0
          ? TrendingUp
          : TrendingDown,
      color:
        niftyChange >= 0
          ? "text-green-400"
          : "text-red-400",
      iconBackground:
        niftyChange >= 0
          ? "bg-green-500/10"
          : "bg-red-500/10",
    },

    {
      title: "SENSEX",
      value: sensex?.price ?? 0,
      displayValue: sensex
        ? formatPrice(sensex.price)
        : "â€”",
      change: sensex
        ? formatPercent(sensexChange)
        : "â€”",
      subtitle: "Live Market Index",
      icon:
        sensexChange >= 0
          ? TrendingUp
          : TrendingDown,
      color:
        sensexChange >= 0
          ? "text-green-400"
          : "text-red-400",
      iconBackground:
        sensexChange >= 0
          ? "bg-green-500/10"
          : "bg-red-500/10",
    },

    {
      title: "WATCHLIST",
      value: watchlistCount,
      displayValue:
        watchlistCount.toString(),
      change:
        watchlistCount > 0
          ? `${watchlistCount} tracked`
          : "0 tracked",
      subtitle: "Stocks You're Tracking",
      icon: Eye,
      color: "text-cyan-400",
      iconBackground:
        "bg-cyan-500/10",
    },

    {
      title: "PRICE ALERTS",
      value: alertsCount,
      displayValue:
        alertsCount.toString(),
      change:
        alertsCount > 0
          ? `${alertsCount} active`
          : "No active alerts",
      subtitle: "Market Alerts",
      icon: BellRing,
      color: "text-blue-400",
      iconBackground:
        "bg-blue-500/10",
    },
  ];

  return (
    <div className="space-y-3">
      {error && (
        <div className="rounded-2xl border border-yellow-500/20 bg-yellow-500/5 px-4 py-3 text-sm text-yellow-300">
          Market data temporarily unavailable.
          Please refresh the dashboard.
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <div
              key={card.title}
              className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:border-blue-500/40 hover:shadow-2xl hover:shadow-blue-500/10"
            >
              {/* Background glow */}
              <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-blue-500/10 blur-3xl transition-all duration-300 group-hover:bg-blue-500/20" />

              <div className="relative flex items-start justify-between">
                <div>
                  <p className="text-xs uppercase tracking-widest text-slate-400">
                    {card.title}
                  </p>

                  <h2 className="mt-4 text-3xl font-extrabold tracking-tight text-white">
                    {card.title ===
                      "NIFTY 50" ||
                    card.title ===
                      "SENSEX"
                      ? "â‚¹"
                      : ""}

                    {card.displayValue ??
                      "â€”"}
                  </h2>

                  <div className="mt-4 flex items-center gap-2">
                    <span
                      className={`font-semibold ${card.color}`}
                    >
                      {card.change}
                    </span>

                    <span className="text-sm text-slate-500">
                      {card.subtitle}
                    </span>
                  </div>
                </div>

                <div
                  className={`rounded-2xl p-4 ${card.iconBackground}`}
                >
                  <Icon
                    className={`h-7 w-7 ${card.color}`}
                  />
                </div>
              </div>

              {/* Mini visual bars */}
              <div className="relative mt-8 flex items-end gap-1">
                {[
                  30,
                  42,
                  36,
                  52,
                  60,
                  70,
                  85,
                ].map(
                  (height, index) => (
                    <div
                      key={index}
                      className="w-full rounded-full bg-blue-500/30 transition-all duration-300 group-hover:bg-blue-400/40"
                      style={{
                        height:
                          `${height / 3}px`,
                      }}
                    />
                  )
                )}
              </div>

              {/* Data source */}
              {(card.title ===
                "NIFTY 50" ||
                card.title ===
                  "SENSEX") &&
                (nifty ||
                  sensex) && (
                  <div className="mt-3 text-[11px] text-slate-600">
                    Live market data
                  </div>
                )}
            </div>
          );
        })}
      </div>
    </div>
  );
}