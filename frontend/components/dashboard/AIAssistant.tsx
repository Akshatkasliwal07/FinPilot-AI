"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import {
  Activity,
  Bot,
  BrainCircuit,
  Send,
  Sparkles,
  User,
  X,
} from "lucide-react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://finpilot-ai-q4nk.onrender.com";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface ChatResponse {
  reply: string;
  market_context?: {
    type?: string;
    scan_time?: string;
    market?: string;
    interval?: string;
    candidates?: MarketCandidate[];
    stock?: MarketCandidate | null;
    data_source?: string;
  } | null;
  timestamp: string;
}

interface MarketCandidate {
  symbol: string;
  price: number | null;
  change_percent: number | null;
  rsi: number | null;
  ema20: number | null;
  volume_ratio: number | null;
  score: number;
  entry_reference: number | null;
  illustrative_stop_loss: number | null;
  illustrative_target: number | null;
  latest_candle_time?: string | null;
  data_source?: string;
}

interface APIResult {
  success?: boolean;
  message?: string;
  data?: ChatResponse;
  error?: string;
  detail?: string;
}

const QUICK_PROMPTS = [
  "What is the current market looking like?",
  "Give me the top 10 stocks with strong current momentum.",
  "Analyze TCS right now.",
  "Which stocks should I watch for intraday today?",
  "Explain RSI and how I should use it.",
];

export default function AIAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm FinPilot AI. Ask me about stocks, the market, technical indicators, news, or current trading setups.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  function getAuthHeaders(): Record<string, string> {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;

    const tokenType =
      typeof window !== "undefined"
        ? localStorage.getItem("token_type") || "bearer"
        : "bearer";

    if (!token) {
      throw new Error(
        "Please login before using FinPilot AI."
      );
    }

    return {
      "Content-Type": "application/json",
      Authorization: `${tokenType} ${token}`,
    };
  }

  async function readJson(
    response: Response
  ): Promise<APIResult | null> {
    try {
      return (await response.json()) as APIResult;
    } catch {
      return null;
    }
  }

  async function sendMessage(
    messageOverride?: string
  ) {
    const message = (
      messageOverride ?? input
    ).trim();

    if (!message || loading) {
      return;
    }

    setError("");

    const userMessage: ChatMessage = {
      role: "user",
      content: message,
    };

    const history = messages
      .filter(
        (item) =>
          item.content.trim().length > 0
      )
      .slice(-12);

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/ai/chat`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            message,
            history,
          }),
          cache: "no-store",
        }
      );

      const result = await readJson(
        response
      );

      if (!response.ok) {
        throw new Error(
          result?.error ||
            result?.detail ||
            result?.message ||
            `AI request failed (${response.status}).`
        );
      }

      if (
        result?.success === false
      ) {
        throw new Error(
          result.message ||
            result.error ||
            "FinPilot AI could not process the request."
        );
      }

      if (!result?.data?.reply) {
        throw new Error(
          "FinPilot AI returned an empty response."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.data!.reply,
        },
      ]);

    } catch (err) {
      console.error(
        "FinPilot chatbot error:",
        err
      );

      const message =
        err instanceof Error
          ? err.message
          : "Unable to connect to FinPilot AI.";

      setError(message);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I couldn't process that request. Please check the backend connection and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    void sendMessage();
  }

  function formatMarketCandidate(
    candidate: MarketCandidate
  ) {
    return (
      <div
        key={candidate.symbol}
        className="rounded-2xl border border-white/10 bg-slate-950/50 p-4"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="font-bold text-white">
              {candidate.symbol}
            </p>

            <p className="text-xs text-slate-500">
              Score: {candidate.score}
            </p>
          </div>

          <div className="text-right">
            <p className="font-semibold text-white">
              {candidate.price !== null
                ? `â‚¹${candidate.price.toFixed(2)}`
                : "â€”"}
            </p>

            <p
              className={
                (candidate.change_percent ?? 0) >= 0
                  ? "text-sm text-emerald-400"
                  : "text-sm text-red-400"
              }
            >
              {candidate.change_percent !== null
                ? `${candidate.change_percent >= 0 ? "+" : ""}${candidate.change_percent.toFixed(2)}%`
                : "â€”"}
            </p>
          </div>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-xl bg-white/5 p-2">
            <span className="text-slate-500">
              RSI
            </span>

            <p className="mt-1 font-semibold text-white">
              {candidate.rsi !== null
                ? candidate.rsi.toFixed(2)
                : "â€”"}
            </p>
          </div>

          <div className="rounded-xl bg-white/5 p-2">
            <span className="text-slate-500">
              Volume
            </span>

            <p className="mt-1 font-semibold text-white">
              {candidate.volume_ratio !== null
                ? `${candidate.volume_ratio.toFixed(2)}x`
                : "â€”"}
            </p>
          </div>
        </div>

        {candidate.entry_reference !== null && (
          <div className="mt-3 border-t border-white/5 pt-3 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">
                Reference
              </span>

              <span className="text-white">
                â‚¹
                {candidate.entry_reference.toFixed(
                  2
                )}
              </span>
            </div>

            <div className="mt-1 flex justify-between">
              <span className="text-slate-500">
                Illustrative stop
              </span>

              <span className="text-red-300">
                {candidate.illustrative_stop_loss !==
                null
                  ? `â‚¹${candidate.illustrative_stop_loss.toFixed(2)}`
                  : "â€”"}
              </span>
            </div>

            <div className="mt-1 flex justify-between">
              <span className="text-slate-500">
                Illustrative target
              </span>

              <span className="text-emerald-300">
                {candidate.illustrative_target !==
                null
                  ? `â‚¹${candidate.illustrative_target.toFixed(2)}`
                  : "â€”"}
              </span>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur-xl">

      {/* HEADER */}
      <div className="border-b border-white/10 bg-gradient-to-r from-blue-950/60 to-cyan-950/40 p-6">

        <div className="flex items-start justify-between gap-4">

          <div className="flex items-center gap-4">

            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/10">
              <BrainCircuit className="h-6 w-6 text-cyan-400" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan-400">
                  FinPilot Intelligence
                </p>

                <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-1 text-[10px] font-semibold text-emerald-400">
                  <Activity className="h-3 w-3" />
                  AI ONLINE
                </span>
              </div>

              <h2 className="mt-1 text-2xl font-bold text-white">
                FinPilot AI Assistant
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Ask questions about stocks, markets,
                technical analysis and trading setups.
              </p>
            </div>

          </div>

        </div>
      </div>

      {/* QUICK QUESTIONS */}
      <div className="border-b border-white/10 p-4">

        <div className="mb-3 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-cyan-400" />

          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Quick questions
          </p>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">

          {QUICK_PROMPTS.map(
            (prompt) => (
              <button
                key={prompt}
                type="button"
                disabled={loading}
                onClick={() =>
                  void sendMessage(prompt)
                }
                className="whitespace-nowrap rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-300 transition hover:border-cyan-500/30 hover:bg-cyan-500/10 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {prompt}
              </button>
            )
          )}

        </div>
      </div>

      {/* CHAT */}
      <div className="h-[560px] overflow-y-auto p-5">

        <div className="space-y-5">

          {messages.map(
            (message, index) => {

              const isUser =
                message.role === "user";

              return (
                <div
                  key={`${message.role}-${index}`}
                  className={`flex gap-3 ${
                    isUser
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >

                  {!isUser && (
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10">
                      <Bot className="h-5 w-5 text-cyan-400" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-7 ${
                      isUser
                        ? "rounded-br-md bg-blue-600 text-white"
                        : "rounded-bl-md border border-white/10 bg-slate-900/70 text-slate-300"
                    }`}
                  >
                    <div className="whitespace-pre-wrap">
                      {message.content}
                    </div>
                  </div>

                  {isUser && (
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-500/10">
                      <User className="h-5 w-5 text-blue-400" />
                    </div>
                  )}

                </div>
              );
            }
          )}

          {/* LOADING */}
          {loading && (
            <div className="flex gap-3">

              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10">
                <Bot className="h-5 w-5 text-cyan-400" />
              </div>

              <div className="rounded-2xl rounded-bl-md border border-white/10 bg-slate-900/70 px-5 py-4">

                <div className="flex items-center gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-400" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-400 [animation-delay:120ms]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-400 [animation-delay:240ms]" />
                </div>

              </div>

            </div>
          )}

          <div ref={messagesEndRef} />

        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div className="mx-5 mb-4 flex items-start gap-3 rounded-2xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-300">

          <X className="mt-0.5 h-4 w-4 shrink-0" />

          <p>
            {error}
          </p>

        </div>
      )}

      {/* INPUT */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-white/10 bg-slate-950/40 p-4"
      >

        <div className="flex items-end gap-3">

          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();

                void sendMessage();
              }
            }}
            placeholder="Ask FinPilot AI anything..."
            rows={2}
            disabled={loading}
            className="min-h-[56px] flex-1 resize-none rounded-2xl border border-white/10 bg-slate-900/70 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500/40 disabled:opacity-50"
          />

          <button
            type="submit"
            disabled={
              loading ||
              !input.trim()
            }
            className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </button>

        </div>

        <div className="mt-3 flex items-center justify-between text-[11px] text-slate-600">

          <span>
            Enter to send Â· Shift + Enter for new line
          </span>

          <span>
            Market data may be delayed
          </span>

        </div>

      </form>

      {/* DISCLAIMER */}
      <div className="border-t border-yellow-500/10 bg-yellow-500/5 px-5 py-4 text-xs leading-5 text-yellow-300/70">
        FinPilot AI provides research and educational
        analysis. Market prices can change rapidly.
        Any entry, stop-loss or target shown by the AI is
        illustrative and is not a guaranteed trading signal
        or personalized financial advice.
      </div>

    </div>
  );
}