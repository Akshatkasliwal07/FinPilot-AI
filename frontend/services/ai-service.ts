import { apiRequest } from "@/lib/api";

export interface AIAnalysisRequest {
  symbol: string;
  current_price: number;
  technical_indicators: {
    rsi: number;
    sma20: number;
    ema20: number;
    macd: number;
  };
  latest_news: Array<{
    title: string;
    description: string;
  }>;
}

export interface AIAnalysis {
  recommendation: string;
  confidence: number;
  reason: string;
}

interface AIAnalysisResponse {
  success: boolean;
  message: string;
  data: AIAnalysis;
}

export async function analyzeStock(
  request: AIAnalysisRequest
): Promise<AIAnalysis> {
  const response = await apiRequest<AIAnalysisResponse>(
    "/ai/analyze",
    {
      method: "POST",
      authenticated: true,
      body: JSON.stringify(request),
    }
  );

  return response.data;
}