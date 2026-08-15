"use client";

import {
  BrainCircuit,
  TrendingUp,
  Wallet,
  Bell,
  Newspaper,
  BarChart3,
} from "lucide-react";

const features = [
  {
    title: "AI Stock Analysis",
    description:
      "Receive institutional-grade insights powered by advanced AI models.",
    icon: BrainCircuit,
    gradient: "from-blue-600 to-cyan-500",
    size: "lg:col-span-2 lg:row-span-2",
  },
  {
    title: "Portfolio Tracking",
    description:
      "Monitor your investments with beautiful analytics.",
    icon: Wallet,
    gradient: "from-emerald-500 to-green-600",
  },
  {
    title: "Live Market",
    description:
      "Real-time stock prices, ETFs and indices.",
    icon: TrendingUp,
    gradient: "from-indigo-500 to-blue-600",
  },
  {
    title: "Price Alerts",
    description:
      "Instant notifications for important market moves.",
    icon: Bell,
    gradient: "from-orange-500 to-red-500",
  },
  {
    title: "Financial News",
    description:
      "AI summarized news from trusted financial sources.",
    icon: Newspaper,
    gradient: "from-pink-500 to-rose-500",
  },
  {
    title: "ETF Comparison",
    description:
      "Compare performance, returns and holdings effortlessly.",
    icon: BarChart3,
    gradient: "from-violet-500 to-purple-600",
  },
];

export default function BentoFeatures() {
  return (
    <section className="py-32">

      <div className="mx-auto max-w-7xl">

        <div className="mb-16 text-center">

          <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-5 py-2 text-sm text-blue-400">
            Features
          </span>

          <h2 className="mt-6 text-5xl font-bold">
            Everything You Need To Invest Smarter
          </h2>

          <p className="mx-auto mt-6 max-w-3xl text-lg text-slate-400">
            AI-powered research, portfolio management,
            real-time analytics and institutional-quality insights
            in one modern platform.
          </p>

        </div>

        <div className="grid auto-rows-[240px] gap-6 lg:grid-cols-4">

          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <div
                key={feature.title}
                className={`${feature.size ?? ""}
                group relative overflow-hidden rounded-3xl border
                border-white/10 bg-white/5 p-8 backdrop-blur-xl
                transition-all duration-500
                hover:-translate-y-2
                hover:border-blue-500/30
                hover:shadow-2xl hover:shadow-blue-500/10`}
              >

                {/* Glow */}
                <div
                  className={`absolute -right-10 -top-10 h-40 w-40 rounded-full bg-gradient-to-br ${feature.gradient} opacity-20 blur-3xl transition-all duration-500 group-hover:scale-125`}
                />

                <div className="relative z-10">

                  <div
                    className={`inline-flex rounded-2xl bg-gradient-to-br ${feature.gradient} p-4`}
                  >
                    <Icon className="h-8 w-8 text-white" />
                  </div>

                  <h3 className="mt-8 text-2xl font-bold">
                    {feature.title}
                  </h3>

                  <p className="mt-4 leading-7 text-slate-400">
                    {feature.description}
                  </p>

                </div>

              </div>
            );
          })}

        </div>

      </div>

    </section>
  );
}