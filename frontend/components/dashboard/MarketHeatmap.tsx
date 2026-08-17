"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";

type StockData = {
  symbol: string;
  changePercent: number;
};

const stocks = [
  {
    symbol: "RELIANCE",
    size: "col-span-2 row-span-2",
  },
  {
    symbol: "TCS",
    size: "",
  },
  {
    symbol: "INFY",
    size: "",
  },
  {
    symbol: "HDFCBANK",
    size: "",
  },
  {
    symbol: "ICICIBANK",
    size: "",
  },
  {
    symbol: "ITC",
    size: "",
  },
  {
    symbol: "LT",
    size: "",
  },
  {
    symbol: "SBIN",
    size: "",
  },
];

export default function MarketHeatmap() {
  const [marketData, setMarketData] = useState<
    StockData[]
  >([]);

  const [loading, setLoading] = useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] = useState("");

  const fetchHeatmapData = async () => {
    try {
      setError("");

      const results = await Promise.all(
        stocks.map(async (stock) => {
          const response = await fetch(
            `https://finpilot-ai-q4nk.onrender.com/stocks/live/${stock.symbol}`,
            {
              cache: "no-store",
            }
          );

          if (!response.ok) {
            throw new Error(
              `Unable to fetch ${stock.symbol}`
            );
          }

          const result = await response.json();

          if (!result.success || !result.data) {
            throw new Error(
              `Invalid data for ${stock.symbol}`
            );
          }

          const changePercent = Number(
            String(
              result.data["10. change percent"]
            ).replace("%", "")
          );

          return {
            symbol: stock.symbol,
            changePercent,
          };
        })
      );

      setMarketData(results);
    } catch (err) {
      console.error(
        "Market Heatmap error:",
        err
      );

      setError(
        "Unable to load live market data."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHeatmapData();

    // Refresh every 5 minutes
    const interval = setInterval(
      fetchHeatmapData,
      5 * 60 * 1000
    );

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchHeatmapData();
  };

  const getStockChange = (
    symbol: string
  ) => {
    return (
      marketData.find(
        (stock) => stock.symbol === symbol
      )?.changePercent ?? 0
    );
  };

  const getBackgroundColor = (
    change: number
  ) => {
    if (change >= 2) {
      return "bg-green-600";
    }

    if (change >= 1) {
      return "bg-green-500";
    }

    if (change > 0) {
      return "bg-green-400";
    }

    if (change <= -2) {
      return "bg-red-500";
    }

    return "bg-red-400";
  };

  const formatChange = (
    change: number
  ) => {
    return `${change >= 0 ? "+" : ""}${change.toFixed(
      2
    )}%`;
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold">
            Market Heatmap
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Live performance across major stocks
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="rounded-xl border border-white/10 bg-white/5 p-2 transition hover:bg-white/10 disabled:opacity-50"
          title="Refresh market data"
        >
          <RefreshCw
            size={18}
            className={
              refreshing
                ? "animate-spin"
                : ""
            }
          />
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="grid auto-rows-[110px] grid-cols-4 gap-4">
          {stocks.map((stock) => (
            <div
              key={stock.symbol}
              className={`${stock.size} animate-pulse rounded-2xl bg-slate-800`}
            />
          ))}
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="rounded-2xl border border-red-500/20 bg-red-950/20 p-5 text-sm text-red-300">
          {error}

          <button
            onClick={handleRefresh}
            className="mt-3 block rounded-lg bg-red-500/10 px-3 py-2 hover:bg-red-500/20"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Heatmap */}
      {!loading && !error && (
        <>
          <div className="grid auto-rows-[110px] grid-cols-4 gap-4">
            {stocks.map((stock) => {
              const change =
                getStockChange(
                  stock.symbol
                );

              const backgroundColor =
                getBackgroundColor(
                  change
                );

              return (
                <div
                  key={stock.symbol}
                  className={`${backgroundColor} ${stock.size}
                    flex cursor-pointer flex-col justify-between rounded-2xl
                    p-5 transition-all duration-300
                    hover:scale-105 hover:shadow-xl`}
                >
                  <h3 className="text-lg font-bold text-white">
                    {stock.symbol}
                  </h3>

                  <p className="text-2xl font-bold text-white">
                    {formatChange(change)}
                  </p>
                </div>
              );
            })}
          </div>

          <p className="mt-5 text-right text-xs text-slate-600">
            Market data â€¢ Auto-refreshes every 5 minutes
          </p>
        </>
      )}
    </div>
  );
}