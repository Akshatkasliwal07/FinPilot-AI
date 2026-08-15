"use client";

const ticker = [
  {
    symbol: "RELIANCE",
    price: "₹3,210.45",
    change: "+2.31%",
  },
  {
    symbol: "TCS",
    price: "₹4,125.30",
    change: "+1.08%",
  },
  {
    symbol: "INFY",
    price: "₹1,845.60",
    change: "-0.72%",
  },
  {
    symbol: "HDFCBANK",
    price: "₹1,730.25",
    change: "+0.95%",
  },
  {
    symbol: "ICICIBANK",
    price: "₹1,215.50",
    change: "+1.52%",
  },
  {
    symbol: "SBIN",
    price: "₹892.30",
    change: "-0.42%",
  },
];

const items = [...ticker, ...ticker];

export default function MarketTicker() {
  return (
    <section className="overflow-hidden border-y border-white/10 bg-slate-950/60 py-4 backdrop-blur-xl">
      <div className="ticker-track flex w-max gap-6">
        {items.map((stock, index) => (
          <div
            key={index}
            className="flex min-w-max items-center gap-4 rounded-full border border-white/10 bg-white/5 px-6 py-3"
          >
            <span className="font-bold">
              {stock.symbol}
            </span>

            <span className="text-slate-300">
              {stock.price}
            </span>

            <span
              className={
                stock.change.startsWith("+")
                  ? "font-semibold text-green-400"
                  : "font-semibold text-red-400"
              }
            >
              {stock.change}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}