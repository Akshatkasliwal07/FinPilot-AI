"use client";

import {
  Bell,
  BellRing,
  Plus,
  Trash2,
  X,
  RefreshCw,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://finpilot-ai-q4nk.onrender.com";

interface PriceAlert {
  id: number;
  stock_symbol: string;
  target_price: number;
  condition: string;
  is_triggered: boolean;
  created_at: string;
}

export default function PriceAlerts() {
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [checking, setChecking] =
    useState(false);

  const [error, setError] =
    useState("");

  const [showForm, setShowForm] =
    useState(false);

  const [stockSymbol, setStockSymbol] =
    useState("");

  const [targetPrice, setTargetPrice] =
    useState("");

  const [condition, setCondition] =
    useState<"above" | "below">("above");

  const [creating, setCreating] =
    useState(false);

  // -----------------------------------------
  // Get authentication token
  // -----------------------------------------

  const getAuthHeaders = () => {
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
        "Please login to manage price alerts."
      );
    }

    return {
      Authorization:
        `${tokenType} ${token}`,
      "Content-Type":
        "application/json",
    };
  };

  // -----------------------------------------
  // Fetch alerts
  // -----------------------------------------

  const fetchAlerts =
    useCallback(async () => {
      try {
        setLoading(true);
        setError("");

        const headers =
          getAuthHeaders();

        const response =
          await fetch(
            `${API_BASE_URL}/price-alerts/?page=1&limit=100`,
            {
              method: "GET",
              headers,
              cache: "no-store",
            }
          );

        const result =
          await response.json();

        if (!response.ok) {
          throw new Error(
            result?.error ||
              result?.detail ||
              result?.message ||
              "Unable to load price alerts."
          );
        }

        setAlerts(
          result?.data?.items ?? []
        );

      } catch (err) {
        console.error(
          "Price alerts error:",
          err
        );

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load price alerts."
        );
      } finally {
        setLoading(false);
      }
    }, []);

  // -----------------------------------------
  // Check live prices
  // -----------------------------------------

  const checkAlerts =
    useCallback(async () => {
      try {
        setChecking(true);

        const headers =
          getAuthHeaders();

        const response =
          await fetch(
            `${API_BASE_URL}/price-alerts/check`,
            {
              method: "POST",
              headers,
              cache: "no-store",
            }
          );

        const result =
          await response.json();

        if (!response.ok) {
          throw new Error(
            result?.error ||
              result?.detail ||
              result?.message ||
              "Unable to check price alerts."
          );
        }

        // Refresh alerts so triggered
        // status is reflected immediately.
        await fetchAlerts();

      } catch (err) {
        console.error(
          "Check price alerts error:",
          err
        );
      } finally {
        setChecking(false);
      }
    }, [fetchAlerts]);

  // -----------------------------------------
  // Initial load
  // -----------------------------------------

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // -----------------------------------------
  // Create alert
  // -----------------------------------------

  const createAlert =
    async (
      event: React.FormEvent
    ) => {
      event.preventDefault();

      try {
        setCreating(true);
        setError("");

        const price =
          Number(targetPrice);

        if (!stockSymbol.trim()) {
          throw new Error(
            "Please enter a stock symbol."
          );
        }

        if (!price || price <= 0) {
          throw new Error(
            "Please enter a valid target price."
          );
        }

        const headers =
          getAuthHeaders();

        const response =
          await fetch(
            `${API_BASE_URL}/price-alerts/`,
            {
              method: "POST",
              headers,
              body: JSON.stringify({
                stock_symbol:
                  stockSymbol
                    .trim()
                    .toUpperCase(),

                target_price: price,

                condition,
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
              "Unable to create price alert."
          );
        }

        // Reset form
        setStockSymbol("");
        setTargetPrice("");
        setCondition("above");
        setShowForm(false);

        // Reload alerts
        await fetchAlerts();

      } catch (err) {
        console.error(
          "Create price alert error:",
          err
        );

        setError(
          err instanceof Error
            ? err.message
            : "Unable to create price alert."
        );
      } finally {
        setCreating(false);
      }
    };

  // -----------------------------------------
  // Delete alert
  // -----------------------------------------

  const deleteAlert =
    async (
      alertId: number
    ) => {
      try {
        const headers =
          getAuthHeaders();

        const response =
          await fetch(
            `${API_BASE_URL}/price-alerts/${alertId}`,
            {
              method: "DELETE",
              headers,
            }
          );

        const result =
          await response.json();

        if (!response.ok) {
          throw new Error(
            result?.error ||
              result?.detail ||
              result?.message ||
              "Unable to delete alert."
          );
        }

        setAlerts(
          (current) =>
            current.filter(
              (alert) =>
                alert.id !== alertId
            )
        );

      } catch (err) {
        console.error(
          "Delete price alert error:",
          err
        );

        setError(
          err instanceof Error
            ? err.message
            : "Unable to delete alert."
        );
      }
    };

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-xl">

      {/* -------------------------------------
          Header
      -------------------------------------- */}

      <div className="flex items-center justify-between">

        <div className="flex items-center gap-3">

          <div className="rounded-xl bg-blue-500/10 p-3">
            <Bell className="h-5 w-5 text-blue-400" />
          </div>

          <div>
            <h2 className="text-xl font-bold">
              Price Alerts
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Get notified when stocks reach your target
            </p>
          </div>

        </div>

        <div className="flex gap-2">

          <button
            onClick={checkAlerts}
            disabled={checking}
            title="Check live prices"
            className="rounded-xl border border-white/10 bg-white/5 p-3 transition hover:bg-white/10 disabled:opacity-50"
          >
            <RefreshCw
              className={`h-5 w-5 ${
                checking
                  ? "animate-spin"
                  : ""
              }`}
            />
          </button>

          <button
            onClick={() =>
              setShowForm(true)
            }
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-medium transition hover:bg-blue-500"
          >
            <Plus className="h-4 w-4" />
            Add Alert
          </button>

        </div>

      </div>


      {/* -------------------------------------
          Error
      -------------------------------------- */}

      {error && (
        <div className="mt-5 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-300">
          {error}
        </div>
      )}


      {/* -------------------------------------
          Create Form
      -------------------------------------- */}

      {showForm && (
        <form
          onSubmit={createAlert}
          className="mt-6 rounded-2xl border border-blue-500/20 bg-slate-900/50 p-5"
        >

          <div className="mb-5 flex items-center justify-between">

            <h3 className="font-semibold">
              Create Price Alert
            </h3>

            <button
              type="button"
              onClick={() =>
                setShowForm(false)
              }
              className="rounded-lg p-2 hover:bg-white/10"
            >
              <X className="h-4 w-4" />
            </button>

          </div>


          <div className="grid gap-4 md:grid-cols-3">

            {/* Stock */}

            <div>
              <label className="mb-2 block text-sm text-slate-400">
                Stock Symbol
              </label>

              <input
                value={stockSymbol}
                onChange={(event) =>
                  setStockSymbol(
                    event.target.value
                  )
                }
                placeholder="TCS"
                className="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
              />
            </div>


            {/* Target */}

            <div>
              <label className="mb-2 block text-sm text-slate-400">
                Target Price
              </label>

              <input
                type="number"
                step="0.01"
                value={targetPrice}
                onChange={(event) =>
                  setTargetPrice(
                    event.target.value
                  )
                }
                placeholder="2500"
                className="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
              />
            </div>


            {/* Condition */}

            <div>
              <label className="mb-2 block text-sm text-slate-400">
                Condition
              </label>

              <select
                value={condition}
                onChange={(event) =>
                  setCondition(
                    event.target.value as
                      | "above"
                      | "below"
                  )
                }
                className="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              >
                <option value="above">
                  Price goes above
                </option>

                <option value="below">
                  Price goes below
                </option>
              </select>
            </div>

          </div>


          <button
            type="submit"
            disabled={creating}
            className="mt-5 rounded-xl bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:opacity-50"
          >
            {creating
              ? "Creating..."
              : "Create Alert"}
          </button>

        </form>
      )}


      {/* -------------------------------------
          Loading
      -------------------------------------- */}

      {loading && (
        <div className="mt-6 rounded-2xl bg-slate-900/50 p-8 text-center text-slate-400">
          Loading price alerts...
        </div>
      )}


      {/* -------------------------------------
          Empty
      -------------------------------------- */}

      {!loading &&
        alerts.length === 0 && (
          <div className="mt-6 flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-slate-900/30 p-10 text-center">

            <Bell className="h-10 w-10 text-slate-600" />

            <h3 className="mt-4 font-semibold">
              No price alerts
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              Create an alert to track your target prices.
            </p>

          </div>
        )}


      {/* -------------------------------------
          Alert List
      -------------------------------------- */}

      {!loading &&
        alerts.length > 0 && (
          <div className="mt-6 space-y-3">

            {alerts.map((alert) => {

              const triggered =
                alert.is_triggered;

              return (
                <div
                  key={alert.id}
                  className={`flex items-center justify-between rounded-2xl border p-4 transition ${
                    triggered
                      ? "border-green-500/20 bg-green-500/5"
                      : "border-white/5 bg-slate-900/50"
                  }`}
                >

                  <div className="flex items-center gap-4">

                    <div
                      className={`rounded-xl p-3 ${
                        triggered
                          ? "bg-green-500/10"
                          : "bg-blue-500/10"
                      }`}
                    >
                      {triggered ? (
                        <BellRing className="h-5 w-5 text-green-400" />
                      ) : (
                        <Bell className="h-5 w-5 text-blue-400" />
                      )}
                    </div>


                    <div>

                      <div className="flex items-center gap-3">

                        <h3 className="font-semibold">
                          {alert.stock_symbol}
                        </h3>

                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                            triggered
                              ? "bg-green-500/10 text-green-400"
                              : "bg-blue-500/10 text-blue-400"
                          }`}
                        >
                          {triggered
                            ? "Triggered"
                            : "Active"}
                        </span>

                      </div>

                      <p className="mt-1 text-sm text-slate-400">

                        {alert.condition ===
                        "above"
                          ? "Price goes above"
                          : "Price goes below"}

                        {" "}

                        <span className="font-medium text-slate-200">
                          Ã¢â€šÂ¹
                          {alert.target_price.toLocaleString(
                            "en-IN",
                            {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            }
                          )}
                        </span>

                      </p>

                    </div>

                  </div>


                  {/* Delete */}

                  <button
                    onClick={() =>
                      deleteAlert(
                        alert.id
                      )
                    }
                    title="Delete alert"
                    className="rounded-xl p-3 text-slate-500 transition hover:bg-red-500/10 hover:text-red-400"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>

                </div>
              );
            })}

          </div>
        )}


      {/* -------------------------------------
          Footer
      -------------------------------------- */}

      {alerts.length > 0 && (
        <div className="mt-5 flex items-center justify-between text-xs text-slate-500">

          <span>
            {alerts.length} alert
            {alerts.length !== 1
              ? "s"
              : ""}{" "}
            configured
          </span>

          <button
            onClick={checkAlerts}
            disabled={checking}
            className="text-blue-400 transition hover:text-blue-300 disabled:opacity-50"
          >
            {checking
              ? "Checking..."
              : "Check live prices"}
          </button>

        </div>
      )}

    </div>
  );
}
