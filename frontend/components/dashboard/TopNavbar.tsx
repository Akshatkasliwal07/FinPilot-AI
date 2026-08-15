"use client";

import {
  Search,
  Bell,
  UserCircle2,
  TrendingUp,
  TrendingDown,
  Loader2,
  Settings,
  LayoutDashboard,
  LogOut,
} from "lucide-react";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import { useRouter } from "next/navigation";

// ============================================================
// API
// ============================================================

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

// ============================================================
// TYPES
// ============================================================

interface StockResult {
  id?: number | null;
  symbol: string;
  name?: string | null;
  company_name?: string | null;
  exchange?: string | null;
  currency?: string | null;
  country?: string | null;
  sector?: string | null;
  industry?: string | null;
  yahoo_symbol?: string | null;
}

interface MarketIndex {
  symbol: string;
  price: number | null;
  previous_close: number | null;
  change: number | null;
  change_percent: number | null;
  timestamp?: string | null;
  market_status?: string;
  data_source?: string;
}

interface IndicesResponse {
  "NIFTY 50"?: MarketIndex;
  SENSEX?: MarketIndex;
}

// ============================================================
// COMPONENT
// ============================================================

export default function TopNavbar() {
  const router = useRouter();

  // ==========================================================
  // SEARCH STATE
  // ==========================================================

  const [query, setQuery] =
    useState("");

  const [results, setResults] =
    useState<StockResult[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [showResults, setShowResults] =
    useState(false);

  const searchRef =
    useRef<HTMLDivElement | null>(
      null
    );

  // ==========================================================
  // MARKET INDEX STATE
  // ==========================================================

  const [nifty, setNifty] =
    useState<MarketIndex | null>(
      null
    );

  const [sensex, setSensex] =
    useState<MarketIndex | null>(
      null
    );

  const [indicesLoading, setIndicesLoading] =
    useState(true);

  // ==========================================================
  // NOTIFICATION STATE
  // ==========================================================

  const [
    showNotifications,
    setShowNotifications,
  ] = useState(false);

  // ==========================================================
  // PROFILE STATE
  // ==========================================================

  const [
    showProfile,
    setShowProfile,
  ] = useState(false);

  const profileRef =
    useRef<HTMLDivElement | null>(
      null
    );

  // ==========================================================
  // FETCH NIFTY + SENSEX
  // ==========================================================

  const fetchIndices =
    async () => {
      try {
        setIndicesLoading(true);

        const response =
          await fetch(
            `${API_BASE_URL}/api/market/live/indices`,
            {
              cache: "no-store",
            }
          );

        if (!response.ok) {
          throw new Error(
            `HTTP ${response.status}`
          );
        }

        const result =
          await response.json();

        if (
          !result?.success
        ) {
          throw new Error(
            result?.error ??
              "Unable to load market indices"
          );
        }

        const data =
          result.data as IndicesResponse;

        setNifty(
          data?.["NIFTY 50"] ??
            null
        );

        setSensex(
          data?.SENSEX ??
            null
        );
      } catch (error) {
        console.error(
          "Failed to load market indices:",
          error
        );

        setNifty(null);
        setSensex(null);
      } finally {
        setIndicesLoading(
          false
        );
      }
    };

  // ==========================================================
  // INITIAL LOAD + AUTO REFRESH
  // ==========================================================

  useEffect(() => {
    fetchIndices();

    const interval =
      setInterval(
        fetchIndices,
        60_000
      );

    return () =>
      clearInterval(
        interval
      );
  }, []);

  // ==========================================================
  // NORMALIZE STOCK SEARCH RESULT
  // ==========================================================

  const normalizeStock = (
    stock: any
  ): StockResult => {
    let exchange =
      stock?.exchange ??
      stock?.exchange_code ??
      null;

    const providerSymbol =
      String(
        stock?.yahoo_symbol ??
          stock?.provider_symbol ??
          stock?.code ??
          ""
      )
        .trim()
        .toUpperCase();

    if (!exchange) {
      if (
        providerSymbol.endsWith(
          ".NS"
        )
      ) {
        exchange = "NSE";
      }

      if (
        providerSymbol.endsWith(
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
          ? Number(stock.id)
          : null,

      symbol: String(
        stock?.symbol ??
          stock?.Code ??
          stock?.code ??
          ""
      )
        .trim()
        .toUpperCase(),

      name:
        stock?.name ??
        stock?.Name ??
        stock?.Description ??
        null,

      company_name:
        stock?.company_name ??
        stock?.name ??
        stock?.Name ??
        stock?.Description ??
        null,

      exchange: exchange
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

      sector:
        stock?.sector ??
        stock?.Sector ??
        null,

      industry:
        stock?.industry ??
        stock?.Industry ??
        null,

      yahoo_symbol:
        providerSymbol ||
        null,
    };
  };

  // ==========================================================
  // GET SEARCH DATA
  // ==========================================================

  const getSearchData = (
    result: any
  ): any[] => {
    if (
      Array.isArray(
        result?.data
      )
    ) {
      return result.data;
    }

    if (
      Array.isArray(
        result?.data?.items
      )
    ) {
      return result.data.items;
    }

    if (
      Array.isArray(
        result?.data?.results
      )
    ) {
      return result.data.results;
    }

    return [];
  };

  // ==========================================================
  // SEARCH STOCKS
  // ==========================================================

  useEffect(() => {
    const searchText =
      query.trim();

    if (!searchText) {
      setResults([]);
      setLoading(false);
      setShowResults(false);

      return;
    }

    setShowResults(true);

    const timer =
      setTimeout(
        async () => {
          try {
            setLoading(true);

            const response =
              await fetch(
                `${API_BASE_URL}/api/market/search?q=${encodeURIComponent(
                  searchText
                )}&limit=10`,
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
              setResults([]);
              return;
            }

            const data =
              getSearchData(
                result
              );

            const stocks =
              data
                .map(
                  (
                    item: any
                  ) =>
                    normalizeStock(
                      item
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

            setResults(
              stocks
            );
          } catch (error) {
            console.error(
              "Navbar stock search error:",
              error
            );

            setResults([]);
          } finally {
            setLoading(
              false
            );
          }
        },
        300
      );

    return () =>
      clearTimeout(
        timer
      );
  }, [query]);

  // ==========================================================
  // CLOSE SEARCH ON OUTSIDE CLICK
  // ==========================================================

  useEffect(() => {
    const handleOutsideClick = (
      event: MouseEvent
    ) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(
          event.target as Node
        )
      ) {
        setShowResults(
          false
        );
      }
    };

    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);

  // ==========================================================
  // CLOSE PROFILE ON OUTSIDE CLICK
  // ==========================================================

  useEffect(() => {
    const handleOutsideProfile = (
      event: MouseEvent
    ) => {
      if (
        profileRef.current &&
        !profileRef.current.contains(
          event.target as Node
        )
      ) {
        setShowProfile(
          false
        );
      }
    };

    document.addEventListener(
      "mousedown",
      handleOutsideProfile
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideProfile
      );
    };
  }, []);

  // ==========================================================
  // OPEN STOCK DETAIL
  // ==========================================================

  const openStock = (
    stock: StockResult
  ) => {
    if (!stock.symbol) {
      return;
    }

    setShowResults(false);
    setQuery("");

    router.push(
      `/stocks/${encodeURIComponent(
        stock.symbol
      )}`
    );
  };

  // ==========================================================
  // SEARCH KEYBOARD HANDLER
  // ==========================================================

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (
      event.key === "Escape"
    ) {
      setShowResults(false);
      return;
    }

    if (
      event.key === "Enter" &&
      results.length > 0
    ) {
      openStock(
        results[0]
      );
    }
  };

  // ==========================================================
  // FORMAT INDEX PRICE
  // ==========================================================

  const formatIndexPrice = (
    value: number | null
  ) => {
    if (
      value === null ||
      !Number.isFinite(value)
    ) {
      return "--";
    }

    return value.toLocaleString(
      "en-IN",
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    );
  };

  // ==========================================================
  // INDEX CARD
  // ==========================================================

  const IndexCard = ({
    title,
    data,
  }: {
    title: string;
    data: MarketIndex | null;
  }) => {
    const change =
      data?.change_percent ??
      null;

    const isPositive =
      change !== null &&
      change >= 0;

    const isNegative =
      change !== null &&
      change < 0;

    return (
      <div
        className={`
          rounded-xl
          px-4
          py-2
          ${
            isNegative
              ? "bg-red-500/10"
              : "bg-green-500/10"
          }
        `}
      >
        <div className="text-xs text-slate-400">
          {title}
        </div>

        <div className="mt-0.5 text-sm font-semibold text-white">
          {indicesLoading
            ? "--"
            : formatIndexPrice(
                data?.price ??
                  null
              )}
        </div>

        <div
          className={`
            flex
            items-center
            gap-1
            text-xs
            font-semibold
            ${
              isPositive
                ? "text-green-400"
                : isNegative
                ? "text-red-400"
                : "text-slate-400"
            }
          `}
        >
          {isPositive ? (
            <TrendingUp
              size={13}
            />
          ) : isNegative ? (
            <TrendingDown
              size={13}
            />
          ) : null}

          {change !== null
            ? `${
                change >= 0
                  ? "+"
                  : ""
              }${change.toFixed(
                2
              )}%`
            : "--"}
        </div>
      </div>
    );
  };

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <header
      className="
        sticky
        top-0
        z-40
        border-b
        border-white/10
        bg-slate-950/70
        backdrop-blur-xl
      "
    >
      <div
        className="
          flex
          h-20
          items-center
          justify-between
          px-8
        "
      >
        {/* ==================================================
            LEFT SIDE
        ================================================== */}

        <div
          className="
            flex
            items-center
            gap-6
          "
        >
          {/* =================================================
              SEARCH
          ================================================= */}

          <div
            ref={searchRef}
            className="
              relative
              w-[420px]
            "
          >
            <Search
              className="
                absolute
                left-4
                top-1/2
                -translate-y-1/2
                text-slate-400
              "
              size={18}
            />

            <input
              type="text"
              value={query}
              onChange={(
                event
              ) => {
                setQuery(
                  event.target
                    .value
                );

                setShowResults(
                  true
                );
              }}
              onFocus={() => {
                if (
                  query.trim()
                ) {
                  setShowResults(
                    true
                  );
                }
              }}
              onKeyDown={
                handleKeyDown
              }
              placeholder="Search Stocks, ETFs..."
              autoComplete="off"
              className="
                w-full
                rounded-2xl
                border
                border-white/10
                bg-white/5
                py-3
                pl-12
                pr-12
                text-white
                outline-none
                backdrop-blur-xl
                transition-all
                focus:border-blue-500
                focus:ring-2
                focus:ring-blue-500/20
              "
            />

            {loading && (
              <Loader2
                className="
                  absolute
                  right-4
                  top-1/2
                  -translate-y-1/2
                  animate-spin
                  text-blue-400
                "
                size={18}
              />
            )}

            {/* SEARCH RESULTS */}

            {showResults &&
              query.trim() && (
                <div
                  className="
                    absolute
                    left-0
                    right-0
                    top-[calc(100%+10px)]
                    z-50
                    max-h-[420px]
                    overflow-y-auto
                    rounded-2xl
                    border
                    border-white/10
                    bg-slate-950
                    p-2
                    shadow-2xl
                  "
                >
                  {loading && (
                    <div
                      className="
                        flex
                        items-center
                        gap-3
                        px-4
                        py-4
                        text-sm
                        text-slate-400
                      "
                    >
                      <Loader2
                        size={16}
                        className="animate-spin text-blue-400"
                      />

                      Searching Indian
                      stocks...
                    </div>
                  )}

                  {!loading &&
                    results.length ===
                      0 && (
                      <div className="px-4 py-5 text-center">
                        <p className="text-sm font-medium text-white">
                          No Indian stock
                          found
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          Try a NSE or BSE
                          stock symbol or
                          company name.
                        </p>
                      </div>
                    )}

                  {!loading &&
                    results.map(
                      (
                        stock,
                        index
                      ) => (
                        <button
                          key={`${stock.id ?? "dynamic"}-${stock.symbol}-${stock.exchange ?? "IN"}-${index}`}
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
                            rounded-xl
                            px-4
                            py-3
                            text-left
                            transition
                            hover:bg-white/5
                          "
                        >
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-white">
                                {
                                  stock.symbol
                                }
                              </span>

                              {stock.exchange && (
                                <span
                                  className="
                                    rounded-md
                                    bg-blue-500/10
                                    px-2
                                    py-0.5
                                    text-[10px]
                                    font-bold
                                    text-blue-400
                                  "
                                >
                                  {
                                    stock.exchange
                                  }
                                </span>
                              )}
                            </div>

                            <p
                              className="
                                mt-1
                                truncate
                                text-xs
                                text-slate-400
                              "
                            >
                              {stock.company_name ??
                                stock.name ??
                                stock.symbol}
                            </p>
                          </div>

                          <span
                            className="
                              ml-4
                              shrink-0
                              text-xs
                              text-slate-500
                            "
                          >
                            View →
                          </span>
                        </button>
                      )
                    )}
                </div>
              )}
          </div>

          {/* =================================================
              LIVE INDIAN INDICES
          ================================================= */}

          <div
            className="
              hidden
              items-center
              gap-5
              xl:flex
            "
          >
            <IndexCard
              title="NIFTY 50"
              data={nifty}
            />

            <IndexCard
              title="SENSEX"
              data={sensex}
            />
          </div>
        </div>

        {/* ==================================================
            RIGHT SIDE
        ================================================== */}

        <div
          className="
            flex
            items-center
            gap-4
          "
        >
          {/* =================================================
              NOTIFICATIONS
          ================================================= */}

          <div className="relative">
            <button
              type="button"
              onClick={() => {
                setShowNotifications(
                  (previous) =>
                    !previous
                );

                setShowProfile(
                  false
                );
              }}
              className="
                relative
                rounded-xl
                border
                border-white/10
                bg-white/5
                p-3
                text-white
                transition
                hover:bg-blue-500/20
              "
              aria-label="Notifications"
              aria-expanded={
                showNotifications
              }
            >
              <Bell size={20} />

              {(nifty !== null ||
                sensex !== null) && (
                <span
                  className="
                    absolute
                    right-2
                    top-2
                    h-2
                    w-2
                    rounded-full
                    bg-blue-400
                  "
                />
              )}
            </button>

            {/* NOTIFICATION PANEL */}

            {showNotifications && (
              <div
                className="
                  absolute
                  right-0
                  top-[calc(100%+12px)]
                  z-50
                  w-[360px]
                  overflow-hidden
                  rounded-2xl
                  border
                  border-white/10
                  bg-slate-950
                  shadow-2xl
                "
              >
                <div
                  className="
                    flex
                    items-center
                    justify-between
                    border-b
                    border-white/10
                    px-5
                    py-4
                  "
                >
                  <div>
                    <h3 className="font-semibold text-white">
                      Notifications
                    </h3>

                    <p className="mt-1 text-xs text-slate-500">
                      Indian market updates
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      setShowNotifications(
                        false
                      )
                    }
                    className="
                      text-xs
                      text-slate-500
                      transition
                      hover:text-white
                    "
                  >
                    Close
                  </button>
                </div>

                {/* NIFTY */}

                {nifty && (
                  <div
                    className="
                      border-b
                      border-white/5
                      px-5
                      py-4
                      transition
                      hover:bg-white/5
                    "
                  >
                    <div className="flex items-center gap-3">
                      {(
                        nifty.change_percent ??
                        0
                      ) >= 0 ? (
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

                      <div>
                        <p className="text-sm font-medium text-white">
                          NIFTY 50
                        </p>

                        <p className="mt-1 text-xs text-slate-400">
                          {formatIndexPrice(
                            nifty.price
                          )}{" "}
                          •{" "}
                          {(
                            nifty.change_percent ??
                            0
                          ) >= 0
                            ? "+"
                            : ""}
                          {(
                            nifty.change_percent ??
                            0
                          ).toFixed(
                            2
                          )}
                          %
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* SENSEX */}

                {sensex && (
                  <div
                    className="
                      border-b
                      border-white/5
                      px-5
                      py-4
                      transition
                      hover:bg-white/5
                    "
                  >
                    <div className="flex items-center gap-3">
                      {(
                        sensex.change_percent ??
                        0
                      ) >= 0 ? (
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

                      <div>
                        <p className="text-sm font-medium text-white">
                          SENSEX
                        </p>

                        <p className="mt-1 text-xs text-slate-400">
                          {formatIndexPrice(
                            sensex.price
                          )}{" "}
                          •{" "}
                          {(
                            sensex.change_percent ??
                            0
                          ) >= 0
                            ? "+"
                            : ""}
                          {(
                            sensex.change_percent ??
                            0
                          ).toFixed(
                            2
                          )}
                          %
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* EMPTY */}

                {!nifty &&
                  !sensex && (
                    <div className="px-5 py-8 text-center">
                      <Bell
                        size={24}
                        className="mx-auto text-slate-600"
                      />

                      <p className="mt-3 text-sm text-slate-300">
                        No market notifications
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Indian market updates
                        will appear here.
                      </p>
                    </div>
                  )}

                <div className="border-t border-white/10 px-5 py-3">
                  <p className="text-[11px] text-slate-600">
                    Data refreshes automatically
                    every 60 seconds.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* =================================================
              PROFILE
          ================================================= */}

          <div
            ref={profileRef}
            className="relative"
          >
            <button
              type="button"
              onClick={() => {
                setShowProfile(
                  (previous) =>
                    !previous
                );

                setShowNotifications(
                  false
                );
              }}
              className="
                rounded-xl
                border
                border-white/10
                bg-white/5
                p-3
                text-white
                transition
                hover:bg-blue-500/20
              "
              aria-label="User profile"
              aria-expanded={
                showProfile
              }
            >
              <UserCircle2
                size={22}
              />
            </button>

            {/* PROFILE DROPDOWN */}

            {showProfile && (
              <div
                className="
                  absolute
                  right-0
                  top-[calc(100%+12px)]
                  z-50
                  w-[250px]
                  overflow-hidden
                  rounded-2xl
                  border
                  border-white/10
                  bg-slate-950
                  shadow-2xl
                "
              >
                {/* PROFILE HEADER */}

                <div
                  className="
                    border-b
                    border-white/10
                    px-5
                    py-4
                  "
                >
                  <div className="flex items-center gap-3">
                    <UserCircle2
                      size={38}
                      className="text-blue-400"
                    />

                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-white">
                        My Account
                      </p>

                      <p className="mt-1 truncate text-xs text-slate-500">
                        FinPilot AI
                      </p>
                    </div>
                  </div>
                </div>

                {/* DASHBOARD */}

                <button
                  type="button"
                  onClick={() => {
                    setShowProfile(
                      false
                    );

                    router.push(
                      "/dashboard"
                    );
                  }}
                  className="
                    flex
                    w-full
                    items-center
                    gap-3
                    px-5
                    py-3
                    text-left
                    text-sm
                    text-slate-300
                    transition
                    hover:bg-white/5
                    hover:text-white
                  "
                >
                  <LayoutDashboard
                    size={18}
                  />

                  Dashboard
                </button>

                {/* SETTINGS */}

                <button
                  type="button"
                  onClick={() => {
                    setShowProfile(
                      false
                    );

                    router.push(
                      "/settings"
                    );
                  }}
                  className="
                    flex
                    w-full
                    items-center
                    gap-3
                    px-5
                    py-3
                    text-left
                    text-sm
                    text-slate-300
                    transition
                    hover:bg-white/5
                    hover:text-white
                  "
                >
                  <Settings
                    size={18}
                  />

                  Settings
                </button>

                {/* DIVIDER */}

                <div className="border-t border-white/10" />

                {/* SIGN OUT */}

                <button
                  type="button"
                  onClick={() => {
                    setShowProfile(
                      false
                    );

                    localStorage.removeItem(
                      "token"
                    );

                    localStorage.removeItem(
                      "access_token"
                    );

                    localStorage.removeItem(
                      "refresh_token"
                    );

                    router.push(
                      "/login"
                    );
                  }}
                  className="
                    flex
                    w-full
                    items-center
                    gap-3
                    px-5
                    py-3
                    text-left
                    text-sm
                    text-red-400
                    transition
                    hover:bg-red-500/10
                  "
                >
                  <LogOut
                    size={18}
                  />

                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}