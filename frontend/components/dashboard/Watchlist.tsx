"use client";

import {
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  Trash2,
  RefreshCw,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

interface WatchlistItem {
  id: number;
  stock_symbol: string;
  created_at: string;
}

interface LiveStock {
  symbol: string;
  price: string;
  change: string;
  changePercent: string;
}

interface DisplayStock {
  id: number;
  symbol: string;
  price: string;
  change: string;
  changePercent: string;
}

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState<
    WatchlistItem[]
  >([]);

  const [stocks, setStocks] = useState<
    DisplayStock[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [showAdd, setShowAdd] = useState(false);
  const [newSymbol, setNewSymbol] = useState("");
  const [adding, setAdding] = useState(false);

  // -----------------------------------------
  // Fetch Watchlist
  // -----------------------------------------

  const fetchWatchlist = useCallback(async () => {
    try {
      setError("");

      const token = localStorage.getItem(
        "access_token"
      );

      const tokenType =
        localStorage.getItem("token_type") ||
        "bearer";

      if (!token) {
        throw new Error(
          "Please login to view your watchlist."
        );
      }

      const response = await fetch(
        `${API_BASE_URL}/watchlist/?page=1&limit=10`,
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
            "Unable to load watchlist."
        );
      }

      const items =
        result?.data?.items;

      if (!Array.isArray(items)) {
        throw new Error(
          "Invalid watchlist response."
        );
      }

      setWatchlist(items);

    } catch (err) {
      console.error(
        "Watchlist error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load watchlist."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // -----------------------------------------
  // Fetch Live Stock Data
  // -----------------------------------------

  const fetchLiveStocks = useCallback(
    async (items: WatchlistItem[]) => {
      const results: DisplayStock[] = [];

      for (const item of items) {
        try {
          const response = await fetch(
            `${API_BASE_URL}/stocks/live/${item.stock_symbol}`,
            {
              cache: "no-store",
            }
          );

          const result =
            await response.json();

          if (!response.ok) {
            continue;
          }

          const data = result?.data;

          if (!data) {
            continue;
          }

          const liveStock: LiveStock = {
            symbol:
              data["01. symbol"] ||
              item.stock_symbol,

            price:
              data["05. price"] ||
              "0",

            change:
              data["09. change"] ||
              "0",

            changePercent:
              data["10. change percent"] ||
              "0%",
          };

          results.push({
            id: item.id,
            symbol: item.stock_symbol,
            price: liveStock.price,
            change: liveStock.change,
            changePercent:
              liveStock.changePercent,
          });

        } catch (err) {
          console.error(
            `Unable to load ${item.stock_symbol}:`,
            err
          );
        }
      }

      setStocks(results);
    },
    []
  );

  // -----------------------------------------
  // Load Watchlist
  // -----------------------------------------

  const loadWatchlist = useCallback(
    async () => {
      setRefreshing(true);

      await fetchWatchlist();

      setRefreshing(false);
    },
    [fetchWatchlist]
  );

  // -----------------------------------------
  // Initial Load
  // -----------------------------------------

  useEffect(() => {
    fetchWatchlist();
  }, [fetchWatchlist]);

  // -----------------------------------------
  // Load Live Prices after Watchlist changes
  // -----------------------------------------

  useEffect(() => {
    if (watchlist.length === 0) {
      setStocks([]);
      return;
    }

    fetchLiveStocks(watchlist);
  }, [watchlist, fetchLiveStocks]);

  // -----------------------------------------
  // Add Stock
  // -----------------------------------------

  async function handleAddStock() {
    const symbol =
      newSymbol.trim().toUpperCase();

    if (!symbol) {
      return;
    }

    try {
      setAdding(true);
      setError("");

      const token = localStorage.getItem(
        "access_token"
      );

      const tokenType =
        localStorage.getItem("token_type") ||
        "bearer";

      if (!token) {
        throw new Error(
          "Please login before adding stocks."
        );
      }

      const response = await fetch(
        `${API_BASE_URL}/watchlist/`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `${tokenType} ${token}`,
          },

          body: JSON.stringify({
            stock_symbol: symbol,
          }),
        }
      );

      const result =
        await response.json();

      if (!response.ok) {
        throw new Error(
          result?.error ||
            result?.detail ||
            result?.message ||
            "Unable to add stock."
        );
      }

      setNewSymbol("");
      setShowAdd(false);

      await fetchWatchlist();

    } catch (err) {
      console.error(
        "Add watchlist error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to add stock."
      );
    } finally {
      setAdding(false);
    }
  }

  // -----------------------------------------
  // Delete Stock
  // -----------------------------------------

  async function handleDelete(
    watchlistId: number
  ) {
    try {
      setError("");

      const token = localStorage.getItem(
        "access_token"
      );

      const tokenType =
        localStorage.getItem("token_type") ||
        "bearer";

      if (!token) {
        throw new Error(
          "Please login before removing stocks."
        );
      }

      const response = await fetch(
        `${API_BASE_URL}/watchlist/${watchlistId}`,
        {
          method: "DELETE",

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
            "Unable to remove stock."
        );
      }

      await fetchWatchlist();

    } catch (err) {
      console.error(
        "Delete watchlist error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to remove stock."
      );
    }
  }

  // -----------------------------------------
  // Loading
  // -----------------------------------------

  if (loading) {
    return (
      <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">
              Watchlist
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Your favorite market assets
            </p>
          </div>

          <RefreshCw
            size={18}
            className="animate-spin text-slate-500"
          />
        </div>

        <div className="mt-6 space-y-3">
          {[1, 2, 3].map((item) => (
            <div
              key={item}
              className="h-20 animate-pulse rounded-2xl bg-white/5"
            />
          ))}
        </div>
      </div>
    );
  }

  // -----------------------------------------
  // Render
  // -----------------------------------------

  return (
    <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-6">

      {/* Header */}

      <div className="mb-6 flex items-center justify-between">

        <div>
          <h2 className="text-xl font-bold">
            Watchlist
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Your favorite market assets
          </p>
        </div>

        <div className="flex items-center gap-2">

          <button
            onClick={loadWatchlist}
            disabled={refreshing}
            className="rounded-xl border border-white/10 bg-white/5 p-2 transition hover:bg-white/10 disabled:opacity-50"
            title="Refresh watchlist"
          >
            <RefreshCw
              size={16}
              className={
                refreshing
                  ? "animate-spin"
                  : ""
              }
            />
          </button>

          <button
            onClick={() =>
              setShowAdd(!showAdd)
            }
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium transition hover:bg-blue-500"
          >
            <Plus size={16} />

            Add
          </button>

        </div>
      </div>

      {/* Add Stock */}

      {showAdd && (
        <div className="mb-5 rounded-2xl border border-blue-500/20 bg-blue-500/5 p-4">

          <p className="mb-3 text-sm font-medium text-slate-300">
            Add stock to your watchlist
          </p>

          <div className="flex gap-2">

            <input
              value={newSymbol}
              onChange={(event) =>
                setNewSymbol(
                  event.target.value
                )
              }
              onKeyDown={(event) => {
                if (
                  event.key === "Enter"
                ) {
                  handleAddStock();
                }
              }}
              placeholder="TCS"
              className="min-w-0 flex-1 rounded-xl border border-white/10 bg-black/20 px-4 py-2 text-sm text-white outline-none placeholder:text-slate-600 focus:border-blue-500/50"
            />

            <button
              onClick={handleAddStock}
              disabled={
                adding ||
                !newSymbol.trim()
              }
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {adding
                ? "Adding..."
                : "Add"}
            </button>

          </div>

          <p className="mt-2 text-xs text-slate-500">
            Available stocks: TCS, RELIANCE,
            INFY, HDFCBANK, ICICIBANK, SBIN
          </p>
        </div>
      )}

      {/* Error */}

      {error && (
        <div className="mb-5 rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Empty State */}

      {watchlist.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.02] p-8 text-center">

          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/10 text-blue-400">
            <Plus size={22} />
          </div>

          <h3 className="mt-4 font-semibold">
            Your watchlist is empty
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Add stocks you want to monitor.
          </p>

          <button
            onClick={() =>
              setShowAdd(true)
            }
            className="mt-4 rounded-xl bg-blue-600 px-5 py-2 text-sm font-medium hover:bg-blue-500"
          >
            Add Your First Stock
          </button>

        </div>
      ) : (
        <div className="space-y-4">

          {watchlist.map((item) => {

            const stock = stocks.find(
              (current) =>
                current.id === item.id
            );

            const change =
              stock?.change ?? "0";

            const changePercent =
              stock?.changePercent ?? "0%";

            const price =
              stock?.price ?? "--";

            const positive =
              !change.startsWith("-") &&
              Number(change) >= 0;

            return (
              <div
                key={item.id}
                className="group flex items-center justify-between rounded-2xl border border-transparent bg-slate-900/50 p-4 transition-all duration-300 hover:border-blue-500/30 hover:bg-slate-900"
              >

                {/* Left */}

                <Link
                  href={`/stocks/${item.stock_symbol}`}
                  className="flex min-w-0 items-center gap-4"
                >

                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 text-sm font-bold text-white">
                    {item.stock_symbol.slice(
                      0,
                      2
                    )}
                  </div>

                  <div className="min-w-0">
                    <h3 className="font-semibold">
                      {item.stock_symbol}
                    </h3>

                    <p className="text-sm text-slate-400">
                      NSE
                    </p>
                  </div>

                </Link>

                {/* Right */}

                <div className="flex items-center gap-4">

                  <Link
                    href={`/stocks/${item.stock_symbol}`}
                    className="text-right"
                  >
                    <h3 className="font-semibold">
                      {price !== "--"
                        ? `₹${price}`
                        : "--"}
                    </h3>

                    <div
                      className={`mt-1 flex items-center justify-end gap-1 text-sm font-medium ${
                        positive
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
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

                      {changePercent}
                    </div>
                  </Link>

                  <button
                    onClick={() =>
                      handleDelete(
                        item.id
                      )
                    }
                    className="rounded-lg p-2 text-slate-600 opacity-0 transition hover:bg-red-500/10 hover:text-red-400 group-hover:opacity-100"
                    title="Remove from watchlist"
                  >
                    <Trash2 size={16} />
                  </button>

                </div>
              </div>
            );
          })}

        </div>
      )}

    </div>
  );
}