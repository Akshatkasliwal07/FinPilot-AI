"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { useCallback, useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

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

interface AllocationItem {
  name: string;
  value: number;
}

export default function PortfolioAllocation() {
  const [data, setData] = useState<AllocationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAllocation = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");
      const tokenType =
        localStorage.getItem("token_type") || "bearer";

      if (!token) {
        throw new Error("Please login to view your portfolio.");
      }

      const response = await fetch(
        `${API_BASE_URL}/portfolio/summary`,
        {
          cache: "no-store",
          headers: {
            Authorization: `${tokenType} ${token}`,
          },
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result?.error ||
            result?.detail ||
            result?.message ||
            "Unable to load portfolio."
        );
      }

      const summary: PortfolioSummary = result.data;

      if (!summary?.items?.length) {
        setData([]);
        return;
      }

      const totalValue = summary.items.reduce(
        (total, item) => total + item.current_value,
        0
      );

      const allocation = summary.items.map((item) => ({
        name: item.stock_symbol,
        value:
          totalValue > 0
            ? (item.current_value / totalValue) * 100
            : 0,
      }));

      setData(allocation);
    } catch (err) {
      console.error("Portfolio allocation error:", err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load portfolio allocation."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllocation();

    const interval = setInterval(
      fetchAllocation,
      5 * 60 * 1000
    );

    return () => clearInterval(interval);
  }, [fetchAllocation]);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-xl font-bold">
          Portfolio Allocation
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Distribution of your current holdings
        </p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex h-72 items-center justify-center">
          <p className="text-slate-400">
            Loading portfolio allocation...
          </p>
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Empty portfolio */}
      {!loading && !error && data.length === 0 && (
        <div className="flex h-72 items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.02]">
          <p className="text-sm text-slate-500">
            Add a portfolio holding to see allocation.
          </p>
        </div>
      )}

      {/* Chart */}
      {!loading && !error && data.length > 0 && (
        <>
          <div className="h-72">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <PieChart>
                <Pie
                  data={data}
                  innerRadius={75}
                  outerRadius={105}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {data.map((item, index) => (
                    <Cell
                      key={item.name}
                      fill={`hsl(${210 + index * 45}, 80%, 55%)`}
                    />
                  ))}
                </Pie>

                <Tooltip
                  formatter={(value) =>
                    `${Number(value).toFixed(2)}%`
                  }
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="mt-6 space-y-4">
            {data.map((item, index) => (
              <div
                key={item.name}
                className="flex items-center justify-between rounded-2xl bg-slate-900/50 p-4"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="h-4 w-4 rounded-full"
                    style={{
                      backgroundColor: `hsl(${
                        210 + index * 45
                      }, 80%, 55%)`,
                    }}
                  />

                  <span className="font-medium">
                    {item.name}
                  </span>
                </div>

                <div className="text-right">
                  <p className="font-semibold">
                    {item.value.toFixed(2)}%
                  </p>

                  <p className="text-xs text-slate-400">
                    Allocation
                  </p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}