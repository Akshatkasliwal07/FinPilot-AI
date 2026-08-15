"use client";

import {
  Search,
  TrendingUp,
  Plus,
  Loader2,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import { useRouter } from "next/navigation";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

// ============================================================
// TYPES
// ============================================================

interface Stock {
  id: number | null;

  symbol: string;

  company_name?: string;

  name?: string;

  sector?: string | null;

  exchange?: string | null;

  currency?: string | null;

  country?: string | null;

  industry?: string | null;

  yahoo_symbol?: string | null;

  data_source?: string | null;

  logo_url?: string | null;
}

interface LiveStock {
  symbol?: string | null;

  code?: string | null;

  price?: number | string | null;

  open?: number | string | null;

  high?: number | string | null;

  low?: number | string | null;

  previous_close?:
    | number
    | string
    | null;

  previousClose?:
    | number
    | string
    | null;

  change?:
    | number
    | string
    | null;

  change_percent?:
    | number
    | string
    | null;

  change_p?:
    | number
    | string
    | null;

  volume?:
    | number
    | string
    | null;

  timestamp?: string | null;

  market_status?: string | null;

  data_source?: string | null;

  close?:
    | number
    | string
    | null;

  "09. change"?: string;

  "10. change percent"?: string;
}

interface SearchStock
  extends Stock {
  live?: LiveStock;
}

// ============================================================
// COMPONENT
// ============================================================

export default function StockSearch() {
  const router = useRouter();

  const [query, setQuery] =
    useState("");

  const [results, setResults] =
    useState<SearchStock[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [
    trendingStocks,
    setTrendingStocks,
  ] = useState<SearchStock[]>([]);

  // ============================================================
  // API RESPONSE NORMALIZER
  // ============================================================

  const getApiData = (
    result: any
  ): any[] => {
    if (!result) {
      return [];
    }

    if (
      Array.isArray(
        result.data
      )
    ) {
      return result.data;
    }

    if (
      result.data &&
      Array.isArray(
        result.data.items
      )
    ) {
      return result.data.items;
    }

    if (
      result.data &&
      Array.isArray(
        result.data.results
      )
    ) {
      return result.data.results;
    }

    return [];
  };

  // ============================================================
  // NORMALIZE STOCK
  // ============================================================

  const normalizeStock = (
    stock: any
  ): Stock => {
    const rawSymbol = String(
      stock?.symbol ??
        stock?.Code ??
        stock?.code ??
        ""
    )
      .trim()
      .toUpperCase();

    const yahooSymbol =
      String(
        stock?.yahoo_symbol ??
          stock?.provider_symbol ??
          stock?.code ??
          ""
      )
        .trim()
        .toUpperCase();

    let exchange =
      stock?.exchange ??
      stock?.exchange_code ??
      stock?.Exchange ??
      null;

    if (!exchange) {
      if (
        yahooSymbol.endsWith(
          ".NS"
        )
      ) {
        exchange = "NSE";
      } else if (
        yahooSymbol.endsWith(
          ".BO"
        )
      ) {
        exchange = "BSE";
      }
    }

    return {
      id:
        stock?.id !== null &&
        stock?.id !== undefined
          ? Number(
              stock.id
            )
          : null,

      symbol: rawSymbol,

      company_name:
        stock?.company_name ??
        stock?.name ??
        stock?.Name ??
        stock?.Description ??
        rawSymbol ??
        "Unknown Company",

      name:
        stock?.name ??
        stock?.Name ??
        stock?.company_name,

      sector:
        stock?.sector ??
        stock?.Sector ??
        null,

      exchange:
        exchange
          ? String(
              exchange
            ).toUpperCase()
          : null,

      currency:
        stock?.currency ??
        stock?.Currency ??
        "INR",

      country:
        stock?.country ??
        stock?.Country ??
        "India",

      industry:
        stock?.industry ??
        stock?.Industry ??
        null,

      yahoo_symbol:
        yahooSymbol ||
        null,

      data_source:
        stock?.data_source ??
        null,

      logo_url:
        stock?.logo_url ??
        null,
    };
  };

  // ============================================================
  // GET LIVE QUOTE
  // ============================================================

  const getLiveQuote = async (
    symbol: string
  ): Promise<
    LiveStock | undefined
  > => {
    if (!symbol) {
      return undefined;
    }

    try {
      const response =
        await fetch(
          `${API_BASE_URL}/api/market/live/quote/${encodeURIComponent(
            symbol
          )}`,
          {
            cache: "no-store",
          }
        );

      if (!response.ok) {
        return undefined;
      }

      const result =
        await response.json();

      if (
        !result ||
        result.success !== true
      ) {
        return undefined;
      }

      return result.data;
    } catch (error) {
      console.error(
        `Live quote error for ${symbol}:`,
        error
      );

      return undefined;
    }
  };

  // ============================================================
  // GET PROVIDER SYMBOL
  //
  // NSE:
  //   RELIANCE.NS
  //
  // BSE:
  //   RELIANCE.BO
  //
  // If backend gives yahoo_symbol, use it.
  // Otherwise default to NSE.
  // ============================================================

  const getProviderSymbol = (
    stock: Stock
  ) => {
    if (
      stock.yahoo_symbol
    ) {
      return stock.yahoo_symbol;
    }

    if (
      stock.symbol.includes(
        "."
      )
    ) {
      return stock.symbol;
    }

    if (
      stock.exchange ===
      "BSE"
    ) {
      return `${stock.symbol}.BO`;
    }

    return `${stock.symbol}.NS`;
  };

  // ============================================================
  // LOAD POPULAR STOCKS
  //
  // These are only displayed when search is empty.
  // They are NOT the stock universe.
  //
  // Search itself is completely dynamic.
  // ============================================================

  useEffect(() => {
    const loadPopularStocks =
      async () => {
        const symbols = [
          "RELIANCE",
          "TCS",
          "INFY",
          "HDFCBANK",
          "ICICIBANK",
          "SBIN",
        ];

        try {
          const stocks: SearchStock[] =
            [];

          for (const symbol of symbols) {
            try {
              const response =
                await fetch(
                  `${API_BASE_URL}/api/market/search?q=${encodeURIComponent(
                    symbol
                  )}&limit=10`,
                  {
                    cache:
                      "no-store",
                  }
                );

              if (
                !response.ok
              ) {
                continue;
              }

              const result =
                await response.json();

              const data =
                getApiData(
                  result
                );

              if (
                !Array.isArray(
                  data
                )
              ) {
                continue;
              }

              const found =
                data.find(
                  (
                    item: any
                  ) =>
                    String(
                      item?.symbol ??
                        ""
                    )
                      .toUpperCase() ===
                    symbol
                ) ??
                data[0];

              if (!found) {
                continue;
              }

              const stock =
                normalizeStock(
                  found
                );

              const live =
                await getLiveQuote(
                  getProviderSymbol(
                    stock
                  )
                );

              stocks.push({
                ...stock,
                live,
              });
            } catch (error) {
              console.error(
                `Popular ${symbol} error:`,
                error
              );
            }
          }

          setTrendingStocks(
            stocks
          );
        } catch (error) {
          console.error(
            "Popular stocks error:",
            error
          );
        }
      };

    loadPopularStocks();
  }, []);

  // ============================================================
  // SEARCH ANY INDIAN STOCK
  // ============================================================

  useEffect(() => {
    const trimmedQuery =
      query.trim();

    if (!trimmedQuery) {
      setResults([]);
      setLoading(false);
      return;
    }

    const timer =
      setTimeout(
        async () => {
          try {
            setLoading(true);

            const response =
              await fetch(
                `${API_BASE_URL}/api/market/search?q=${encodeURIComponent(
                  trimmedQuery
                )}&limit=20`,
                {
                  cache:
                    "no-store",
                }
              );

            const result =
              await response.json();

            if (
              !response.ok ||
              result?.success !==
                true
            ) {
              throw new Error(
                result?.error ??
                  result?.detail ??
                  "Unable to search stocks."
              );
            }

            const rawStocks =
              getApiData(
                result
              );

            if (
              !Array.isArray(
                rawStocks
              )
            ) {
              setResults([]);
              return;
            }

            // ------------------------------------------------
            // NORMALIZE
            // ------------------------------------------------

            const stocks =
              rawStocks
                .map(
                  (
                    stock: any
                  ) =>
                    normalizeStock(
                      stock
                    )
                )
                .filter(
                  (
                    stock
                  ) => {
                    if (
                      !stock.symbol
                    ) {
                      return false;
                    }

                    const country =
                      String(
                        stock.country ??
                          ""
                      ).toLowerCase();

                    const currency =
                      String(
                        stock.currency ??
                          ""
                      ).toUpperCase();

                    return (
                      country ===
                        "" ||
                      country.includes(
                        "india"
                      ) ||
                      currency ===
                        "INR"
                    );
                  }
                );

            // ------------------------------------------------
            // FETCH LIVE DATA
            // ------------------------------------------------

            const stocksWithLiveData =
              await Promise.all(
                stocks.map(
                  async (
                    stock
                  ) => {
                    const providerSymbol =
                      getProviderSymbol(
                        stock
                      );

                    const live =
                      await getLiveQuote(
                        providerSymbol
                      );

                    return {
                      ...stock,
                      live,
                    };
                  }
                )
              );

            setResults(
              stocksWithLiveData
            );
          } catch (error) {
            console.error(
              "Stock search error:",
              error
            );

            setResults([]);
          } finally {
            setLoading(
              false
            );
          }
        },
        350
      );

    return () =>
      clearTimeout(
        timer
      );
  }, [query]);

  // ============================================================
  // FORMAT PRICE
  // ============================================================

  const formatPrice = (
    price?:
      | number
      | string
      | null
  ) => {
    if (
      price === null ||
      price === undefined ||
      price === ""
    ) {
      return "--";
    }

    const value =
      Number(price);

    if (
      !Number.isFinite(
        value
      )
    ) {
      return "--";
    }

    return `₹${value.toLocaleString(
      "en-IN",
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    )}`;
  };

  // ============================================================
  // GET CHANGE %
  // ============================================================

  const getChangePercent = (
    live?: LiveStock
  ) => {
    if (!live) {
      return null;
    }

    const value =
      live.change_percent ??
      live.change_p ??
      live[
        "10. change percent"
      ];

    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return null;
    }

    const number =
      Number(
        String(value).replace(
          "%",
          ""
        )
      );

    return Number.isFinite(
      number
    )
      ? number
      : null;
  };

  // ============================================================
  // FORMAT CHANGE %
  // ============================================================

  const formatChangePercent = (
    live?: LiveStock
  ) => {
    const value =
      getChangePercent(
        live
      );

    if (
      value === null
    ) {
      return "--";
    }

    return `${
      value >= 0
        ? "+"
        : ""
    }${value.toFixed(
      2
    )}%`;
  };

  // ============================================================
  // OPEN STOCK DETAILS
  // ============================================================

  const openStock = (
    stock: Stock
  ) => {
    /*
     * The details page receives the normal symbol:
     *
     * /stocks/IRCTC
     *
     * The backend then dynamically resolves the
     * correct Indian market data.
     */

    router.push(
      `/stocks/${encodeURIComponent(
        stock.symbol
      )}`
    );
  };

  // ============================================================
  // STOCK RESULT ROW
  // ============================================================

  const StockResult = ({
    stock,
  }: {
    stock: SearchStock;
  }) => {
    const change =
      getChangePercent(
        stock.live
      );

    const positive =
      change === null
        ? true
        : change >= 0;

    return (
      <button
        type="button"
        onClick={() =>
          openStock(
            stock
          )
        }
        className="
          flex
          w-full
          items-center
          justify-between
          rounded-2xl
          border
          border-white/5
          bg-slate-900/70
          p-4
          text-left
          transition
          hover:border-blue-500/40
          hover:bg-slate-900
        "
      >
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-white">
              {stock.symbol}
            </h4>

            {stock.exchange && (
              <span
                className="
                  rounded-md
                  bg-blue-500/10
                  px-2
                  py-0.5
                  text-[10px]
                  font-bold
                  uppercase
                  text-blue-400
                "
              >
                {stock.exchange}
              </span>
            )}
          </div>

          <p className="mt-1 truncate text-sm text-slate-400">
            {stock.company_name}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            India
            {stock.currency
              ? ` • ${stock.currency}`
              : ""}
          </p>
        </div>

        <div className="ml-4 shrink-0 text-right">
          <p className="font-semibold text-white">
            {formatPrice(
              stock.live?.price
            )}
          </p>

          <p
            className={`mt-1 text-sm font-medium ${
              positive
                ? "text-green-400"
                : "text-red-400"
            }`}
          >
            {formatChangePercent(
              stock.live
            )}
          </p>
        </div>
      </button>
    );
  };

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div
      className="
        rounded-3xl
        border
        border-white/10
        bg-white/5
        p-6
        shadow-xl
        backdrop-blur-xl
      "
    >
      {/* HEADER */}

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">
            Stock Explorer
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Search any Indian NSE/BSE stock
          </p>
        </div>

        <div className="rounded-xl bg-blue-500/10 p-3">
          <Search className="h-5 w-5 text-blue-400" />
        </div>
      </div>

      {/* SEARCH INPUT */}

      <div className="relative mt-6">
        <Search
          className="
            absolute
            left-4
            top-1/2
            h-5
            w-5
            -translate-y-1/2
            text-slate-400
          "
        />

        <input
          type="text"
          value={query}
          onChange={(
            event
          ) =>
            setQuery(
              event.target
                .value
            )
          }
          placeholder="Search any NSE/BSE stock..."
          className="
            w-full
            rounded-2xl
            border
            border-white/10
            bg-slate-900/60
            py-4
            pl-12
            pr-12
            text-white
            outline-none
            transition
            placeholder:text-slate-500
            focus:border-blue-500
          "
        />

        {loading && (
          <Loader2
            className="
              absolute
              right-4
              top-1/2
              h-5
              w-5
              -translate-y-1/2
              animate-spin
              text-blue-400
            "
          />
        )}
      </div>

      {/* SEARCH RESULTS */}

      {query.trim() && (
        <div className="mt-3 space-y-2">
          {!loading &&
            results.length ===
              0 && (
              <div
                className="
                  rounded-2xl
                  bg-slate-900/50
                  p-4
                  text-sm
                  text-slate-400
                "
              >
                No Indian NSE/BSE
                stock found for "
                {query}"
              </div>
            )}

          {results.map(
            (
              stock,
              index
            ) => (
              <StockResult
                key={`${stock.id ?? "dynamic"}-${stock.symbol}-${stock.exchange ?? "IN"}-${index}`}
                stock={stock}
              />
            )
          )}

          {results.length >
            0 && (
            <p className="px-2 pt-2 text-xs text-slate-500">
              Click a stock to open
              full live details →
            </p>
          )}
        </div>
      )}

      {/* POPULAR STOCKS */}

      {!query.trim() && (
        <div className="mt-8">
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-400" />

            <h3 className="font-semibold text-white">
              Popular Indian Stocks
            </h3>
          </div>

          <div className="space-y-3">
            {trendingStocks.map(
              (stock) => {
                const change =
                  getChangePercent(
                    stock.live
                  );

                const positive =
                  change ===
                    null ||
                  change >= 0;

                return (
                  <div
                    key={`${stock.id ?? "dynamic"}-${stock.symbol}`}
                    onClick={() =>
                      openStock(
                        stock
                      )
                    }
                    className="
                      flex
                      cursor-pointer
                      items-center
                      justify-between
                      rounded-2xl
                      bg-slate-900/50
                      p-4
                      transition
                      hover:bg-slate-900
                    "
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold text-white">
                          {stock.symbol}
                        </h4>

                        {stock.exchange && (
                          <span className="text-[10px] font-bold text-blue-400">
                            {stock.exchange}
                          </span>
                        )}
                      </div>

                      <p className="truncate text-sm text-slate-400">
                        {stock.company_name}
                      </p>
                    </div>

                    <div className="ml-4 flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-semibold text-white">
                          {formatPrice(
                            stock
                              .live
                              ?.price
                          )}
                        </p>

                        <span
                          className={`text-sm font-medium ${
                            positive
                              ? "text-green-400"
                              : "text-red-400"
                          }`}
                        >
                          {formatChangePercent(
                            stock.live
                          )}
                        </span>
                      </div>

                      <button
                        type="button"
                        onClick={(
                          event
                        ) => {
                          event.stopPropagation();

                          openStock(
                            stock
                          );
                        }}
                        className="
                          rounded-xl
                          bg-blue-600
                          p-2
                          text-white
                          transition
                          hover:bg-blue-500
                        "
                        title="Open stock details"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                );
              }
            )}

            {trendingStocks.length ===
              0 && (
              <div className="rounded-2xl bg-slate-900/50 p-4 text-sm text-slate-500">
                Loading Indian stocks...
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}