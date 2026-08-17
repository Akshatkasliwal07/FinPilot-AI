"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://finpilot-ai-q4nk.onrender.com";

interface Stock {
  id: number;
  symbol: string;
  company_name?: string;
  name?: string;
  exchange?: string;
  sector?: string;
}

interface LiveStock {
  symbol: string;
  open: string;
  high: string;
  low: string;
  price: string;
  volume: string;
  previousClose: string;
  change: string;
  changePercent: string;
  dataSource?: string;
}

export default function StocksPage() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [liveData, setLiveData] = useState<
    Record<string, LiveStock>
  >({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function fetchStocks() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_BASE_URL}/stocks`,
        {
          cache: "no-store",
        }
      );

      const result = await response.json();

      console.log("Stocks API response:", result);

      if (!response.ok) {
        throw new Error(
          result?.error ||
            result?.message ||
            "Failed to fetch stocks"
        );
      }

      let stockList: Stock[] = [];

      if (Array.isArray(result)) {
        stockList = result;
      } else if (Array.isArray(result?.data)) {
        stockList = result.data;
      } else if (Array.isArray(result?.data?.items)) {
        stockList = result.data.items;
      } else if (Array.isArray(result?.items)) {
        stockList = result.items;
      } else if (Array.isArray(result?.stocks)) {
        stockList = result.stocks;
      }

      setStocks(stockList);

      await fetchLivePrices(stockList);
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Failed to fetch stocks"
      );
    } finally {
      setLoading(false);
    }
  }

  async function fetchLivePrices(
    stockList: Stock[]
  ) {
    const prices: Record<string, LiveStock> = {};

    await Promise.all(
      stockList.map(async (stock) => {
        try {
          console.log(
            `Fetching live data for ${stock.symbol}`
          );

          const response = await fetch(
            `${API_BASE_URL}/stocks/live/${stock.symbol}`,
            {
              cache: "no-store",
            }
          );

          const result = await response.json();

          console.log(
            `Live response for ${stock.symbol}:`,
            result
          );

          if (!response.ok || !result?.data) {
            return;
          }

          const data = result.data;

          prices[stock.symbol] = {
            symbol: data["01. symbol"],
            open: data["02. open"],
            high: data["03. high"],
            low: data["04. low"],
            price: data["05. price"],
            volume: data["06. volume"],
            previousClose: data["08. previous close"],
            change: data["09. change"],
            changePercent: data["10. change percent"],
            dataSource:
              data["data_source"] ||
              "Yahoo Finance",
          };
        } catch (err) {
          console.error(
            `Failed to fetch ${stock.symbol}:`,
            err
          );
        }
      })
    );

    setLiveData(prices);
  }

  async function refreshPrices() {
    setRefreshing(true);

    await fetchLivePrices(stocks);

    setRefreshing(false);
  }

  useEffect(() => {
    fetchStocks();
  }, []);

  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg, #030712 0%, #071226 50%, #050b1c 100%)",
        color: "#ffffff",
        padding: "40px",
      }}
    >
      <div
        style={{
          maxWidth: "1400px",
          margin: "0 auto",
        }}
      >
        {/* HEADER */}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "20px",
            marginBottom: "40px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                color: "#60a5fa",
                fontSize: "13px",
                fontWeight: 700,
                letterSpacing: "2px",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}
            >
              Market
            </div>

            <h1
              style={{
                margin: 0,
                fontSize: "46px",
                fontWeight: 800,
                letterSpacing: "-1.5px",
              }}
            >
              Stocks
            </h1>

            <p
              style={{
                color: "#94a3b8",
                marginTop: "10px",
                fontSize: "16px",
              }}
            >
              Explore and track live stock prices
              available in FinPilot AI.
            </p>
          </div>

          <button
            onClick={refreshPrices}
            disabled={refreshing || loading}
            style={{
              background: "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: "12px",
              padding: "14px 24px",
              fontWeight: 700,
              fontSize: "14px",
              cursor:
                refreshing || loading
                  ? "not-allowed"
                  : "pointer",
              opacity:
                refreshing || loading ? 0.7 : 1,
              boxShadow:
                "0 10px 30px rgba(37,99,235,0.25)",
            }}
          >
            {refreshing
              ? "Refreshing..."
              : "Refresh Prices"}
          </button>
        </div>

        {/* ERROR */}

        {error && (
          <div
            style={{
              background: "#1f1115",
              border: "1px solid #7f1d1d",
              borderRadius: "16px",
              padding: "20px",
              marginBottom: "25px",
              color: "#fca5a5",
            }}
          >
            {error}
          </div>
        )}

        {/* LOADING */}

        {loading && (
          <div
            style={{
              background: "#111827",
              border: "1px solid #263244",
              borderRadius: "20px",
              padding: "30px",
              color: "#94a3b8",
            }}
          >
            Loading stocks...
          </div>
        )}

        {/* EMPTY */}

        {!loading && stocks.length === 0 && (
          <div
            style={{
              background: "#111827",
              border: "1px solid #263244",
              borderRadius: "20px",
              padding: "30px",
              color: "#94a3b8",
            }}
          >
            No stocks found.
          </div>
        )}

        {/* STOCK GRID */}

        {!loading && stocks.length > 0 && (
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(380px, 1fr))",
              gap: "22px",
            }}
          >
            {stocks.map((stock) => {
              const live = liveData[stock.symbol];

              const change = live
                ? Number(live.change)
                : 0;

              const positive = change >= 0;

              return (
                <div
                  key={stock.id}
                  style={{
                    background:
                      "linear-gradient(145deg, #111827, #0f172a)",
                    border: "1px solid #263244",
                    borderRadius: "22px",
                    padding: "26px",
                    boxShadow:
                      "0 15px 40px rgba(0,0,0,0.2)",
                  }}
                >
                  {/* CARD HEADER */}

                  <div
                    style={{
                      display: "flex",
                      justifyContent:
                        "space-between",
                      alignItems: "flex-start",
                      gap: "15px",
                    }}
                  >
                    <div>
                      <h2
                        style={{
                          margin: 0,
                          fontSize: "28px",
                          fontWeight: 800,
                        }}
                      >
                        {stock.symbol}
                      </h2>

                      <p
                        style={{
                          color: "#94a3b8",
                          marginTop: "7px",
                          marginBottom: 0,
                        }}
                      >
                        {stock.company_name ||
                          stock.name ||
                          stock.symbol}
                      </p>
                    </div>

                    <span
                      style={{
                        background: "#1e293b",
                        color: "#93c5fd",
                        padding: "7px 11px",
                        borderRadius: "999px",
                        fontSize: "12px",
                        fontWeight: 700,
                      }}
                    >
                      {stock.exchange || "NSE"}
                    </span>
                  </div>

                  {/* PRICE */}

                  {live ? (
                    <>
                      <div
                        style={{
                          marginTop: "25px",
                          padding: "20px",
                          borderRadius: "16px",
                          background: "#0b1220",
                          border:
                            "1px solid #1e293b",
                        }}
                      >
                        <div
                          style={{
                            color: "#64748b",
                            fontSize: "13px",
                          }}
                        >
                          Current Price
                        </div>

                        <div
                          style={{
                            fontSize: "34px",
                            fontWeight: 800,
                            marginTop: "6px",
                          }}
                        >
                          â‚¹{live.price}
                        </div>

                        <div
                          style={{
                            color: positive
                              ? "#22c55e"
                              : "#ef4444",
                            fontWeight: 700,
                            marginTop: "7px",
                          }}
                        >
                          {positive ? "+" : ""}
                          {live.change}{" "}
                          ({positive ? "+" : ""}
                          {live.changePercent})
                        </div>
                      </div>

                      {/* MINI STATS */}

                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns:
                            "1fr 1fr",
                          gap: "12px",
                          marginTop: "15px",
                        }}
                      >
                        {[
                          ["Open", live.open],
                          ["High", live.high],
                          ["Low", live.low],
                          [
                            "Prev. Close",
                            live.previousClose,
                          ],
                        ].map(([label, value]) => (
                          <div
                            key={label}
                            style={{
                              background:
                                "#172033",
                              borderRadius: "12px",
                              padding: "13px",
                            }}
                          >
                            <div
                              style={{
                                color: "#64748b",
                                fontSize: "12px",
                              }}
                            >
                              {label}
                            </div>

                            <div
                              style={{
                                color: "#e2e8f0",
                                fontWeight: 600,
                                marginTop: "4px",
                              }}
                            >
                              â‚¹{value}
                            </div>
                          </div>
                        ))}
                      </div>

                      <div
                        style={{
                          display: "flex",
                          justifyContent:
                            "space-between",
                          alignItems: "center",
                          marginTop: "18px",
                          color: "#64748b",
                          fontSize: "12px",
                        }}
                      >
                        <span>
                          Volume:{" "}
                          {Number(
                            live.volume
                          ).toLocaleString(
                            "en-IN"
                          )}
                        </span>

                        <span
                          style={{
                            background:
                              "#172554",
                            color: "#60a5fa",
                            padding:
                              "6px 10px",
                            borderRadius:
                              "999px",
                          }}
                        >
                          {live.dataSource ||
                            "Yahoo Finance"}
                        </span>
                      </div>
                    </>
                  ) : (
                    <div
                      style={{
                        marginTop: "25px",
                        padding: "25px",
                        borderRadius: "16px",
                        background: "#172033",
                        color: "#64748b",
                      }}
                    >
                      Live data unavailable
                    </div>
                  )}

                  {/* FOOTER */}

                  <div
                    style={{
                      display: "flex",
                      justifyContent:
                        "space-between",
                      alignItems: "center",
                      marginTop: "22px",
                      paddingTop: "18px",
                      borderTop:
                        "1px solid #1e293b",
                    }}
                  >
                    <div
                      style={{
                        color: "#64748b",
                        fontSize: "12px",
                      }}
                    >
                      {stock.sector ||
                        "Market"}{" "}
                      â€¢ {stock.exchange || "NSE"}
                    </div>

                    <Link
                      href={`/stocks/${stock.symbol}`}
                      style={{
                        color: "#60a5fa",
                        textDecoration:
                          "none",
                        fontWeight: 700,
                        fontSize: "13px",
                      }}
                    >
                      View Details â†’
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}