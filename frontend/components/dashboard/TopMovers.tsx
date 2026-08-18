"use client";

import { useCallback, useEffect, useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
} from "lucide-react";

type StockData = {
  symbol: string;
  company: string;
  price: number | null;
  change: number | null;
  changePercent: number | null;
  marketStatus: string;
  dataSource: string;
};

const stocks = [
  {
    symbol: "RELIANCE",
    company: "Reliance Industries",
  },
  {
    symbol: "TCS",
    company: "Tata Consultancy Services",
  },
  {
    symbol: "HDFCBANK",
    company: "HDFC Bank",
  },
  {
    symbol: "INFY",
    company: "Infosys",
  },
  {
    symbol: "ICICIBANK",
    company: "ICICI Bank",
  },
  {
    symbol: "SBIN",
    company: "State Bank of India",
  },
];

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://finpilot-ai-q4nk.onrender.com";

export default function TopMovers() {
  const [marketData, setMarketData] =
    useState<StockData[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState("");

  // ============================================================
  // FETCH QUOTE FOR ONE STOCK
  // ============================================================

  const fetchStockQuote = async (
    stock: {
      symbol: string;
      company: string;
    }
  ): Promise<StockData | null> => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/market/live/quote/${stock.symbol}`,
        {
          method: "GET",
          cache: "no-store",
        }
      );

      if (!response.ok) {
        console.error(
          `Quote request failed for ${stock.symbol}:`,
          response.status
        );

        return null;
      }

      const result = await response.json();

      if (
        !result ||
        result.success !== true ||
        !result.data
      ) {
        console.error(
          `Invalid quote response for ${stock.symbol}:`,
          result
        );

        return null;
      }

      const data = result.data;

      // --------------------------------------------------------
      // PRICE
      // --------------------------------------------------------

      const rawPrice =
        data.price ??
        data.close ??
        data["05. price"];

      const price =
        rawPrice !== null &&
        rawPrice !== undefined
          ? Number(rawPrice)
          : null;

      // --------------------------------------------------------
      // CHANGE
      // --------------------------------------------------------

      const rawChange =
        data.change ??
        data["09. change"];

      const change =
        rawChange !== null &&
        rawChange !== undefined
          ? Number(rawChange)
          : null;

      // --------------------------------------------------------
      // CHANGE %
      // --------------------------------------------------------

      const rawChangePercent =
        data.change_percent ??
        data.changePercent ??
        data.change_p ??
        data["10. change percent"];

      let changePercent: number | null =
        null;

      if (
        rawChangePercent !== null &&
        rawChangePercent !== undefined
      ) {
        const parsed = Number(
          String(rawChangePercent).replace(
            "%",
            ""
          )
        );

        if (Number.isFinite(parsed)) {
          changePercent = parsed;
        }
      }

      // --------------------------------------------------------
      // Reject invalid price
      // --------------------------------------------------------

      if (
        price === null ||
        !Number.isFinite(price) ||
        price <= 0
      ) {
        console.warn(
          `No valid price for ${stock.symbol}`,
          data
        );

        return null;
      }

      return {
        symbol: stock.symbol,
        company: stock.company,

        price,

        change:
          change !== null &&
          Number.isFinite(change)
            ? change
            : null,

        changePercent,

        marketStatus:
          data.market_status ||
          "latest_available",

        dataSource:
          data.data_source ||
          "Market Data",
      };
    } catch (error) {
      console.error(
        `Error loading ${stock.symbol}:`,
        error
      );

      return null;
    }
  };

  // ============================================================
  // FETCH ALL MARKET DATA
  // ============================================================

  const fetchMarketData = useCallback(
    async () => {
      try {
        setError("");

        const results =
          await Promise.all(
            stocks.map((stock) =>
              fetchStockQuote(stock)
            )
          );

        const validResults =
          results.filter(
            (
              item
            ): item is StockData =>
              item !== null
          );

        if (
          validResults.length === 0
        ) {
          throw new Error(
            "Unable to load Indian stock prices from the backend."
          );
        }

        setMarketData(
          validResults
        );
      } catch (err) {
        console.error(
          "Top Movers error:",
          err
        );

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load Indian market data."
        );
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    []
  );

  // ============================================================
  // INITIAL LOAD + AUTO REFRESH
  // ============================================================

  useEffect(() => {
    fetchMarketData();

    const interval =
      setInterval(
        fetchMarketData,
        5 * 60 * 1000
      );

    return () => {
      clearInterval(interval);
    };
  }, [fetchMarketData]);

  // ============================================================
  // MANUAL REFRESH
  // ============================================================

  const handleRefresh = () => {
    if (refreshing) {
      return;
    }

    setRefreshing(true);

    fetchMarketData();
  };

  // ============================================================
  // TOP GAINERS
  // ============================================================

  const gainers =
    [...marketData]
      .filter(
        (stock) =>
          stock.changePercent !== null &&
          stock.changePercent > 0
      )
      .sort(
        (a, b) =>
          (b.changePercent ?? 0) -
          (a.changePercent ?? 0)
      )
      .slice(0, 3);

  // ============================================================
  // TOP LOSERS
  // ============================================================

  const losers =
    [...marketData]
      .filter(
        (stock) =>
          stock.changePercent !== null &&
          stock.changePercent < 0
      )
      .sort(
        (a, b) =>
          (a.changePercent ?? 0) -
          (b.changePercent ?? 0)
      )
      .slice(0, 3);

  // ============================================================
  // FORMAT PRICE
  // ============================================================

  const formatPrice = (
    value: number | null
  ) => {
    if (
      value === null ||
      !Number.isFinite(value)
    ) {
      return "--";
    }

    return `\u20B9${value.toLocaleString(
      "en-IN",
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    )}`;
  };

  // ============================================================
  // FORMAT CHANGE
  // ============================================================

  const formatChange = (
    value: number | null
  ) => {
    if (
      value === null ||
      !Number.isFinite(value)
    ) {
      return "--";
    }

    return `${value >= 0 ? "+" : ""}Ã¢â€šÂ¹${Math.abs(
      value
    ).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  // ============================================================
  // FORMAT PERCENT
  // ============================================================

  const formatPercent = (
    value: number | null
  ) => {
    if (
      value === null ||
      !Number.isFinite(value)
    ) {
      return "--";
    }

    return `${
      value >= 0 ? "+" : ""
    }${value.toFixed(2)}%`;
  };

  // ============================================================
  // STOCK ROW
  // ============================================================

  const StockRow = ({
    stock,
    positive,
  }: {
    stock: StockData;
    positive: boolean;
  }) => {
    return (
      <div
        className="
          group
          flex
          items-center
          justify-between
          rounded-2xl
          border
          border-white/5
          bg-slate-900/50
          p-4
          transition
          duration-200
          hover:border-white/10
          hover:bg-slate-900
        "
      >
        {/* LEFT */}
        <div className="flex min-w-0 items-center gap-3">
          {/* ICON */}
          <div
            className={`
              flex
              h-10
              w-10
              shrink-0
              items-center
              justify-center
              rounded-xl
              ${
                positive
                  ? "bg-green-500/10"
                  : "bg-red-500/10"
              }
            `}
          >
            {positive ? (
              <TrendingUp
                size={18}
                className="text-green-400"
              />
            ) : (
              <TrendingDown
                size={18}
                className="text-red-400"
              />
            )}
          </div>

          {/* COMPANY */}
          <div className="min-w-0">
            <h4 className="font-semibold text-white">
              {stock.symbol}
            </h4>

            <p className="truncate text-sm text-slate-400">
              {stock.company}
            </p>

            <p className="mt-1 text-xs text-slate-600">
              NSE Ã¢â‚¬Â¢ India
            </p>
          </div>
        </div>

        {/* RIGHT */}
        <div className="ml-4 shrink-0 text-right">
          <p className="font-semibold text-white">
            {formatPrice(stock.price)}
          </p>

          <div
            className={`
              mt-1
              flex
              items-center
              justify-end
              gap-1
              text-sm
              font-medium
              ${
                positive
                  ? "text-green-400"
                  : "text-red-400"
              }
            `}
          >
            {positive ? (
              <ArrowUpRight
                size={16}
              />
            ) : (
              <ArrowDownRight
                size={16}
              />
            )}

            <span>
              {formatChange(
                stock.change
              )}
            </span>

            <span>
              (
              {formatPercent(
                stock.changePercent
              )}
              )
            </span>
          </div>
        </div>
      </div>
    );
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <div>
      {/* HEADER */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">
            Top Movers
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Indian market Ã¢â‚¬Â¢ NSE
          </p>
        </div>

        {/* REFRESH */}
        <button
          type="button"
          onClick={
            handleRefresh
          }
          disabled={
            refreshing
          }
          className="
            rounded-xl
            border
            border-white/10
            bg-white/5
            p-2
            text-slate-300
            transition
            hover:bg-white/10
            hover:text-white
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
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

      {/* LOADING */}
      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map(
            (item) => (
              <div
                key={item}
                className="
                  h-20
                  animate-pulse
                  rounded-2xl
                  bg-slate-900/50
                "
              />
            )
          )}
        </div>
      )}

      {/* ERROR */}
      {!loading &&
        error && (
          <div
            className="
              rounded-2xl
              border
              border-red-500/20
              bg-red-950/20
              p-5
              text-sm
              text-red-300
            "
          >
            <p>{error}</p>

            <button
              type="button"
              onClick={
                handleRefresh
              }
              className="
                mt-3
                rounded-lg
                bg-red-500/10
                px-3
                py-2
                text-red-300
                transition
                hover:bg-red-500/20
              "
            >
              Try Again
            </button>
          </div>
        )}

      {/* MARKET DATA */}
      {!loading &&
        !error &&
        marketData.length > 0 && (
          <>
            {/* TOP GAINERS */}
            <div>
              <div className="mb-3 flex items-center gap-2">
                <TrendingUp
                  className="h-5 w-5 text-green-400"
                />

                <h3 className="font-semibold text-green-400">
                  Top Gainers
                </h3>
              </div>

              <div className="space-y-3">
                {gainers.length ===
                0 ? (
                  <p className="rounded-2xl bg-slate-900/50 p-4 text-sm text-slate-500">
                    No gainers available.
                  </p>
                ) : (
                  gainers.map(
                    (stock) => (
                      <StockRow
                        key={
                          stock.symbol
                        }
                        stock={
                          stock
                        }
                        positive={
                          true
                        }
                      />
                    )
                  )
                )}
              </div>
            </div>

            {/* DIVIDER */}
            <div className="my-6 border-t border-white/10" />

            {/* TOP LOSERS */}
            <div>
              <div className="mb-3 flex items-center gap-2">
                <TrendingDown
                  className="h-5 w-5 text-red-400"
                />

                <h3 className="font-semibold text-red-400">
                  Top Losers
                </h3>
              </div>

              <div className="space-y-3">
                {losers.length ===
                0 ? (
                  <p className="rounded-2xl bg-slate-900/50 p-4 text-sm text-slate-500">
                    No losers available.
                  </p>
                ) : (
                  losers.map(
                    (stock) => (
                      <StockRow
                        key={
                          stock.symbol
                        }
                        stock={
                          stock
                        }
                        positive={
                          false
                        }
                      />
                    )
                  )
                )}
              </div>
            </div>

            {/* DATA SOURCE */}
            <div className="mt-5 flex items-center justify-between">
              <p className="text-xs text-slate-600">
                Indian NSE market data
              </p>

              <p className="text-xs text-slate-600">
                Auto-refresh: 5 min
              </p>
            </div>
          </>
        )}

      {/* NO DATA */}
      {!loading &&
        !error &&
        marketData.length === 0 && (
          <div
            className="
              rounded-2xl
              bg-slate-900/50
              p-5
              text-center
              text-sm
              text-slate-500
            "
          >
            No market data available.
          </div>
        )}
    </div>
  );
}
