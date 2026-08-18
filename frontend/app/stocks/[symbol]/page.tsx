"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type Interval =
  | "1m"
  | "2m"
  | "5m"
  | "15m"
  | "30m"
  | "60m"
  | "1d";

type Period = "1d" | "5d" | "1mo" | "3mo" | "6mo" | "1y";

interface LiveStock {
  symbol: string;
  code?: string;
  open: string;
  high: string;
  low: string;
  price: string;
  volume: string;
  previousClose: string;
  change: string;
  changePercent: string;
  timestamp?: string;
  marketStatus?: string;
  dataSource?: string;
}

interface Candle {
  time: string;
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

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
}

interface AIAnalysis {
  recommendation: string;
  confidence: number;
  reason: string;
}

const INTERVALS: { value: Interval; label: string }[] = [
  { value: "1m", label: "1m" },
  { value: "2m", label: "2m" },
  { value: "5m", label: "5m" },
  { value: "15m", label: "15m" },
  { value: "30m", label: "30m" },
  { value: "60m", label: "1H" },
  { value: "1d", label: "1D" },
];

const PERIODS: { value: Period; label: string }[] = [
  { value: "1d", label: "1D" },
  { value: "5d", label: "5D" },
  { value: "1mo", label: "1M" },
  { value: "3mo", label: "3M" },
  { value: "6mo", label: "6M" },
  { value: "1y", label: "1Y" },
];

const DEFAULT_PERIOD_FOR_INTERVAL: Record<Interval, Period> = {
  "1m": "1d",
  "2m": "5d",
  "5m": "5d",
  "15m": "1mo",
  "30m": "1mo",
  "60m": "3mo",
  "1d": "1y",
};

function isIntraday(interval: Interval) {
  return interval !== "1d";
}

function intervalLabel(interval: Interval) {
  return interval === "60m" ? "1 hour" : interval;
}

function safeNumber(value: unknown): number | null {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function parseTimestamp(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value < 10_000_000_000 ? value * 1000 : value;
  }

  if (typeof value !== "string" || !value.trim()) return null;

  const numeric = Number(value);
  if (Number.isFinite(numeric)) {
    return numeric < 10_000_000_000 ? numeric * 1000 : numeric;
  }

  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatDateTime(timestamp: number) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "--";

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function formatAxisTime(timestamp: number, interval: Interval) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "";

  if (interval === "1d") {
    return date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
    });
  }

  return date.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function formatCandleDate(timestamp: number, interval: Interval) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "--";

  if (interval === "1d") {
    return date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function formatPrice(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return "Gé¦--";

  return `Gé¦${value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function formatVolume(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return "--";
  return value.toLocaleString("en-IN");
}

function readJson(response: Response) {
  return response
    .json()
    .catch(() => null);
}

function extractArray(raw: any): any[] {
  if (Array.isArray(raw)) return raw;
  if (Array.isArray(raw?.items)) return raw.items;
  if (Array.isArray(raw?.history)) return raw.history;
  if (Array.isArray(raw?.candles)) return raw.candles;
  if (Array.isArray(raw?.data)) return raw.data;
  return [];
}

function normalizeCandle(item: any): Candle | null {
  if (Array.isArray(item)) {
    const timestamp = parseTimestamp(item[0]);
    const open = safeNumber(item[1]);
    const high = safeNumber(item[2]);
    const low = safeNumber(item[3]);
    const close = safeNumber(item[4]);
    const volume = safeNumber(item[5]) ?? 0;

    if (
      timestamp === null ||
      open === null ||
      high === null ||
      low === null ||
      close === null
    ) {
      return null;
    }

    return {
      time: new Date(timestamp).toISOString(),
      timestamp,
      open,
      high,
      low,
      close,
      volume,
    };
  }

  const timestamp = parseTimestamp(
    item?.timestamp ??
      item?.datetime ??
      item?.date ??
      item?.time ??
      item?.Date
  );

  const open = safeNumber(item?.open ?? item?.Open);
  const high = safeNumber(item?.high ?? item?.High);
  const low = safeNumber(item?.low ?? item?.Low);
  const close = safeNumber(item?.close ?? item?.Close);
  const volume = safeNumber(item?.volume ?? item?.Volume) ?? 0;

  if (
    timestamp === null ||
    open === null ||
    high === null ||
    low === null ||
    close === null
  ) {
    return null;
  }

  return {
    time: new Date(timestamp).toISOString(),
    timestamp,
    open,
    high,
    low,
    close,
    volume,
  };
}

function normalizeCandles(raw: any) {
  const items = extractArray(raw);

  return items
    .map(normalizeCandle)
    .filter((item): item is Candle => item !== null)
    .sort((a, b) => a.timestamp - b.timestamp);
}

function calculateSMA(values: number[], period: number) {
  if (values.length < period) return null;

  const slice = values.slice(-period);
  return slice.reduce((sum, value) => sum + value, 0) / period;
}

function calculateRSI(values: number[], period = 14) {
  if (values.length <= period) return null;

  let gains = 0;
  let losses = 0;

  for (let i = 1; i <= period; i += 1) {
    const change = values[i] - values[i - 1];
    if (change > 0) gains += change;
    else losses += Math.abs(change);
  }

  let averageGain = gains / period;
  let averageLoss = losses / period;

  for (let i = period + 1; i < values.length; i += 1) {
    const change = values[i] - values[i - 1];

    const gain = change > 0 ? change : 0;
    const loss = change < 0 ? Math.abs(change) : 0;

    averageGain =
      (averageGain * (period - 1) + gain) / period;

    averageLoss =
      (averageLoss * (period - 1) + loss) / period;
  }

  if (averageLoss === 0) return 100;

  const rs = averageGain / averageLoss;
  return 100 - 100 / (1 + rs);
}

function calculateEMA(values: number[], period: number) {
  if (values.length < period) return [];

  const multiplier = 2 / (period + 1);

  let ema =
    values.slice(0, period).reduce(
      (sum, value) => sum + value,
      0
    ) / period;

  const result: Array<number | null> = new Array(
    period - 1
  ).fill(null);

  result.push(ema);

  for (let i = period; i < values.length; i += 1) {
    ema = (values[i] - ema) * multiplier + ema;
    result.push(ema);
  }

  return result;
}

function calculateTechnicalAnalysis(
  candles: Candle[]
): TechnicalAnalysis | null {
  const closes = candles.map((item) => item.close);
  const volumes = candles.map((item) => item.volume);

  if (closes.length < 20) return null;

  const latestClose = closes[closes.length - 1];

  const sma20 = calculateSMA(closes, 20);
  const sma50 = calculateSMA(closes, 50);
  const rsi14 = calculateRSI(closes, 14);

  let rsiSignal = "NEUTRAL";
  if (rsi14 !== null) {
    if (rsi14 >= 70) rsiSignal = "OVERBOUGHT";
    else if (rsi14 <= 30) rsiSignal = "OVERSOLD";
    else if (rsi14 >= 50) rsiSignal = "BULLISH";
    else rsiSignal = "BEARISH";
  }

  const ema12 = calculateEMA(closes, 12);
  const ema26 = calculateEMA(closes, 26);

  const macdValues: number[] = [];

  for (let i = 0; i < closes.length; i += 1) {
    if (
      ema12[i] !== null &&
      ema12[i] !== undefined &&
      ema26[i] !== null &&
      ema26[i] !== undefined
    ) {
      macdValues.push(
        (ema12[i] as number) - (ema26[i] as number)
      );
    }
  }

  const macd =
    macdValues.length > 0
      ? macdValues[macdValues.length - 1]
      : null;

  const signalValues = calculateEMA(macdValues, 9);

  const macdSignal =
    signalValues.length > 0
      ? signalValues[signalValues.length - 1]
      : null;

  const macdHistogram =
    macd !== null && macdSignal !== null
      ? macd - macdSignal
      : null;

  const macdDirection =
    macd !== null && macdSignal !== null
      ? macd > macdSignal
        ? "BULLISH"
        : macd < macdSignal
        ? "BEARISH"
        : "NEUTRAL"
      : "NEUTRAL";

  const macdHistogramDirection =
    macdHistogram !== null
      ? macdHistogram > 0
        ? "POSITIVE"
        : macdHistogram < 0
        ? "NEGATIVE"
        : "NEUTRAL"
      : "NEUTRAL";

  const recentCloses = closes.slice(-21);
  const returns: number[] = [];

  for (let i = 1; i < recentCloses.length; i += 1) {
    if (recentCloses[i - 1] !== 0) {
      returns.push(
        ((recentCloses[i] - recentCloses[i - 1]) /
          recentCloses[i - 1]) *
          100
      );
    }
  }

  let volatility20d: number | null = null;

  if (returns.length > 0) {
    const mean =
      returns.reduce((sum, value) => sum + value, 0) /
      returns.length;

    const variance =
      returns.reduce(
        (sum, value) =>
          sum + Math.pow(value - mean, 2),
        0
      ) / returns.length;

    volatility20d = Math.sqrt(variance);
  }

  const latestVolume =
    volumes.length > 0
      ? volumes[volumes.length - 1]
      : null;

  const volume20 =
    volumes.length >= 20
      ? volumes.slice(-20).reduce(
          (sum, value) => sum + value,
          0
        ) / 20
      : null;

  const volumeRatio =
    latestVolume !== null &&
    volume20 !== null &&
    volume20 !== 0
      ? latestVolume / volume20
      : null;

  let volumeSignal = "NORMAL";
  if (volumeRatio !== null) {
    if (volumeRatio >= 1.5) volumeSignal = "HIGH";
    else if (volumeRatio <= 0.7) volumeSignal = "LOW";
  }

  const supportWindow = closes.slice(-20);

  const support =
    supportWindow.length > 0
      ? Math.min(...supportWindow)
      : null;

  const resistance =
    supportWindow.length > 0
      ? Math.max(...supportWindow)
      : null;

  let trend = "NEUTRAL";

  if (sma20 !== null && sma50 !== null) {
    if (
      latestClose > sma20 &&
      sma20 > sma50
    ) {
      trend = "BULLISH";
    } else if (
      latestClose < sma20 &&
      sma20 < sma50
    ) {
      trend = "BEARISH";
    }
  }

  const priceVsSMA20 =
    sma20 !== null && sma20 !== 0
      ? ((latestClose - sma20) / sma20) * 100
      : null;

  const priceVsSMA50 =
    sma50 !== null && sma50 !== 0
      ? ((latestClose - sma50) / sma50) * 100
      : null;

  return {
    latest_close: latestClose,
    sma_20: sma20,
    sma_50: sma50,
    rsi_14: rsi14,
    rsi_signal: rsiSignal,
    macd,
    macd_signal: macdSignal,
    macd_histogram: macdHistogram,
    macd_direction: macdDirection,
    macd_histogram_direction: macdHistogramDirection,
    volatility_20d: volatility20d,
    latest_volume: latestVolume,
    volume_average_20d: volume20,
    volume_ratio: volumeRatio,
    volume_signal: volumeSignal,
    trend,
    support,
    resistance,
    price_vs_sma20_percent: priceVsSMA20,
    price_vs_sma50_percent: priceVsSMA50,
  };
}

export default function StockDetailsPage() {
  const params = useParams();

  const symbol = String(params?.symbol ?? "")
    .trim()
    .toUpperCase();

  const [stock, setStock] =
    useState<LiveStock | null>(null);

  const [candles, setCandles] =
    useState<Candle[]>([]);

  const [interval, setInterval] =
    useState<Interval>("5m");

  const [period, setPeriod] =
    useState<Period>("5d");

  const [loading, setLoading] =
    useState(true);

  const [chartLoading, setChartLoading] =
    useState(false);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState("");

  const [chartError, setChartError] =
    useState("");

  const [technicalAnalysis, setTechnicalAnalysis] =
    useState<TechnicalAnalysis | null>(null);

  const [aiLoading, setAiLoading] =
    useState(false);

  const [aiAnalysis, setAiAnalysis] =
    useState<AIAnalysis | null>(null);

  const [aiError, setAiError] =
    useState("");

  const [watchlistAdded, setWatchlistAdded] =
    useState(false);

  const [watchlistLoading, setWatchlistLoading] =
    useState(false);

  const [watchlistError, setWatchlistError] =
    useState("");

  const [selectedCandle, setSelectedCandle] =
    useState<Candle | null>(null);

  const readJsonSafe = useCallback(
    async (response: Response) => {
      return readJson(response);
    },
    []
  );

  const fetchLiveStock =
    useCallback(async () => {
      if (!symbol) {
        throw new Error("Stock symbol is missing.");
      }

      const response = await fetch(
        `${API_BASE_URL}/api/market/live/quote/${encodeURIComponent(
          symbol
        )}`,
        {
          cache: "no-store",
        }
      );

      const result =
        await readJsonSafe(response);

      if (
        !response.ok ||
        result?.success !== true
      ) {
        throw new Error(
          result?.error ??
            result?.detail ??
            "Unable to load live stock data."
        );
      }

      const data = result?.data;

      if (!data) {
        throw new Error(
          "No live stock data received."
        );
      }

      setStock({
        symbol: data.symbol ?? symbol,
        code: data.code,
        price: String(data.price ?? ""),
        open: String(data.open ?? ""),
        high: String(data.high ?? ""),
        low: String(data.low ?? ""),
        previousClose: String(
          data.previous_close ??
            data.previousClose ??
            ""
        ),
        change: String(data.change ?? ""),
        changePercent: String(
          data.change_percent ??
            data.change_p ??
            ""
        ),
        volume: String(data.volume ?? ""),
        timestamp:
          data.timestamp ??
          undefined,
        marketStatus:
          data.market_status ??
          "latest_available",
        dataSource:
          data.data_source ??
          "Market Data",
      });
    },
    [symbol, readJsonSafe]
  );

  const fetchCandles = useCallback(
    async (
      selectedInterval: Interval,
      selectedPeriod: Period
    ) => {
      if (!symbol) return;

      try {
        setChartLoading(true);
        setChartError("");

        const response = await fetch(
          `${API_BASE_URL}/api/market/live/intraday/${encodeURIComponent(
            symbol
          )}?interval=${encodeURIComponent(
            selectedInterval
          )}&period=${encodeURIComponent(
            selectedPeriod
          )}`,
          {
            cache: "no-store",
          }
        );

        const result =
          await readJsonSafe(response);

        if (
          !response.ok ||
          result?.success !== true
        ) {
          throw new Error(
            result?.error ??
              result?.detail ??
              "Unable to load candle data."
          );
        }

        const normalized =
          normalizeCandles(result?.data);

        if (normalized.length === 0) {
          throw new Error(
            `No ${intervalLabel(
              selectedInterval
            )} OHLC candles were returned for ${symbol}.`
          );
        }

        setCandles(normalized);
        setSelectedCandle(
          normalized[normalized.length - 1]
        );
      } catch (err) {
        console.error(
          "Candle data error:",
          err
        );

        setCandles([]);
        setSelectedCandle(null);
        setChartError(
          err instanceof Error
            ? err.message
            : "Unable to load candle data."
        );
      } finally {
        setChartLoading(false);
      }
    },
    [symbol, readJsonSafe]
  );

  const fetchTechnical = useCallback(
    async () => {
      if (!symbol) return;

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/market/live/history/${encodeURIComponent(
            symbol
          )}?period=1y`,
          {
            cache: "no-store",
          }
        );

        const result =
          await readJsonSafe(response);

        if (
          !response.ok ||
          result?.success !== true
        ) {
          setTechnicalAnalysis(null);
          return;
        }

        const normalized =
          normalizeCandles(result?.data);

        setTechnicalAnalysis(
          calculateTechnicalAnalysis(
            normalized
          )
        );
      } catch (err) {
        console.error(
          "Technical analysis error:",
          err
        );
        setTechnicalAnalysis(null);
      }
    },
    [symbol, readJsonSafe]
  );

  useEffect(() => {
    if (!symbol) return;

    try {
      const saved = localStorage.getItem(
        `finpilot_watchlist_${symbol}`
      );

      setWatchlistAdded(
        saved === "true"
      );
    } catch {
      setWatchlistAdded(false);
    }
  }, [symbol]);

  async function handleAddToWatchlist() {
    if (!symbol || watchlistAdded) return;

    try {
      setWatchlistLoading(true);
      setWatchlistError("");

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
          "Please login before adding stocks to your watchlist."
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
        await readJson(response);

      if (!response.ok) {
        const message = String(
          result?.detail ??
            result?.error ??
            result?.message ??
            ""
        );

        const alreadyExists =
          response.status === 409 ||
          /already|exists|duplicate/i.test(
            message
          );

        if (!alreadyExists) {
          throw new Error(
            message ||
              "Unable to add this stock to your watchlist."
          );
        }
      }

      setWatchlistAdded(true);

      localStorage.setItem(
        `finpilot_watchlist_${symbol}`,
        "true"
      );
    } catch (err) {
      console.error(
        "Watchlist error:",
        err
      );

      setWatchlistError(
        err instanceof Error
          ? err.message
          : "Unable to add stock to watchlist."
      );
    } finally {
      setWatchlistLoading(false);
    }
  }

  useEffect(() => {
    if (!symbol) return;

    let cancelled = false;

    async function loadPage() {
      try {
        setLoading(true);
        setError("");

        await Promise.all([
          fetchLiveStock(),
          fetchCandles(
            interval,
            period
          ),
          fetchTechnical(),
        ]);
      } catch (err) {
        if (cancelled) return;

        console.error(
          "Stock page error:",
          err
        );

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load stock."
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadPage();

    return () => {
      cancelled = true;
    };
  }, [
    symbol,
    fetchLiveStock,
    fetchCandles,
    fetchTechnical,
    interval,
    period,
  ]);

  useEffect(() => {
    if (!symbol) return;

    if (!isIntraday(interval)) return;

    const timer = window.setInterval(
      () => {
        fetchLiveStock();
        fetchCandles(
          interval,
          period
        );
      },
      30000
    );

    return () => {
      window.clearInterval(timer);
    };
  }, [
    symbol,
    interval,
    period,
    fetchLiveStock,
    fetchCandles,
  ]);

  function handleIntervalChange(
    newInterval: Interval
  ) {
    const newPeriod =
      DEFAULT_PERIOD_FOR_INTERVAL[
        newInterval
      ];

    setInterval(newInterval);
    setPeriod(newPeriod);
    setChartError("");
  }

  function handlePeriodChange(
    newPeriod: Period
  ) {
    setPeriod(newPeriod);
    setChartError("");
  }

  async function handleRefresh() {
    try {
      setRefreshing(true);
      setError("");

      await Promise.all([
        fetchLiveStock(),
        fetchCandles(
          interval,
          period
        ),
        fetchTechnical(),
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Refresh failed."
      );
    } finally {
      setRefreshing(false);
    }
  }

  async function handleAIAnalysis() {
    try {
      setAiLoading(true);
      setAiError("");
      setAiAnalysis(null);

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
          "Please login before using FinPilot AI analysis."
        );
      }

      let response = await fetch(
        `${API_BASE_URL}/ai/decision/${encodeURIComponent(
          symbol
        )}`,
        {
          method: "GET",
          cache: "no-store",
          headers: {
            Authorization:
              `${tokenType} ${token}`,
          },
        }
      );

      let result =
        await readJson(response);

      if (response.status === 404) {
        response = await fetch(
          `${API_BASE_URL}/ai/analyze`,
          {
            method: "POST",
            cache: "no-store",
            headers: {
              "Content-Type":
                "application/json",
              Authorization:
                `${tokenType} ${token}`,
            },
            body: JSON.stringify({
              symbol,
              current_price:
                Number(stock?.price),
              technical_indicators: {
                open:
                  Number(stock?.open),
                high:
                  Number(stock?.high),
                low:
                  Number(stock?.low),
                previous_close:
                  Number(
                    stock?.previousClose
                  ),
                change:
                  Number(stock?.change),
                change_percent:
                  Number(
                    String(
                      stock?.changePercent ??
                        ""
                    ).replace(
                      "%",
                      ""
                    )
                  ),
                volume:
                  Number(stock?.volume),
                historical_data:
                  candles.map(
                    (item) => ({
                      date:
                        item.time,
                      open:
                        item.open,
                      high:
                        item.high,
                      low:
                        item.low,
                      close:
                        item.close,
                      volume:
                        item.volume,
                    })
                  ),
                technical_analysis:
                  technicalAnalysis,
              },
              latest_news: [],
            }),
          }
        );

        result =
          await readJson(response);
      }

      if (!response.ok) {
        throw new Error(
          result?.error ??
            result?.detail ??
            result?.message ??
            "Unable to generate FinPilot AI decision."
        );
      }

      if (!result?.data) {
        throw new Error(
          "FinPilot AI returned no decision data."
        );
      }

      const data =
        result.data;

      const recommendation =
        String(
          data.recommendation ??
            data.decision ??
            data.action ??
            "WAIT"
        ).toUpperCase();

      const confidence =
        Number(
          data.confidence ??
            data.confidence_score ??
            0
        );

      const reason =
        String(
          data.reason ??
            data.action_reason ??
            data.explanation ??
            data.message ??
            data.summary ??
            "No additional explanation was returned by FinPilot AI."
        );

      setAiAnalysis({
        recommendation,
        confidence: Math.min(
          Math.max(
            Number.isFinite(
              confidence
            )
              ? confidence
              : 0,
            0
          ),
          100
        ),
        reason,
      });
    } catch (err) {
      console.error(
        "AI decision error:",
        err
      );

      setAiError(
        err instanceof Error
          ? err.message
          : "Unable to generate FinPilot AI decision."
      );
    } finally {
      setAiLoading(false);
    }
  }

  const price =
    Number(stock?.price);

  const change =
    Number(stock?.change);

  const changePercent =
    Number(
      String(
        stock?.changePercent ??
          ""
      ).replace(
        "%",
        ""
      )
    );

  const positive =
    Number.isFinite(change)
      ? change >= 0
      : changePercent >= 0;

  const chartCandles =
    useMemo(() => {
      const maxCandles = 500;

      if (
        candles.length <=
        maxCandles
      ) {
        return candles;
      }

      return candles.slice(
        candles.length -
          maxCandles
      );
    }, [candles]);

  if (loading) {
    return (
      <PageShell>
        <Link
          href="/stocks"
          className="text-sm font-medium text-blue-400 hover:text-blue-300"
        >
          GåÉ Back to Stocks
        </Link>

        <div className="mt-8 rounded-3xl border border-white/10 bg-slate-900/70 p-10">
          <div className="animate-pulse">
            <div className="h-4 w-28 rounded bg-slate-800" />
            <div className="mt-5 h-12 w-48 rounded bg-slate-800" />
            <div className="mt-4 h-5 w-72 rounded bg-slate-800" />
            <div className="mt-8 h-[420px] rounded-2xl bg-slate-950" />
          </div>
        </div>
      </PageShell>
    );
  }

  if (error || !stock) {
    return (
      <PageShell>
        <Link
          href="/stocks"
          className="text-sm font-medium text-blue-400 hover:text-blue-300"
        >
          GåÉ Back to Stocks
        </Link>

        <div className="mt-8 rounded-3xl border border-red-500/20 bg-red-950/20 p-8">
          <h1 className="text-2xl font-bold text-red-400">
            Unable to load stock
          </h1>

          <p className="mt-3 text-red-300">
            {error ||
              "Stock data unavailable."}
          </p>

          <button
            onClick={handleRefresh}
            className="mt-6 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-500"
          >
            Try Again
          </button>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link
          href="/stocks"
          className="text-sm font-medium text-blue-400 hover:text-blue-300"
        >
          GåÉ Back to Stocks
        </Link>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={
              handleAddToWatchlist
            }
            disabled={
              watchlistLoading ||
              watchlistAdded
            }
            className={`rounded-xl px-5 py-2.5 text-sm font-semibold ${
              watchlistAdded
                ? "border border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border border-yellow-500/30 bg-yellow-500/10 text-yellow-300 hover:bg-yellow-500/20"
            }`}
          >
            {watchlistLoading
              ? "Adding..."
              : watchlistAdded
              ? "G£ô In Watchlist"
              : "Gÿå Add to Watchlist"}
          </button>

          <button
            onClick={
              handleRefresh
            }
            disabled={
              refreshing
            }
            className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-60"
          >
            {refreshing
              ? "Refreshing..."
              : "Refresh Data"}
          </button>
        </div>
      </div>

      {watchlistError && (
        <div className="mt-4 rounded-xl border border-red-500/20 bg-red-950/20 px-4 py-3 text-sm text-red-300">
          {watchlistError}
        </div>
      )}

      <section className="mt-8">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">
            Stock Details
          </span>

          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-400">
            NSE / BSE
          </span>

          <span
            className={`rounded-full border px-3 py-1 text-xs font-semibold ${
              stock.marketStatus ===
              "live"
                ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
                : "border-yellow-500/20 bg-yellow-500/10 text-yellow-300"
            }`}
          >
            {stock.marketStatus ??
              "latest_available"}
          </span>
        </div>

        <div className="mt-3 flex flex-wrap items-end gap-4">
          <h1 className="text-5xl font-extrabold tracking-tight text-white">
            {symbol}
          </h1>

          {stock.code && (
            <span className="pb-1 text-sm text-slate-500">
              {stock.code}
            </span>
          )}
        </div>

        <p className="mt-2 text-slate-400">
          Live market information,
          OHLC candlestick charts,
          technical analysis and
          FinPilot AI research.
        </p>
      </section>

      <section className="mt-7 overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900 to-slate-950 shadow-2xl">
        <div className="p-7 md:p-9">
          <div className="flex flex-col justify-between gap-8 md:flex-row md:items-center">
            <div>
              <p className="text-sm text-slate-500">
                Current Market Price
              </p>

              <div className="mt-2 text-5xl font-extrabold tracking-tight text-white">
                {Number.isFinite(
                  price
                )
                  ? formatPrice(
                      price
                    )
                  : "Gé¦--"}
              </div>

              <div
                className={`mt-3 text-lg font-bold ${
                  positive
                    ? "text-emerald-400"
                    : "text-red-400"
                }`}
              >
                {Number.isFinite(
                  change
                )
                  ? `${
                      positive
                        ? "+"
                        : ""
                    }${change.toFixed(
                      2
                    )}`
                  : "--"}

                <span className="ml-2">
                  {Number.isFinite(
                    changePercent
                  )
                    ? `(${
                        positive
                          ? "+"
                          : ""
                      }${changePercent.toFixed(
                        2
                      )}%)`
                    : "(--)"}
                </span>
              </div>
            </div>

            <div className="rounded-2xl border border-blue-500/20 bg-blue-500/10 px-5 py-4">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Data Source
              </p>

              <p className="mt-1 font-semibold text-blue-400">
                GùÅ{" "}
                {stock.dataSource ??
                  "Market Data"}
              </p>

              {stock.timestamp && (
                <p className="mt-1 text-xs text-slate-500">
                  {stock.timestamp}
                </p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Open"
          value={formatPrice(
            Number(stock.open)
          )}
        />

        <StatCard
          label="Day High"
          value={formatPrice(
            Number(stock.high)
          )}
        />

        <StatCard
          label="Day Low"
          value={formatPrice(
            Number(stock.low)
          )}
        />

        <StatCard
          label="Previous Close"
          value={formatPrice(
            Number(
              stock.previousClose
            )
          )}
        />
      </section>

      <section className="mt-6 rounded-3xl border border-white/10 bg-slate-900/70 p-5 shadow-xl md:p-7">
        <div className="flex flex-col justify-between gap-5 xl:flex-row xl:items-end">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-400">
              Market Performance
            </p>

            <h2 className="mt-2 text-2xl font-bold text-white">
              Real OHLC Candlestick Chart
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              {interval === "1d"
                ? "Daily candles"
                : `${intervalLabel(
                    interval
                  )} candles`}{" "}
              GÇó{" "}
              {candles.length} candles
              loaded
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {INTERVALS.map(
              (item) => (
                <button
                  key={
                    item.value
                  }
                  onClick={() =>
                    handleIntervalChange(
                      item.value
                    )
                  }
                  className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
                    interval ===
                    item.value
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-900/30"
                      : "border border-white/10 bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  {item.label}
                </button>
              )
            )}
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {PERIODS.map(
              (item) => (
                <button
                  key={
                    item.value
                  }
                  onClick={() =>
                    handlePeriodChange(
                      item.value
                    )
                  }
                  disabled={
                    interval ===
                      "1m" &&
                    !["1d", "5d"].includes(
                      item.value
                    )
                  }
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${
                    period ===
                    item.value
                      ? "bg-blue-500/20 text-blue-300"
                      : "border border-white/10 bg-white/5 text-slate-500 hover:text-white"
                  } disabled:cursor-not-allowed disabled:opacity-30`}
                >
                  {item.label}
                </button>
              )
            )}
          </div>

          <div className="text-xs text-slate-500">
            Auto-refresh:{" "}
            {isIntraday(interval)
              ? "30 seconds"
              : "manual"}
          </div>
        </div>

        {chartError && (
          <div className="mt-5 rounded-xl border border-red-500/20 bg-red-950/20 p-4 text-sm text-red-300">
            {chartError}
          </div>
        )}

        <div className="mt-6">
          {chartLoading ? (
            <div className="flex h-[560px] items-center justify-center rounded-2xl border border-white/5 bg-slate-950/70">
              <div className="text-center">
                <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
                <p className="mt-4 text-sm text-slate-500">
                  Loading real OHLC candles...
                </p>
              </div>
            </div>
          ) : chartCandles.length ===
            0 ? (
            <div className="flex h-[560px] items-center justify-center rounded-2xl border border-white/5 bg-slate-950/70">
              <div className="text-center">
                <p className="text-slate-400">
                  No candle data available.
                </p>
                <p className="mt-2 text-xs text-slate-600">
                  Check the backend
                  /live/intraday endpoint
                  and provider response.
                </p>
              </div>
            </div>
          ) : (
            <CandlestickChart
              candles={
                chartCandles
              }
              interval={
                interval
              }
              selected={
                selectedCandle
              }
              onSelect={
                setSelectedCandle
              }
            />
          )}
        </div>

        {selectedCandle && (
          <div className="mt-5 grid gap-3 rounded-2xl border border-white/10 bg-black/20 p-4 sm:grid-cols-2 lg:grid-cols-6">
            <MiniValue
              label="Time"
              value={formatCandleDate(
                selectedCandle.timestamp,
                interval
              )}
            />

            <MiniValue
              label="Open"
              value={formatPrice(
                selectedCandle.open
              )}
            />

            <MiniValue
              label="High"
              value={formatPrice(
                selectedCandle.high
              )}
            />

            <MiniValue
              label="Low"
              value={formatPrice(
                selectedCandle.low
              )}
            />

            <MiniValue
              label="Close"
              value={formatPrice(
                selectedCandle.close
              )}
            />

            <MiniValue
              label="Volume"
              value={formatVolume(
                selectedCandle.volume
              )}
            />
          </div>
        )}
      </section>

      <section className="mt-6 rounded-3xl border border-white/10 bg-slate-900/70 p-5 shadow-xl md:p-7">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-400">
            Market Intelligence
          </p>

          <h2 className="mt-2 text-2xl font-bold text-white">
            Technical Analysis
          </h2>
        </div>

        {!technicalAnalysis ? (
          <div className="mt-6 rounded-xl border border-white/5 bg-black/20 p-6 text-center text-sm text-slate-500">
            Technical analysis
            unavailable.
          </div>
        ) : (
          <>
            <div className="mt-6 rounded-2xl border border-white/10 bg-black/20 p-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Overall Trend
              </p>

              <p
                className={`mt-2 text-3xl font-extrabold ${
                  technicalAnalysis.trend ===
                  "BULLISH"
                    ? "text-emerald-400"
                    : technicalAnalysis.trend ===
                      "BEARISH"
                    ? "text-red-400"
                    : "text-yellow-400"
                }`}
              >
                {
                  technicalAnalysis.trend
                }
              </p>
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <TechnicalCard
                label="SMA 20"
                value={
                  technicalAnalysis.sma_20 !==
                  null
                    ? formatPrice(
                        technicalAnalysis.sma_20
                      )
                    : "N/A"
                }
                sub={
                  technicalAnalysis.price_vs_sma20_percent !==
                  null
                    ? `Price vs SMA: ${technicalAnalysis.price_vs_sma20_percent.toFixed(
                        2
                      )}%`
                    : "N/A"
                }
              />

              <TechnicalCard
                label="SMA 50"
                value={
                  technicalAnalysis.sma_50 !==
                  null
                    ? formatPrice(
                        technicalAnalysis.sma_50
                      )
                    : "N/A"
                }
                sub={
                  technicalAnalysis.price_vs_sma50_percent !==
                  null
                    ? `Price vs SMA: ${technicalAnalysis.price_vs_sma50_percent.toFixed(
                        2
                      )}%`
                    : "N/A"
                }
              />

              <TechnicalCard
                label="RSI 14"
                value={
                  technicalAnalysis.rsi_14 !==
                  null
                    ? technicalAnalysis.rsi_14.toFixed(
                        2
                      )
                    : "N/A"
                }
                sub={
                  technicalAnalysis.rsi_signal
                }
                positive={
                  technicalAnalysis.rsi_signal ===
                  "BULLISH"
                }
                negative={
                  technicalAnalysis.rsi_signal ===
                  "BEARISH"
                }
              />

              <TechnicalCard
                label="MACD"
                value={
                  technicalAnalysis.macd !==
                  null
                    ? technicalAnalysis.macd.toFixed(
                        2
                      )
                    : "N/A"
                }
                sub={
                  technicalAnalysis.macd_direction
                }
                positive={
                  technicalAnalysis.macd_direction ===
                  "BULLISH"
                }
                negative={
                  technicalAnalysis.macd_direction ===
                  "BEARISH"
                }
              />

              <TechnicalCard
                label="MACD Signal"
                value={
                  technicalAnalysis.macd_signal !==
                  null
                    ? technicalAnalysis.macd_signal.toFixed(
                        2
                      )
                    : "N/A"
                }
                sub={
                  technicalAnalysis.macd_histogram !==
                  null
                    ? `Histogram: ${technicalAnalysis.macd_histogram.toFixed(
                        2
                      )}`
                    : "N/A"
                }
              />

              <TechnicalCard
                label="Volatility 20D"
                value={
                  technicalAnalysis.volatility_20d !==
                  null
                    ? `${technicalAnalysis.volatility_20d.toFixed(
                        2
                      )}%`
                    : "N/A"
                }
              />

              <TechnicalCard
                label="Volume"
                value={
                  technicalAnalysis.latest_volume !==
                  null
                    ? formatVolume(
                        technicalAnalysis.latest_volume
                      )
                    : "N/A"
                }
                sub={
                  technicalAnalysis.volume_ratio !==
                  null
                    ? `Ratio: ${technicalAnalysis.volume_ratio.toFixed(
                        2
                      )}`
                    : "N/A"
                }
              />

              <TechnicalCard
                label="Support"
                value={
                  technicalAnalysis.support !==
                  null
                    ? formatPrice(
                        technicalAnalysis.support
                      )
                    : "N/A"
                }
              />

              <TechnicalCard
                label="Resistance"
                value={
                  technicalAnalysis.resistance !==
                  null
                    ? formatPrice(
                        technicalAnalysis.resistance
                      )
                    : "N/A"
                }
              />
            </div>
          </>
        )}
      </section>

      <section className="mt-6 rounded-3xl border border-white/10 bg-slate-900/70 p-5 shadow-xl md:p-7">
        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-xl">
                =ƒñû
              </div>

              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-400">
                  FinPilot Intelligence
                </p>

                <h2 className="mt-1 text-2xl font-bold text-white">
                  AI Research &
                  Recommendation
                </h2>
              </div>
            </div>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
              Get a direct AI-powered
              market decision using the
              latest available stock data,
              technical indicators and
              market signals.
            </p>
          </div>

          <button
            onClick={
              handleAIAnalysis
            }
            disabled={aiLoading}
            className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-500 disabled:opacity-60"
          >
            {aiLoading
              ? "Analyzing..."
              : "Ask FinPilot AI"}
          </button>
        </div>

        {aiError && (
          <div className="mt-5 rounded-xl border border-red-500/20 bg-red-950/20 p-4 text-sm text-red-300">
            {aiError}
          </div>
        )}

        {aiLoading && (
          <div className="mt-6 rounded-2xl border border-white/5 bg-black/20 p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-5 w-32 rounded bg-slate-800" />
              <div className="h-10 w-48 rounded bg-slate-800" />
              <div className="h-4 w-full rounded bg-slate-800" />
              <div className="h-4 w-5/6 rounded bg-slate-800" />
            </div>
          </div>
        )}

        {aiAnalysis &&
          !aiLoading && (
            <div className="mt-6 rounded-2xl border border-white/10 bg-black/20 p-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Recommendation
                  </p>

                  <p
                    className={`mt-2 text-4xl font-extrabold ${
                      aiAnalysis.recommendation ===
                      "BUY"
                        ? "text-emerald-400"
                        : aiAnalysis.recommendation ===
                          "SELL"
                        ? "text-red-400"
                        : "text-yellow-400"
                    }`}
                  >
                    {
                      aiAnalysis.recommendation
                    }
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/5 px-5 py-4">
                  <p className="text-xs text-slate-500">
                    AI Confidence
                  </p>

                  <div className="mt-3 h-2 w-32 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-blue-500"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            Number(
                              aiAnalysis.confidence
                            ) || 0,
                            0
                          ),
                          100
                        )}%`,
                      }}
                    />
                  </div>

                  <p className="mt-2 text-xs text-slate-400">
                    {
                      aiAnalysis.confidence
                    }
                    %
                  </p>
                </div>
              </div>

              <div className="mt-6 border-t border-white/5 pt-5">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  AI Reasoning
                </p>

                <p className="mt-3 leading-7 text-slate-300">
                  {
                    aiAnalysis.reason
                  }
                </p>
              </div>

              <div className="mt-5 rounded-xl border border-yellow-500/10 bg-yellow-500/5 p-4 text-xs leading-5 text-yellow-300/80">
                GÜá AI analysis is generated
                from supplied market data
                and is intended for research
                and educational purposes only.
                It is not personalized financial
                advice.
              </div>
            </div>
          )}
      </section>

      <section className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Trading Volume
          </p>

          <p className="mt-2 text-3xl font-bold text-white">
            {formatVolume(
              Number(stock.volume)
            )}
          </p>

          <p className="mt-1 text-sm text-slate-500">
            Latest reported session
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Market Data
          </p>

          <div className="mt-3 flex items-center gap-3">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                stock.marketStatus ===
                "live"
                  ? "bg-emerald-400"
                  : "bg-yellow-400"
              }`}
            />

            <span className="font-semibold text-slate-200">
              {stock.marketStatus ===
              "live"
                ? "Live Data"
                : "Latest Available Data"}
            </span>
          </div>

          <p className="mt-2 text-sm text-slate-500">
            Powered by{" "}
            {stock.dataSource ??
              "Market Data"}
          </p>
        </div>
      </section>

      <div className="mt-8 border-t border-white/5 py-6 text-center text-xs text-slate-600">
        FinPilot AI GÇó Indian NSE &
        BSE market data
      </div>
    </PageShell>
  );
}

function CandlestickChart({
  candles,
  interval,
  selected,
  onSelect,
}: {
  candles: Candle[];
  interval: Interval;
  selected: Candle | null;
  onSelect: (candle: Candle) => void;
}) {
  const width = 1400;
  const height = 560;

  const padding = {
    top: 30,
    right: 85,
    bottom: 60,
    left: 75,
  };

  const plotWidth =
    width -
    padding.left -
    padding.right;

  const plotHeight =
    height -
    padding.top -
    padding.bottom;

  const high = Math.max(
    ...candles.map(
      (item) => item.high
    )
  );

  const low = Math.min(
    ...candles.map(
      (item) => item.low
    )
  );

  const range =
    high - low || 1;

  const y = (value: number) =>
    padding.top +
    ((high - value) /
      range) *
      plotHeight;

  const step =
    plotWidth /
    Math.max(
      candles.length,
      1
    );

  const candleWidth = Math.max(
    2,
    Math.min(
      12,
      step * 0.65
    )
  );

  const tickCount = 6;

  const yTicks = Array.from(
    { length: tickCount },
    (_, index) =>
      high -
      (range *
        index) /
        (tickCount - 1)
  );

  const xIndexes =
    candles.length <= 8
      ? candles.map(
          (_, index) =>
            index
        )
      : Array.from(
          { length: 8 },
          (_, index) =>
            Math.min(
              candles.length - 1,
              Math.round(
                (index *
                  (candles.length -
                    1)) /
                  7
              )
            )
        );

  return (
    <div className="overflow-x-auto rounded-2xl border border-white/5 bg-slate-950/80">
      <div
        className="relative min-w-[1050px]"
        style={{
          aspectRatio:
            `${width}/${height}`,
        }}
      >
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="h-full w-full select-none"
          role="img"
          aria-label="OHLC candlestick chart"
        >
          <rect
            x="0"
            y="0"
            width={width}
            height={height}
            fill="#020617"
          />

          {yTicks.map(
            (tick, index) => {
              const yPos =
                y(tick);

              return (
                <g
                  key={`y-${index}`}
                >
                  <line
                    x1={
                      padding.left
                    }
                    x2={
                      width -
                      padding.right
                    }
                    y1={yPos}
                    y2={yPos}
                    stroke="#1e293b"
                    strokeDasharray="4 5"
                  />

                  <text
                    x={
                      padding.left -
                      12
                    }
                    y={
                      yPos + 4
                    }
                    textAnchor="end"
                    fill="#64748b"
                    fontSize="12"
                  >
                    Gé¦
                    {tick.toLocaleString(
                      "en-IN",
                      {
                        maximumFractionDigits:
                          2,
                        minimumFractionDigits:
                          2,
                      }
                    )}
                  </text>
                </g>
              );
            }
          )}

          {candles.map(
            (candle, index) => {
              const x =
                padding.left +
                index * step +
                step / 2;

              const openY =
                y(candle.open);
              const closeY =
                y(candle.close);
              const highY =
                y(candle.high);
              const lowY =
                y(candle.low);

              const bullish =
                candle.close >=
                candle.open;

              const bodyTop =
                Math.min(
                  openY,
                  closeY
                );

              const bodyHeight =
                Math.max(
                  1.5,
                  Math.abs(
                    openY -
                      closeY
                  )
                );

              const isSelected =
                selected?.timestamp ===
                candle.timestamp;

              return (
                <g
                  key={`${candle.timestamp}-${index}`}
                  onClick={() =>
                    onSelect(
                      candle
                    )
                  }
                  className="cursor-pointer"
                >
                  {isSelected && (
                    <rect
                      x={
                        x -
                        step / 2
                      }
                      y={
                        padding.top
                      }
                      width={step}
                      height={
                        plotHeight
                      }
                      fill="#1d4ed8"
                      opacity="0.10"
                    />
                  )}

                  <line
                    x1={x}
                    x2={x}
                    y1={highY}
                    y2={lowY}
                    stroke={
                      bullish
                        ? "#34d399"
                        : "#f87171"
                    }
                    strokeWidth={
                      isSelected
                        ? 2
                        : 1.2
                    }
                  />

                  <rect
                    x={
                      x -
                      candleWidth /
                        2
                    }
                    y={bodyTop}
                    width={
                      candleWidth
                    }
                    height={
                      bodyHeight
                    }
                    rx="1"
                    fill={
                      bullish
                        ? "#10b981"
                        : "#ef4444"
                    }
                    stroke={
                      bullish
                        ? "#34d399"
                        : "#f87171"
                    }
                    strokeWidth={
                      isSelected
                        ? 1
                        : 0.5
                    }
                  />
                </g>
              );
            }
          )}

          <line
            x1={
              padding.left
            }
            x2={
              width -
              padding.right
            }
            y1={
              height -
              padding.bottom
            }
            y2={
              height -
              padding.bottom
            }
            stroke="#334155"
          />

          {xIndexes.map(
            (index) => {
              const candle =
                candles[index];

              if (!candle)
                return null;

              const x =
                padding.left +
                index * step +
                step / 2;

              return (
                <text
                  key={`x-${index}`}
                  x={x}
                  y={
                    height -
                    padding.bottom +
                    25
                  }
                  textAnchor="middle"
                  fill="#64748b"
                  fontSize="12"
                >
                  {formatAxisTime(
                    candle.timestamp,
                    interval
                  )}
                </text>
              );
            }
          )}

          <text
            x={
              width -
              padding.right
            }
            y={
              padding.top -
              10
            }
            textAnchor="end"
            fill="#64748b"
            fontSize="11"
          >
            {interval ===
            "1d"
              ? "DAILY OHLC"
              : `${intervalLabel(
                  interval
                )} OHLC`}
          </text>
        </svg>
      </div>
    </div>
  );
}

function PageShell({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <main className="min-h-screen bg-[#030712] px-4 py-7 text-white md:px-8">
      <div className="mx-auto max-w-[1500px]">
        {children}
      </div>
    </main>
  );
}

function StatCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5 transition hover:border-blue-500/20">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold text-white">
        {value}
      </p>
    </div>
  );
}

function MiniValue({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-slate-950/60 p-3">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">
        {label}
      </p>

      <p className="mt-1 truncate text-sm font-semibold text-slate-200">
        {value}
      </p>
    </div>
  );
}

function TechnicalCard({
  label,
  value,
  sub,
  positive,
  negative,
}: {
  label: string;
  value: string;
  sub?: string;
  positive?: boolean;
  negative?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-5">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold text-white">
        {value}
      </p>

      {sub && (
        <p
          className={`mt-1 text-xs font-semibold ${
            positive
              ? "text-emerald-400"
              : negative
              ? "text-red-400"
              : "text-slate-500"
          }`}
        >
          {sub}
        </p>
      )}
    </div>
  );
}
