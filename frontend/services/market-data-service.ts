const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://finpilot-ai-q4nk.onrender.com";

async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
      cache: "no-store",
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      data?.message ||
      "Market data request failed"
    );
  }

  return data;
}


// ============================================================
// SEARCH
// ============================================================

export interface MarketInstrument {
  id: number;
  symbol: string;
  name: string;
  instrument_type: string;
  exchange_id?: number | null;
  currency?: string | null;
  country?: string | null;
  sector?: string | null;
  industry?: string | null;
  logo_url?: string | null;
}

export async function searchMarket(
  query: string,
  limit = 20
): Promise<MarketInstrument[]> {
  return apiRequest<MarketInstrument[]>(
    `/api/market/search?q=${encodeURIComponent(query)}&limit=${limit}`
  );
}


// ============================================================
// QUOTE
// ============================================================

export interface MarketQuote {
  price: number | null;
  open: number | null;
  high: number | null;
  low: number | null;
  previous_close: number | null;
  change: number | null;
  change_percent: number | null;
  volume: number | null;
  market_cap: number | null;
  bid: number | null;
  ask: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  market_status?: string | null;
  quote_time?: string | null;
  data_source?: string | null;
}

export interface MarketQuoteResponse {
  instrument: MarketInstrument;
  quote: MarketQuote | null;
}

export async function getMarketQuote(
  symbol: string
): Promise<MarketQuoteResponse> {
  return apiRequest<MarketQuoteResponse>(
    `/api/market/quote/${encodeURIComponent(
      symbol.toUpperCase()
    )}`
  );
}


// ============================================================
// HISTORY
// ============================================================

export interface PriceHistoryItem {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  adjusted_close?: number | null;
  volume?: number | null;
}

export async function getMarketHistory(
  symbol: string,
  timeframe = "1d",
  limit = 365
): Promise<PriceHistoryItem[]> {
  return apiRequest<PriceHistoryItem[]>(
    `/api/market/history/${encodeURIComponent(
      symbol.toUpperCase()
    )}?timeframe=${encodeURIComponent(
      timeframe
    )}&limit=${limit}`
  );
}


// ============================================================
// FUNDAMENTALS
// ============================================================

export interface FundamentalData {
  market_cap?: number | null;
  enterprise_value?: number | null;
  revenue?: number | null;
  net_income?: number | null;
  gross_profit?: number | null;
  operating_income?: number | null;
  total_assets?: number | null;
  total_liabilities?: number | null;
  total_equity?: number | null;
  cash?: number | null;
  debt?: number | null;
  eps?: number | null;
  book_value_per_share?: number | null;
  dividend_per_share?: number | null;
  dividend_yield?: number | null;
  pe_ratio?: number | null;
  pb_ratio?: number | null;
  ps_ratio?: number | null;
  roe?: number | null;
  roa?: number | null;
  debt_to_equity?: number | null;
  fiscal_year?: number | null;
  fiscal_quarter?: number | null;
  report_date?: string | null;
}

export async function getFundamentals(
  symbol: string
): Promise<FundamentalData[]> {
  return apiRequest<FundamentalData[]>(
    `/api/market/fundamentals/${encodeURIComponent(
      symbol.toUpperCase()
    )}`
  );
}


// ============================================================
// TECHNICAL INDICATORS
// ============================================================

export interface TechnicalData {
  timeframe: string;
  calculation_time: string;

  sma_20?: number | null;
  sma_50?: number | null;
  sma_200?: number | null;

  ema_20?: number | null;
  ema_50?: number | null;
  ema_200?: number | null;

  rsi_14?: number | null;

  macd?: number | null;
  macd_signal?: number | null;
  macd_histogram?: number | null;

  bollinger_upper?: number | null;
  bollinger_middle?: number | null;
  bollinger_lower?: number | null;

  volatility?: number | null;

  support?: number | null;
  resistance?: number | null;
}

export async function getTechnicalData(
  symbol: string,
  timeframe = "1d"
): Promise<TechnicalData> {
  return apiRequest<TechnicalData>(
    `/api/market/technical/${encodeURIComponent(
      symbol.toUpperCase()
    )}?timeframe=${encodeURIComponent(timeframe)}`
  );
}


// ============================================================
// NEWS
// ============================================================

export interface MarketNewsItem {
  id: number;
  title: string;
  description?: string | null;
  url?: string | null;
  image_url?: string | null;
  source?: string | null;
  sentiment?: string | null;
  sentiment_score?: number | null;
  published_at?: string | null;
}

export async function getMarketNews(
  symbol: string,
  limit = 20
): Promise<MarketNewsItem[]> {
  return apiRequest<MarketNewsItem[]>(
    `/api/market/news/${encodeURIComponent(
      symbol.toUpperCase()
    )}?limit=${limit}`
  );
}