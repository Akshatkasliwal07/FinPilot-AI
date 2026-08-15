"use client";

import {
  ArrowUpRight,
  Clock3,
  Newspaper,
} from "lucide-react";

import { useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

interface NewsArticle {
  title: string;
  source: string;
  published_at: string;
  url: string;
  sentiment: string;
}

interface NewsResponse {
  symbol: string;
  overall_sentiment: string;
  confidence: number;
  articles: NewsArticle[];
}

export default function MarketNews() {
  const [news, setNews] = useState<NewsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE_URL}/news?limit=5`,
          {
            cache: "no-store",
          }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {
          throw new Error(
            result?.error ||
              result?.detail ||
              result?.message ||
              "Unable to load market news."
          );
        }

        setNews(result.data);
      } catch (err) {
        console.error("Market news error:", err);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load market news."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  const formatTime = (value: string) => {
    if (!value) return "";

    const year = Number(value.slice(0, 4));
    const month = Number(value.slice(4, 6)) - 1;
    const day = Number(value.slice(6, 8));
    const hour = Number(value.slice(9, 11));
    const minute = Number(value.slice(11, 13));

    const date = new Date(
      year,
      month,
      day,
      hour,
      minute
    );

    return date.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const sentimentColor = (sentiment: string) => {
    if (sentiment === "Bullish") {
      return "bg-green-500/10 text-green-400";
    }

    if (sentiment === "Bearish") {
      return "bg-red-500/10 text-red-400";
    }

    return "bg-slate-500/10 text-slate-400";
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">
            Market News
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Latest financial headlines
          </p>
        </div>

        <div className="rounded-xl bg-blue-500/10 p-3">
          <Newspaper className="h-5 w-5 text-blue-400" />
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((item) => (
            <div
              key={item}
              className="h-32 animate-pulse rounded-2xl bg-slate-900/50"
            />
          ))}
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* News */}
      {!loading && !error && news && (
        <>
          {/* Market Sentiment */}
         <div className="mb-5 flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-4">
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-500">
                Market Sentiment
              </p>

              <p
                className={`mt-2 inline-block rounded-full px-3 py-1 text-sm font-semibold ${sentimentColor(
                  news.overall_sentiment
                )}`}
              >
                {news.overall_sentiment}
              </p>
            </div>

           <div className="shrink-0 text-right">
  <p className="text-xs text-slate-500">
    AI Confidence
  </p>

  <p className="mt-1 text-xl font-bold text-cyan-400">
    {news.confidence}%
  </p>
</div>
          </div>

          <div className="space-y-4">
            {news.articles.map((article, index) => (
              <div
                key={`${article.title}-${index}`}
                className="group rounded-2xl border border-transparent bg-slate-900/50 p-5 transition-all duration-300 hover:border-blue-500/30 hover:bg-slate-900"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-medium ${sentimentColor(
                        article.sentiment
                      )}`}
                    >
                      {article.sentiment}
                    </span>

                    <h3 className="mt-3 text-lg font-semibold leading-7 transition group-hover:text-blue-400">
                      {article.title}
                    </h3>

                    <div className="mt-4 flex flex-wrap items-center gap-5 text-sm text-slate-400">
                      <div className="flex items-center gap-1">
                        <Clock3 className="h-4 w-4" />
                        {formatTime(
                          article.published_at
                        )}
                      </div>

                      <span>
                        {article.source}
                      </span>
                    </div>
                  </div>

                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0 rounded-xl bg-white/5 p-3 transition hover:bg-blue-500/20"
                  >
                    <ArrowUpRight className="h-5 w-5" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}