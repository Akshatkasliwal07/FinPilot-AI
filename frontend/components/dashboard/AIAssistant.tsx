"use client";

import {
  useCallback,
  useState,
} from "react";

import {
  BrainCircuit,
  BarChart3,
  Send,
  Newspaper,
  TrendingUp,
  Activity,
} from "lucide-react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

interface TechnicalAnalysis {
  latest_close: number | null;

  sma_20: number | null;
  sma_50: number | null;

  rsi_14: number | null;
  rsi_signal: string;

  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;

  macd_direction: string;
  macd_histogram_direction: string;

  volatility_20d: number | null;

  latest_volume: number | null;
  volume_average_20d: number | null;
  volume_ratio: number | null;
  volume_signal: string;

  trend: string;

  support: number | null;
  resistance: number | null;

  price_vs_sma20_percent: number | null;
  price_vs_sma50_percent: number | null;

  ema_20?: number | null;
}

interface AIAnalysis {
  recommendation: string;
  confidence: number;
  reason: string;
}

interface NewsArticle {
  title: string;
  source?: string;
  published_at?: string;
  url?: string;
  sentiment?: string;
}

interface NewsResponse {
  symbol: string;
  overall_sentiment: string;
  confidence: number;
  articles: NewsArticle[];
}

interface LiveStock {
  symbol: string;
  price: string;
  open: string;
  high: string;
  low: string;
  volume: string;
  previousClose: string;
  change: string;
  changePercent: string;
  dataSource?: string;
}

export default function AIAssistant() {
  const [symbol, setSymbol] =
    useState("");

  const [stock, setStock] =
    useState<LiveStock | null>(null);

  const [technicalAnalysis, setTechnicalAnalysis] =
    useState<TechnicalAnalysis | null>(null);

  const [aiAnalysis, setAiAnalysis] =
    useState<AIAnalysis | null>(null);

  const [news, setNews] =
    useState<NewsArticle[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  /*
   * ---------------------------------------------------------
   * SAFE JSON
   * ---------------------------------------------------------
   */

  const readJson = async (
    response: Response
  ) => {
    try {
      return await response.json();
    } catch {
      return null;
    }
  };

  /*
   * ---------------------------------------------------------
   * FETCH LIVE STOCK
   * ---------------------------------------------------------
   */

  const fetchLiveStock = useCallback(
    async (stockSymbol: string) => {
      const response = await fetch(
        `${API_BASE_URL}/stocks/live/${encodeURIComponent(
          stockSymbol
        )}`,
        {
          cache: "no-store",
        }
      );

      const result =
        await readJson(response);

      if (!response.ok) {
        throw new Error(
          result?.error ||
            result?.detail ||
            result?.message ||
            `Unable to load ${stockSymbol}.`
        );
      }

      const data = result?.data;

      if (!data) {
        throw new Error(
          "Live stock data was not returned."
        );
      }

      return {
        symbol:
          data["01. symbol"] ??
          stockSymbol,

        open:
          data["02. open"] ?? "—",

        high:
          data["03. high"] ?? "—",

        low:
          data["04. low"] ?? "—",

        price:
          data["05. price"] ?? "—",

        volume:
          data["06. volume"] ?? "0",

        previousClose:
          data["08. previous close"] ?? "—",

        change:
          data["09. change"] ?? "0",

        changePercent:
          data["10. change percent"] ?? "0%",

        dataSource:
          data["data_source"] ??
          "Market Data",
      } as LiveStock;
    },
    []
  );

  /*
   * ---------------------------------------------------------
   * FETCH TECHNICAL ANALYSIS
   * ---------------------------------------------------------
   */

  const fetchTechnicalAnalysis =
    useCallback(
      async (stockSymbol: string) => {
        const response = await fetch(
          `${API_BASE_URL}/stocks/analysis/${encodeURIComponent(
            stockSymbol
          )}?period=3mo`,
          {
            cache: "no-store",
          }
        );

        const result =
          await readJson(response);

        if (!response.ok) {
          throw new Error(
            result?.error ||
              result?.detail ||
              result?.message ||
              "Technical analysis unavailable."
          );
        }

        if (
          result?.success !== true ||
          !result?.data
        ) {
          throw new Error(
            result?.message ||
              "Technical analysis data unavailable."
          );
        }

        return result.data as TechnicalAnalysis;
      },
      []
    );

  /*
   * ---------------------------------------------------------
   * FETCH STOCK NEWS
   * ---------------------------------------------------------
   */

  const fetchStockNews =
    useCallback(
      async (stockSymbol: string) => {
        try {
          const response =
            await fetch(
              `${API_BASE_URL}/news/stock/${encodeURIComponent(
                stockSymbol
              )}?limit=10`,
              {
                cache: "no-store",
              }
            );

          const result =
            await readJson(response);

          if (!response.ok) {
            return [];
          }

          return (
            result?.data?.articles ??
            result?.articles ??
            []
          ) as NewsArticle[];
        } catch (err) {
          console.warn(
            "News unavailable:",
            err
          );

          return [];
        }
      },
      []
    );

  /*
   * ---------------------------------------------------------
   * AI ANALYSIS
   * ---------------------------------------------------------
   */

  const fetchAIAnalysis = useCallback(
    async (
      stockData: LiveStock,
      technical: TechnicalAnalysis,
      latestNews: NewsArticle[]
    ) => {
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
          "Please login before using FinPilot AI."
        );
      }

      const response =
        await fetch(
          `${API_BASE_URL}/ai/analyze`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              Authorization:
                `${tokenType} ${token}`,
            },

            body: JSON.stringify({
              symbol:
                stockData.symbol,

              current_price:
                Number(
                  stockData.price
                ),

              technical_indicators: {
                open:
                  Number(
                    stockData.open
                  ),

                high:
                  Number(
                    stockData.high
                  ),

                low:
                  Number(
                    stockData.low
                  ),

                previous_close:
                  Number(
                    stockData.previousClose
                  ),

                change:
                  Number(
                    stockData.change
                  ),

                change_percent:
                  Number(
                    String(
                      stockData.changePercent
                    ).replace("%", "")
                  ),

                volume:
                  Number(
                    stockData.volume
                  ),

                /*
                 * IMPORTANT:
                 * Send already calculated
                 * technical indicators.
                 */

                rsi:
                  technical.rsi_14,

                sma20:
                  technical.sma_20,

                sma50:
                  technical.sma_50,

                ema20:
                  technical.ema_20 ??
                  null,

                macd:
                  technical.macd,

                macd_signal:
                  technical.macd_signal,

                macd_histogram:
                  technical.macd_histogram,

                trend:
                  technical.trend,

                volatility_20d:
                  technical.volatility_20d,

                volume_ratio:
                  technical.volume_ratio,

                support:
                  technical.support,

                resistance:
                  technical.resistance,

                price_vs_sma20_percent:
                  technical.price_vs_sma20_percent,

                price_vs_sma50_percent:
                  technical.price_vs_sma50_percent,
              },

              latest_news:
                latestNews,
            }),
          }
        );

      const result =
        await readJson(response);

      if (!response.ok) {
        throw new Error(
          result?.error ||
            result?.detail ||
            result?.message ||
            "AI analysis failed."
        );
      }

      if (!result?.data) {
        throw new Error(
          "AI analysis returned no data."
        );
      }

      return result.data as AIAnalysis;
    },
    []
  );

  /*
   * ---------------------------------------------------------
   * MAIN ANALYZE FUNCTION
   * ---------------------------------------------------------
   */

  async function handleAnalyze() {
    const cleanSymbol =
      symbol
        .trim()
        .toUpperCase();

    if (!cleanSymbol) {
      setError(
        "Enter a stock symbol first."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");

      setStock(null);
      setTechnicalAnalysis(null);
      setAiAnalysis(null);
      setNews([]);

      /*
       * Load everything for the same stock.
       */

      const stockData =
        await fetchLiveStock(
          cleanSymbol
        );

      setStock(stockData);

      const technical =
        await fetchTechnicalAnalysis(
          cleanSymbol
        );

      setTechnicalAnalysis(
        technical
      );

      const latestNews =
        await fetchStockNews(
          cleanSymbol
        );

      setNews(
        latestNews
      );

      /*
       * Generate AI report using
       * the same technical data.
       */

      const ai =
        await fetchAIAnalysis(
          stockData,
          technical,
          latestNews
        );

      setAiAnalysis(ai);

    } catch (err) {
      console.error(
        "FinPilot AI error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to analyze stock."
      );
    } finally {
      setLoading(false);
    }
  }

  /*
   * ---------------------------------------------------------
   * ENTER KEY
   * ---------------------------------------------------------
   */

  function handleKeyDown(
    e: React.KeyboardEvent<HTMLInputElement>
  ) {
    if (e.key === "Enter") {
      handleAnalyze();
    }
  }

  /*
   * ---------------------------------------------------------
   * FORMAT HELPERS
   * ---------------------------------------------------------
   */

  function formatValue(
    value: number | null | undefined,
    prefix = ""
  ) {
    if (
      value === null ||
      value === undefined ||
      !Number.isFinite(value)
    ) {
      return "—";
    }

    return `${prefix}${value.toFixed(2)}`;
  }

  function formatVolume(
    value:
      | number
      | null
      | undefined
  ) {
    if (
      value === null ||
      value === undefined ||
      !Number.isFinite(value)
    ) {
      return "—";
    }

    return value.toLocaleString(
      "en-IN"
    );
  }

  function recommendationClass() {
    if (
      aiAnalysis?.recommendation ===
      "BUY"
    ) {
      return "text-emerald-400";
    }

    if (
      aiAnalysis?.recommendation ===
      "SELL"
    ) {
      return "text-red-400";
    }

    return "text-yellow-400";
  }

  /*
   * ---------------------------------------------------------
   * UI
   * ---------------------------------------------------------
   */

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">

      {/* HEADER */}

      <div className="flex items-start gap-4">

        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blue-500/10">
          <BrainCircuit className="h-6 w-6 text-cyan-400" />
        </div>

        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan-400">
            FinPilot Intelligence
          </p>

          <h2 className="mt-1 text-2xl font-bold text-white">
            AI Stock Analysis
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            Analyze live market data, technical
            indicators and recent stock news.
          </p>
        </div>

      </div>

      {/* SEARCH */}

      <div className="mt-8 flex gap-3">

        <input
          type="text"
          value={symbol}
          onChange={(e) =>
            setSymbol(
              e.target.value.toUpperCase()
            )
          }
          onKeyDown={handleKeyDown}
          placeholder="Enter symbol, e.g. TCS"
          className="flex-1 rounded-2xl border border-white/10 bg-slate-900/60 px-5 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500/50"
        />

        <button
          type="button"
          onClick={handleAnalyze}
          disabled={loading}
          className="rounded-2xl bg-blue-600 p-3 text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Analyze stock"
        >
          <Send className="h-5 w-5" />
        </button>

      </div>

      {/* ERROR */}

      {error && (
        <div className="mt-5 rounded-2xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* LOADING */}

      {loading && (
        <div className="mt-6 animate-pulse rounded-3xl border border-white/5 bg-slate-900/50 p-6">

          <div className="h-5 w-40 rounded bg-slate-800" />

          <div className="mt-5 h-12 w-52 rounded bg-slate-800" />

          <div className="mt-5 grid gap-4 sm:grid-cols-2">

            <div className="h-24 rounded-2xl bg-slate-800" />

            <div className="h-24 rounded-2xl bg-slate-800" />

            <div className="h-24 rounded-2xl bg-slate-800" />

            <div className="h-24 rounded-2xl bg-slate-800" />

          </div>

        </div>
      )}

      {/* RESULT */}

      {aiAnalysis &&
        technicalAnalysis &&
        stock &&
        !loading && (

        <div className="mt-6 rounded-3xl border border-blue-500/30 bg-gradient-to-br from-blue-950/60 to-slate-900/80 p-6">

          {/* TITLE */}

          <div className="flex items-center gap-3">

            <Activity className="h-6 w-6 text-cyan-400" />

            <h3 className="text-lg font-semibold text-cyan-300">
              AI Stock Analysis
            </h3>

          </div>

          {/* PRICE + RECOMMENDATION */}

          <div className="mt-6 grid gap-4 md:grid-cols-2">

            <div className="rounded-2xl bg-slate-950/40 p-5">

              <p className="text-xs uppercase tracking-wider text-slate-500">
                Current Price
              </p>

              <p className="mt-3 text-3xl font-extrabold text-white">
                ₹
                {stock.price}
              </p>

              <p
                className={`mt-2 text-sm font-semibold ${
                  Number(
                    stock.change
                  ) >= 0
                    ? "text-emerald-400"
                    : "text-red-400"
                }`}
              >
                {Number(
                  stock.change
                ) >= 0
                  ? "+"
                  : ""}
                {stock.change}{" "}
                (
                {stock.changePercent}
                )
              </p>

            </div>

            <div className="rounded-2xl bg-slate-950/40 p-5">

              <p className="text-xs uppercase tracking-wider text-slate-500">
                AI Recommendation
              </p>

              <p
                className={`mt-3 text-3xl font-extrabold ${recommendationClass()}`}
              >
                {
                  aiAnalysis.recommendation
                }
              </p>

            </div>

          </div>

          {/* CONFIDENCE */}

          <div className="mt-6">

            <div className="flex items-center justify-between">

              <p className="text-sm text-slate-400">
                AI Confidence
              </p>

              <p className="font-bold text-white">
                {
                  aiAnalysis.confidence
                }
                %
              </p>

            </div>

            <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">

              <div
                className="h-full rounded-full bg-blue-500 transition-all duration-700"
                style={{
                  width: `${Math.min(
                    Math.max(
                      aiAnalysis.confidence,
                      0
                    ),
                    100
                  )}%`,
                }}
              />

            </div>

          </div>

          {/* TECHNICAL INDICATORS */}

          <div className="mt-8">

            <div className="flex items-center gap-3">

              <BarChart3 className="h-5 w-5 text-blue-400" />

              <h3 className="font-semibold text-white">
                Technical Indicators
              </h3>

            </div>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">

              <Indicator
                label="RSI (14)"
                value={formatValue(
                  technicalAnalysis.rsi_14
                )}
                sub={
                  technicalAnalysis.rsi_signal
                }
              />

              <Indicator
                label="SMA 20"
                value={formatValue(
                  technicalAnalysis.sma_20,
                  "₹"
                )}
                sub={
                  technicalAnalysis.price_vs_sma20_percent !==
                  null
                    ? `Price vs SMA: ${technicalAnalysis.price_vs_sma20_percent.toFixed(
                        2
                      )}%`
                    : "—"
                }
              />

              <Indicator
                label="SMA 50"
                value={formatValue(
                  technicalAnalysis.sma_50,
                  "₹"
                )}
                sub={
                  technicalAnalysis.price_vs_sma50_percent !==
                  null
                    ? `Price vs SMA: ${technicalAnalysis.price_vs_sma50_percent.toFixed(
                        2
                      )}%`
                    : "—"
                }
              />

              <Indicator
                label="MACD"
                value={formatValue(
                  technicalAnalysis.macd
                )}
                sub={
                  technicalAnalysis.macd_direction
                }
              />

              <Indicator
                label="MACD Signal"
                value={formatValue(
                  technicalAnalysis.macd_signal
                )}
                sub={
                  technicalAnalysis.macd_histogram !==
                  null
                    ? `Histogram: ${technicalAnalysis.macd_histogram.toFixed(
                        2
                      )}`
                    : "—"
                }
              />

              <Indicator
                label="Volatility (20D)"
                value={formatValue(
                  technicalAnalysis.volatility_20d,
                  ""
                )}
                sub="20-day volatility"
              />

              <Indicator
                label="Volume"
                value={formatVolume(
                  technicalAnalysis.latest_volume
                )}
                sub={
                  technicalAnalysis.volume_signal ||
                  "—"
                }
              />

              <Indicator
                label="Trend"
                value={
                  technicalAnalysis.trend ||
                  "NEUTRAL"
                }
                sub="Overall market trend"
              />

              <Indicator
                label="Support"
                value={formatValue(
                  technicalAnalysis.support,
                  "₹"
                )}
                sub="Reference level"
              />

              <Indicator
                label="Resistance"
                value={formatValue(
                  technicalAnalysis.resistance,
                  "₹"
                )}
                sub="Reference level"
              />

            </div>

          </div>

          {/* NEWS */}

          <div className="mt-8 flex items-center gap-3">

            <Newspaper className="h-5 w-5 text-slate-400" />

            <p className="text-sm text-slate-300">
              {news.length} latest news article
              {news.length === 1
                ? ""
                : "s"} analyzed
            </p>

          </div>

          {/* REASONING */}

          <div className="mt-6 rounded-2xl bg-slate-950/40 p-5">

            <div className="flex items-center gap-3">

              <TrendingUp className="h-5 w-5 text-cyan-400" />

              <h3 className="font-semibold text-white">
                AI Reasoning
              </h3>

            </div>

            <p className="mt-4 leading-7 text-slate-300">
              {
                aiAnalysis.reason
              }
            </p>

          </div>

          {/* DISCLAIMER */}

          <p className="mt-5 text-xs leading-5 text-slate-600">
            AI analysis is generated from available
            market data and is intended for research
            and educational purposes only. It is not
            personalized financial advice or a
            guarantee of future returns.
          </p>

        </div>
      )}

    </div>
  );
}

/*
 * ============================================================
 * INDICATOR CARD
 * ============================================================
 */

function Indicator({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub: string;
}) {
  return (
    <div className="rounded-2xl bg-slate-950/40 p-5">

      <p className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold text-white">
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        {sub}
      </p>

    </div>
  );
}