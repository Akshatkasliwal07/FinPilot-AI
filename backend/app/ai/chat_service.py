import os
import re
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf
import requests
from langchain_groq import ChatGroq

from app.ai.chat_schema import AIChatRequest


IST = ZoneInfo("Asia/Kolkata")


# ------------------------------------------------------------
# LIQUID NSE STOCK UNIVERSE
# ------------------------------------------------------------

NSE_UNIVERSE = [
    # Major / large-cap
    "RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY",
    "BHARTIARTL", "LT", "AXISBANK", "KOTAKBANK", "BAJFINANCE",
    "MARUTI", "M&M", "SUNPHARMA", "ITC", "NTPC", "POWERGRID",
    "TITAN", "ADANIENT", "ADANIPORTS", "ETERNAL", "TRENT",
    "TATAMOTORS", "TATASTEEL", "JIOFIN", "HCLTECH", "WIPRO",
    "TECHM", "COFORGE", "INDUSINDBK", "BANKBARODA", "PNB",
    "CANBK", "IDFCFIRSTB", "FEDERALBNK", "RECLTD", "PFC",
    "ONGC", "COALINDIA", "BPCL", "IOC", "GAIL", "HAL", "BEL",
    "SIEMENS", "ABB", "BHEL", "IRCTC", "ULTRACEMCO", "ASIANPAINT",
    "HINDUNILVR", "MARICO", "NESTLEIND", "BRITANNIA", "DABUR",
    "TATACONSUM", "PIDILITIND", "HAVELLS", "VOLTAS", "DLF",
    "LODHA", "OBEROIRLTY", "GODREJPROP", "DIVISLAB", "CIPLA",
    "DRREDDY", "LUPIN", "AUROPHARMA", "BIOCON", "EICHERMOT",
    "HEROMOTOCO", "TVSMOTOR", "BAJAJ-AUTO", "ASHOKLEY",
    "MOTHERSON", "BOSCHLTD", "APOLLOHOSP", "MAXHEALTH",
    "ZYDUSLIFE", "ADANIPOWER", "TATAPOWER", "JSWENERGY",
    "NHPC", "TORNTPOWER", "VEDL", "HINDALCO", "JSWSTEEL",
    "JINDALSTEL", "SAIL", "NMDC", "INDIGO", "IRFC", "RVNL",
    "DMART", "PAYTM", "SWIGGY", "NYKAA", "JUBLFOOD", "ZOMATO",
    "INDHOTEL", "M&MFIN", "CHOLAFIN", "SHRIRAMFIN", "BAJAJFINSV",
    "HDFCLIFE", "SBILIFE", "ICICIPRULI", "LICI", "SRF", "AMBER",
    "BSE", "MCX", "CDSL", "POLYCAB", "DIXON", "KAYNES",
]

# ------------------------------------------------------------
# COMPANY ALIASES
# ------------------------------------------------------------

ALIASES = {
    "RELIANCE": "RELIANCE",
    "RELIANCE INDUSTRIES": "RELIANCE",

    "HDFC": "HDFCBANK",
    "HDFC BANK": "HDFCBANK",
    "HDFCBANK": "HDFCBANK",

    "ICICI": "ICICIBANK",
    "ICICI BANK": "ICICIBANK",
    "ICICIBANK": "ICICIBANK",

    "STATE BANK": "SBIN",
    "SBI": "SBIN",
    "SBIN": "SBIN",

    "TATA CONSULTANCY": "TCS",
    "TCS": "TCS",

    "INFOSYS": "INFY",
    "INFY": "INFY",

    "AIRTEL": "BHARTIARTL",
    "BHARTI AIRTEL": "BHARTIARTL",
    "BHARTIARTL": "BHARTIARTL",

    "LARSEN": "LT",
    "L&T": "LT",
    "LT": "LT",

    "AXIS BANK": "AXISBANK",
    "AXISBANK": "AXISBANK",

    "KOTAK": "KOTAKBANK",
    "KOTAK BANK": "KOTAKBANK",
    "KOTAKBANK": "KOTAKBANK",

    "BAJAJ FINANCE": "BAJFINANCE",
    "BAJFINANCE": "BAJFINANCE",

    "MARUTI": "MARUTI",
    "MARUTI SUZUKI": "MARUTI",

    "M&M": "M&M",
    "MAHINDRA": "M&M",
    "MAHINDRA AND MAHINDRA": "M&M",

    "SUN PHARMA": "SUNPHARMA",
    "SUNPHARMA": "SUNPHARMA",

    "ITC": "ITC",

    "NTPC": "NTPC",

    "POWERGRID": "POWERGRID",
    "POWER GRID": "POWERGRID",

    "TITAN": "TITAN",

    "ADANI ENTERPRISES": "ADANIENT",
    "ADANIENT": "ADANIENT",

    "ADANI PORTS": "ADANIPORTS",
    "ADANIPORTS": "ADANIPORTS",

    "IRCTC": "IRCTC",

    # New / commonly requested stocks
    "TRENT": "TRENT",
    "TRENT LIMITED": "TRENT",
    "ETERNAL": "ETERNAL",
    "ETERNAL LIMITED": "ETERNAL",
    "ZOMATO": "ETERNAL",
    "ZOMATO LIMITED": "ETERNAL",
    "TATA MOTORS": "TATAMOTORS",
    "TATAMOTORS": "TATAMOTORS",
    "TATA STEEL": "TATASTEEL",
    "JIOFIN": "JIOFIN",
    "JIO FINANCIAL": "JIOFIN",
    "HCL TECH": "HCLTECH",
    "HCL TECHNOLOGIES": "HCLTECH",
    "WIPRO": "WIPRO",
    "TECH MAHINDRA": "TECHM",
    "COFORGE": "COFORGE",
    "INDUSIND BANK": "INDUSINDBK",
    "BANK OF BARODA": "BANKBARODA",
    "PUNJAB NATIONAL BANK": "PNB",
    "CANARA BANK": "CANBK",
    "FEDERAL BANK": "FEDERALBNK",
    "IDFC FIRST BANK": "IDFCFIRSTB",
    "LIFE INSURANCE CORPORATION": "LICI",
    "LIC": "LICI",
    "BAJAJ AUTO": "BAJAJ-AUTO",
    "TVS MOTOR": "TVSMOTOR",
    "HERO MOTOCORP": "HEROMOTOCO",
    "ASHOK LEYLAND": "ASHOKLEY",
    "MOTHERSON": "MOTHERSON",
    "MAHINDRA FINANCE": "M&MFIN",
    "BAJAJ FINSERV": "BAJAJFINSV",
    "BAJAJ FINSERV LIMITED": "BAJAJFINSV",
    "SHRIRAM FINANCE": "SHRIRAMFIN",
    "CHOLA FINANCE": "CHOLAFIN",
    "HINDUSTAN UNILEVER": "HINDUNILVR",
    "NESTLE INDIA": "NESTLEIND",
    "BRITANNIA": "BRITANNIA",
    "MARICO": "MARICO",
    "DABUR": "DABUR",
    "TATA CONSUMER": "TATACONSUM",
    "ASIAN PAINTS": "ASIANPAINT",
    "ULTRATECH": "ULTRACEMCO",
    "ULTRATECH CEMENT": "ULTRACEMCO",
    "COAL INDIA": "COALINDIA",
    "POWER GRID": "POWERGRID",
    "POWERGRID": "POWERGRID",
    "ONGC": "ONGC",
    "INDIAN OIL": "IOC",
    "IOC": "IOC",
    "BPCL": "BPCL",
    "GAIL": "GAIL",
    "HINDALCO": "HINDALCO",
    "JSW STEEL": "JSWSTEEL",
    "JINDAL STEEL": "JINDALSTEL",
    "ADANI POWER": "ADANIPOWER",
    "TATA POWER": "TATAPOWER",
    "JSW ENERGY": "JSWENERGY",
    "NHPC": "NHPC",
    "IRFC": "IRFC",
    "RVNL": "RVNL",
    "DLF": "DLF",
    "DMART": "DMART",
    "AVENUE SUPERMARTS": "DMART",
    "PAYTM": "PAYTM",
    "ONE97 COMMUNICATIONS": "PAYTM",
    "SWIGGY": "SWIGGY",
    "NYKAA": "NYKAA",
    "FSN E-COMMERCE": "NYKAA",
    "BSE": "BSE",
    "MCX": "MCX",
    "CDSL": "CDSL",
    "POLYCAB": "POLYCAB",
    "DIXON": "DIXON",
    "DIXON TECHNOLOGIES": "DIXON",
    "HAL": "HAL",
    "HINDUSTAN AERONAUTICS": "HAL",
    "BEL": "BEL",
    "BHARAT ELECTRONICS": "BEL",
}


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def _now_ist() -> datetime:
    return datetime.now(IST)


def _yahoo_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()

    if symbol == "M&M":
        return "M&M.NS"

    return f"{symbol}.NS"


def _clean_number(value):
    try:
        if pd.isna(value):
            return None

        return float(value)

    except Exception:
        return None


def _calculate_rsi(series: pd.Series, period: int = 14):
    delta = series.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.rolling(period).mean()
    avg_loss = losses.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


def _extract_symbol(message: str) -> str | None:
    """Resolve a known NSE symbol from company names or ticker text."""

    text = message.upper().strip()

    # 1. Exact aliases first.
    for alias in sorted(ALIASES.keys(), key=len, reverse=True):
        if re.search(
            rf"(?<![A-Z0-9]){re.escape(alias)}(?![A-Z0-9])",
            text,
        ):
            return ALIASES[alias]

    # 2. Direct symbol from our scan universe.
    for symbol in NSE_UNIVERSE:
        if re.search(
            rf"(?<![A-Z0-9]){re.escape(symbol)}(?![A-Z0-9])",
            text,
        ):
            return symbol

    # 3. Explicit Yahoo/NSE-style symbol.
    match = re.search(
        r"\b([A-Z][A-Z0-9&-]{1,20})\.NS\b",
        text,
    )
    if match:
        return match.group(1)

    return None


@lru_cache(maxsize=512)
def _search_nse_symbol(query: str) -> str | None:
    """
    Search Yahoo's symbol directory and return an NSE equity symbol.

    This allows FinPilot to analyze stocks outside the hardcoded
    Top-10 scan universe, e.g. TRENT, ETERNAL, HAL, etc.
    """

    query = query.strip()

    if not query:
        return None

    try:
        response = requests.get(
            "https://query1.finance.yahoo.com/v1/finance/search",
            params={
                "q": query,
                "quotesCount": 10,
                "newsCount": 0,
            },
            headers={
                "User-Agent": "Mozilla/5.0 FinPilot-AI/1.0",
            },
            timeout=6,
        )

        response.raise_for_status()

        data = response.json()

        quotes = data.get("quotes", [])

        # Prefer NSE equity listings.
        for quote in quotes:
            symbol = str(
                quote.get("symbol", "")
            ).upper()

            quote_type = str(
                quote.get("quoteType", "")
            ).upper()

            if (
                symbol.endswith(".NS")
                and quote_type in {"EQUITY", "STOCK"}
            ):
                return symbol[:-3]

        # Some Yahoo results omit quoteType.
        for quote in quotes:
            symbol = str(
                quote.get("symbol", "")
            ).upper()

            if symbol.endswith(".NS"):
                return symbol[:-3]

    except Exception:
        return None

    return None


def _candidate_words(message: str) -> list[str]:
    """
    Extract useful words/phrases from a natural-language stock question.
    """

    text = re.sub(
        r"[^A-Z0-9&.-]+",
        " ",
        message.upper(),
    )

    words = text.split()

    ignored = {
        "WHAT", "ABOUT", "ANALYZE", "ANALYSIS", "ANALYSE",
        "STOCK", "STOCKS", "SHARE", "SHARES", "PRICE",
        "TODAY", "CURRENT", "NOW", "RIGHT", "LOOKING",
        "MARKET", "PLEASE", "TELL", "ME", "THE", "IS",
        "OF", "FOR", "BUY", "SELL", "GOOD", "BAD",
        "SHOULD", "CAN", "YOU", "EXPLAIN", "WHY", "HOW",
        "WILL", "DO", "I", "GIVE", "VIEW", "ON",
        "IN", "THIS", "COMPANY", "COMPANIES", "TRADING",
        "TRADE", "INTRADAY", "TARGET", "ENTRY", "STOP",
        "LOSS", "RSI", "EMA", "VOLUME", "SIGNAL",
    }

    return [
        word
        for word in words
        if word not in ignored and len(word) >= 2
    ]


def _resolve_any_stock(message: str) -> str | None:
    """
    Resolve almost any NSE-listed stock mentioned by the user.

    Resolution order:
    1. Known aliases/universe
    2. Explicit .NS symbol
    3. Yahoo symbol search using the full phrase
    4. Yahoo symbol search using useful words

    This keeps Top-10 scanning fast while allowing individual
    analysis of stocks outside NSE_UNIVERSE.
    """

    known = _extract_symbol(message)

    if known:
        return known

    text = message.strip()

    # Search the full message first.
    symbol = _search_nse_symbol(text)

    if symbol:
        return symbol

    # Then try useful word combinations.
    words = _candidate_words(text)

    for size in (3, 2, 1):
        if len(words) < size:
            continue

        for i in range(len(words) - size + 1):
            phrase = " ".join(words[i:i + size])

            symbol = _search_nse_symbol(phrase)

            if symbol:
                return symbol

    return None


# ------------------------------------------------------------
# ONE STOCK
# ------------------------------------------------------------

def fetch_stock_context(symbol: str) -> dict | None:

    try:

        yahoo_symbol = _yahoo_symbol(symbol)

        ticker = yf.Ticker(yahoo_symbol)

        df = ticker.history(
            period="1d",
            interval="5m",
            auto_adjust=False,
        )

        if df is None or df.empty:

            df = ticker.history(
                period="5d",
                interval="15m",
                auto_adjust=False,
            )

        if df is None or df.empty:
            return None

        df = df.dropna(
            subset=["Close"]
        )

        if df.empty:
            return None

        close = df["Close"]

        latest = df.iloc[-1]

        current_price = _clean_number(
            latest["Close"]
        )

        open_price = _clean_number(
            latest["Open"]
        )

        high = _clean_number(
            latest["High"]
        )

        low = _clean_number(
            latest["Low"]
        )

        volume = _clean_number(
            latest["Volume"]
        )

        previous_close = None

        try:
            if len(df) >= 2:
                previous_close = _clean_number(
                    df.iloc[-2]["Close"]
                )
        except Exception:
            pass

        change_percent = None

        if (
            current_price is not None
            and previous_close
        ):
            change_percent = (
                (
                    current_price
                    - previous_close
                )
                / previous_close
            ) * 100

        ema20 = None

        if len(close) >= 20:

            ema20 = _clean_number(
                close.ewm(
                    span=20,
                    adjust=False,
                ).mean().iloc[-1]
            )

        rsi = None

        if len(close) >= 15:

            rsi = _clean_number(
                _calculate_rsi(
                    close
                ).iloc[-1]
            )

        volume_ratio = None

        if (
            volume is not None
            and len(df) >= 20
        ):

            avg_volume = _clean_number(
                df["Volume"]
                .tail(20)
                .mean()
            )

            if avg_volume:
                volume_ratio = (
                    volume / avg_volume
                )

        trend_score = 0

        if (
            current_price is not None
            and ema20 is not None
        ):

            if current_price > ema20:
                trend_score += 1
            else:
                trend_score -= 1

        momentum_score = 0

        if change_percent is not None:

            if change_percent > 1:
                momentum_score += 2

            elif change_percent > 0.25:
                momentum_score += 1

            elif change_percent < -1:
                momentum_score -= 2

            elif change_percent < -0.25:
                momentum_score -= 1

        rsi_score = 0

        if rsi is not None:

            if 50 <= rsi <= 68:
                rsi_score = 2

            elif 68 < rsi <= 75:
                rsi_score = 1

            elif rsi > 75:
                rsi_score = -1

            elif rsi < 30:
                rsi_score = -1

        volume_score = 0

        if volume_ratio is not None:

            if volume_ratio >= 1.5:
                volume_score = 2

            elif volume_ratio >= 1.15:
                volume_score = 1

        score = (
            trend_score
            + momentum_score
            + rsi_score
            + volume_score
        )

        # ----------------------------------------------------
        # Illustrative levels
        # ----------------------------------------------------

        entry = current_price

        stop_loss = None
        target = None

        if current_price is not None:

            stop_loss = round(
                current_price * 0.985,
                2,
            )

            target = round(
                current_price * 1.025,
                2,
            )

        candle_time = None

        try:

            ts = df.index[-1]

            if getattr(
                ts,
                "tzinfo",
                None,
            ) is not None:

                ts = ts.tz_convert(
                    IST
                )

            candle_time = ts.isoformat()

        except Exception:
            candle_time = None

        return {
            "symbol": symbol,
            "price": current_price,
            "open": open_price,
            "high": high,
            "low": low,
            "previous_close": previous_close,
            "change_percent": (
                round(
                    change_percent,
                    2,
                )
                if change_percent is not None
                else None
            ),
            "rsi": (
                round(rsi, 2)
                if rsi is not None
                else None
            ),
            "ema20": (
                round(ema20, 2)
                if ema20 is not None
                else None
            ),
            "volume": volume,
            "volume_ratio": (
                round(
                    volume_ratio,
                    2,
                )
                if volume_ratio is not None
                else None
            ),
            "score": score,
            "entry_reference": entry,
            "illustrative_stop_loss": stop_loss,
            "illustrative_target": target,
            "latest_candle_time": candle_time,
            "data_source": "Yahoo Finance",
        }

    except Exception:
        return None


# ------------------------------------------------------------
# TOP MARKET CANDIDATES
# ------------------------------------------------------------

def scan_top_candidates(
    limit: int = 10,
) -> dict:

    collected = []

    with ThreadPoolExecutor(
        max_workers=5
    ) as executor:

        futures = {
            executor.submit(
                fetch_stock_context,
                symbol,
            ): symbol
            for symbol in NSE_UNIVERSE
        }

        for future in as_completed(
            futures
        ):

            try:

                result = future.result()

                if result:
                    collected.append(
                        result
                    )

            except Exception:
                continue

    collected.sort(
        key=lambda item: (
            item.get("score", -999),
            item.get(
                "change_percent"
            )
            or -999,
        ),
        reverse=True,
    )

    return {
        "scan_time": _now_ist().isoformat(),
        "market": "NSE India",
        "interval": "5m",
        "candidates": collected[:limit],
        "data_source": "Yahoo Finance",
    }


# ------------------------------------------------------------
# SHOULD WE SCAN MARKET?
# ------------------------------------------------------------

def _needs_market_scan(
    message: str,
) -> bool:

    text = message.lower()

    keywords = [
        "today",
        "right now",
        "currently",
        "current",
        "buy",
        "sell",
        "stock",
        "stocks",
        "top 10",
        "top ten",
        "best stock",
        "best stocks",
        "intraday",
        "trade",
        "trading",
        "momentum",
        "market",
        "profit",
        "gain",
        "gainer",
        "breakout",
        "entry",
        "target",
        "stop loss",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# ------------------------------------------------------------
# LLM
# ------------------------------------------------------------

def _get_llm():

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b",
    )

    temperature = float(
        os.getenv(
            "LLM_TEMPERATURE",
            "0.2",
        )
    )

    return ChatGroq(
        api_key=api_key,
        model=model,
        temperature=temperature,
    )


# ------------------------------------------------------------
# MAIN CHAT
# ------------------------------------------------------------

def chat_with_finpilot(
    request: AIChatRequest,
):

    message = request.message.strip()

    if not message:
        raise ValueError(
            "Message cannot be empty."
        )

    market_context = None

    # --------------------------------------------------------
    # Current market request
    # --------------------------------------------------------

    if _needs_market_scan(
        message
    ):

        symbol = _resolve_any_stock(
            message
        )

        if symbol:

            stock = fetch_stock_context(
                symbol
            )

            market_context = {
                "type": "single_stock",
                "scan_time": _now_ist().isoformat(),
                "symbol": symbol,
                "stock": stock,
            }

        else:

            market_context = {
                "type": "market_scan",
                **scan_top_candidates(
                    10
                ),
            }

    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": """
You are FinPilot AI, a friendly and practical financial research assistant.

Your first priority is to understand exactly what the user is asking and answer it in the simplest useful way. The user should understand the answer within a few seconds.

ACCURACY RULES:
1. Never guarantee profit or claim that a stock WILL rise or WILL fall.
2. Never invent current prices, timestamps, indicators, news, company facts, or market conditions.
3. When current FinPilot market data is supplied, use it instead of guessing.
4. Clearly distinguish facts from your interpretation.
5. Never pretend Yahoo Finance data is tick-by-tick live. If data is delayed or the market is closed, say so briefly.
6. If data is missing or unreliable, say so instead of making up an answer.
7. For buy/sell/trading questions, give research-based candidates and reasons. Any entry, stop or target must be clearly labelled illustrative and must never be presented as guaranteed.\n8. If a stock symbol is supplied but market data could not be retrieved, say clearly that the latest data could not be retrieved right now. Do not say the company is unsupported or unknown if the symbol was resolved.

CONVERSATION STYLE:
1. Be natural, friendly and direct, like a helpful finance expert talking to a beginner.
2. Use simple English and avoid unnecessary jargon. Explain a technical term briefly when needed.
3. Answer the actual question first. Do not begin with a long introduction.
4. Keep normal answers SHORT: usually 3–7 short sentences or compact lines.
5. If the user says brief, briefly, short, or quickly, make it even shorter.
6. Only give a detailed answer when the user asks for detail, deep analysis, full analysis, explain properly, or similar.
7. Do not repeat information or restate the user's question.

PRESENTATION RULES — VERY IMPORTANT:
1. Do NOT use Markdown tables.
2. Do NOT use long paragraphs.
3. Do NOT use Markdown headings such as ###.
4. Do NOT use **bold** markers, backticks, horizontal rules, or raw pipe characters.
5. Use clean short labels, short lines, and spacing so the answer is easy to scan.
6. Use only a few helpful emojis when they improve readability.
7. Put the main conclusion near the top.
8. For multiple stocks, use a numbered list instead of a table.
9. Keep each stock to 1–3 short lines unless the user asks for detailed analysis.

PREFERRED MARKET FORMAT:
📊 Market view
Overall: Slightly positive / neutral / slightly negative.
One short sentence explaining why.

🔎 What matters
• Short point.
• Short point.

⭐ Stocks to watch
1. HDFC Bank — ₹728.50
   Signal: Positive | Why: strong volume and supportive trend.
2. Reliance — ₹1,316
   Signal: Positive | Why: buying activity is strong.

⚠️ Note
Prices can change after the latest available market-data timestamp.

PREFERRED SINGLE-STOCK FORMAT:
📌 TCS
Price: ₹X
View: Positive / Neutral / Cautious
Why: one or two simple reasons.
Watch: one clear confirmation or risk level.

STOCK DATA:
When a single-stock market context is supplied, answer specifically about that stock. Use its price, change, RSI, EMA, volume and score only when those values are available.\n\nTOP-10 REQUEST:\nGive 10 concise numbered candidates. For each include only the stock name, current/reference price if available, simple signal, and one short reason. Do not create a large table or research report.

BUY/SELL OR INTRADAY REQUEST:
Give the best available candidates from the supplied data. If useful, provide Entry, Stop and Target on separate short lines. Clearly label them illustrative and never guarantee the outcome.

EDUCATIONAL QUESTIONS:
For RSI, EMA, volume and similar topics, explain in plain language with a simple example. Keep it short unless the user asks for more detail.

The response should feel like a clean, modern financial assistant — not a research report. This is financial research and decision support, not guaranteed financial advice.
""",
        }
    ]

    for item in request.history[-12:]:

        messages.append(
            {
                "role": item.role,
                "content": item.content,
            }
        )

    # --------------------------------------------------------
    # Add current market context
    # --------------------------------------------------------

    context_text = ""

    if market_context:

        context_text = (
            "\n\nCURRENT FINPILOT MARKET DATA:\n"
            + str(
                market_context
            )
        )

    messages.append(
        {
            "role": "user",
            "content": (
                message
                + context_text
            ),
        }
    )

    llm = _get_llm()

    response = llm.invoke(
        messages
    )

    reply = response.content

    if isinstance(
        reply,
        list,
    ):

        reply = "".join(
            str(
                item.get(
                    "text",
                    item,
                )
            )
            if isinstance(
                item,
                dict,
            )
            else str(item)
            for item in reply
        )

    # Final UI cleanup: prevent accidental Markdown from appearing literally.
    reply = str(reply).strip()
    reply = re.sub(r"^#{1,6}\s*", "", reply, flags=re.MULTILINE)
    reply = reply.replace("**", "")
    reply = reply.replace("```", "")
    reply = re.sub(r"^\s*---\s*$", "", reply, flags=re.MULTILINE)

    return {
        "reply": reply,

        "market_context":
            market_context,

        "timestamp":
            _now_ist().isoformat(),
    }