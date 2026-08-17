"use client";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import { useCallback, useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://finpilot-ai-q4nk.onrender.com";

interface PortfolioItem {
  id: number;
  stock_symbol: string;
  quantity: number;
  purchase_price: number;
  live_price: number;
  invested_amount: number;
  current_value: number;
  profit_loss: number;
  return_percentage: number;
}

interface PortfolioSummary {
  total_invested: number;
  current_value: number;
  profit_loss: number;
  return_percentage: number;
  holdings: number;
  items: PortfolioItem[];
}

export default function PortfolioChart() {
  const [summary, setSummary] =
    useState<PortfolioSummary | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const fetchPortfolioSummary =
    useCallback(async () => {
      try {
        setLoading(true);
        setError("");

        const token =
          localStorage.getItem(
            "access_token"
          );

        const tokenType =
          localStorage.getItem(
            "token_type"
          ) || "bearer";

        if (!token) {
          throw new Error(
            "Please login to view your portfolio."
          );
        }

        const response = await fetch(
          `${API_BASE_URL}/portfolio/summary`,
          {
            cache: "no-store",
            headers: {
              Authorization:
                `${tokenType} ${token}`,
            },
          }
        );

        const result =
          await response.json();

        if (!response.ok) {
          throw new Error(
            result?.error ||
              result?.detail ||
              result?.message ||
              "Unable to load portfolio."
          );
        }

        setSummary(result?.data ?? null);

      } catch (err) {
        console.error(
          "Portfolio summary error:",
          err
        );

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load portfolio."
        );
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    fetchPortfolioSummary();
  }, [fetchPortfolioSummary]);

  // -----------------------------------------
  // Loading
  // -----------------------------------------

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="mb-8 h-20 rounded-2xl bg-white/5" />

        <div className="h-[360px] rounded-2xl bg-white/5" />
      </div>
    );
  }

  // -----------------------------------------
  // Error
  // -----------------------------------------

  if (error) {
    return (
      <div>
        <p className="text-sm uppercase tracking-widest text-slate-400">
          Portfolio Growth
        </p>

        <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-300">
          {error}
        </div>
      </div>
    );
  }

  // -----------------------------------------
  // Empty Portfolio
  // -----------------------------------------

  if (
    !summary ||
    summary.holdings === 0
  ) {
    return (
      <div>
        <p className="text-sm uppercase tracking-widest text-slate-400">
          Portfolio Growth
        </p>

        <h2 className="mt-3 text-4xl font-bold">
          â‚¹0.00
        </h2>

        <p className="mt-2 text-slate-500">
          Add your first holding to start
          tracking portfolio performance.
        </p>

        <div className="mt-8 flex h-[300px] items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.02]">
          <p className="text-sm text-slate-500">
            No portfolio holdings yet
          </p>
        </div>
      </div>
    );
  }

  // -----------------------------------------
  // Create chart data
  // -----------------------------------------

  const chartData =
    summary.items.map((item) => ({
      symbol: item.stock_symbol,
      value: item.current_value,
    }));

  const positive =
    summary.profit_loss >= 0;

  return (
    <div>

      {/* Header */}

      <div className="mb-8 flex items-center justify-between">

        <div>

          <p className="text-sm uppercase tracking-widest text-slate-400">
            Portfolio Value
          </p>

          <h2 className="mt-3 text-4xl font-bold">
            â‚¹
            {summary.current_value.toLocaleString(
              "en-IN",
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}
          </h2>

          <p
            className={`mt-2 font-medium ${
              positive
                ? "text-green-400"
                : "text-red-400"
            }`}
          >
            {positive ? "â–²" : "â–¼"}{" "}
            â‚¹
            {Math.abs(
              summary.profit_loss
            ).toLocaleString(
              "en-IN",
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}{" "}
            (
            {summary.return_percentage.toFixed(
              2
            )}
            %)
          </p>

        </div>

        <div className="rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 px-6 py-4">

          <p className="text-sm text-slate-400">
            Invested
          </p>

          <h3 className="text-2xl font-bold">
            â‚¹
            {summary.total_invested.toLocaleString(
              "en-IN",
              {
                maximumFractionDigits: 2,
              }
            )}
          </h3>

        </div>

      </div>

      {/* Chart */}

      <div className="h-[360px]">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <AreaChart
            data={chartData}
          >

            <defs>

              <linearGradient
                id="portfolioGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >

                <stop
                  offset="0%"
                  stopColor="#3b82f6"
                  stopOpacity={0.4}
                />

                <stop
                  offset="100%"
                  stopColor="#3b82f6"
                  stopOpacity={0}
                />

              </linearGradient>

            </defs>

            <CartesianGrid
              stroke="#1e293b"
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="symbol"
              stroke="#94a3b8"
            />

            <YAxis
              stroke="#94a3b8"
            />

            <Tooltip
              formatter={(value) =>
                `â‚¹${Number(
                  value
                ).toLocaleString(
                  "en-IN"
                )}`
              }
            />

            <Area
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={4}
              fill="url(#portfolioGradient)"
            />

          </AreaChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}