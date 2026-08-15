"use client";

import {
  BrainCircuit,
  TrendingUp,
  ShieldCheck,
  Rocket,
} from "lucide-react";

const timeline = [
  {
    title: "AI Research",
    description:
      "Advanced machine learning models analyze thousands of market signals.",
    icon: BrainCircuit,
  },
  {
    title: "Market Intelligence",
    description:
      "Live stock prices, ETFs, indices and financial news in one place.",
    icon: TrendingUp,
  },
  {
    title: "Portfolio Protection",
    description:
      "AI risk scoring helps investors understand portfolio exposure.",
    icon: ShieldCheck,
  },
  {
    title: "Investment Confidence",
    description:
      "Make smarter financial decisions with institutional-grade insights.",
    icon: Rocket,
  },
];

const stats = [
  {
    value: "50K+",
    label: "Active Investors",
  },
  {
    value: "99.8%",
    label: "AI Accuracy",
  },
  {
    value: "5M+",
    label: "Market Data Points",
  },
  {
    value: "24/7",
    label: "AI Availability",
  },
];

export default function Timeline() {
  return (
    <section className="py-32">

      <div className="mx-auto max-w-7xl">

        <div className="mb-20 text-center">

          <span className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-5 py-2 text-sm text-cyan-400">
            Why FinPilot AI
          </span>

          <h2 className="mt-6 text-5xl font-bold">
            From Market Data
            <br />
            To Better Decisions
          </h2>

          <p className="mx-auto mt-6 max-w-3xl text-lg text-slate-400">
            Every feature is designed to help investors
            analyze faster, reduce uncertainty,
            and make informed investment decisions.
          </p>

        </div>

        <div className="grid gap-20 lg:grid-cols-2">

          {/* Timeline */}

          <div className="relative">

            <div className="absolute left-7 top-0 h-full w-px bg-white/10" />

            <div className="space-y-12">

              {timeline.map((item) => {

                const Icon = item.icon;

                return (

                  <div
                    key={item.title}
                    className="relative flex gap-6"
                  >

                    <div className="relative z-10 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-cyan-500">

                      <Icon className="h-7 w-7 text-white" />

                    </div>

                    <div>

                      <h3 className="text-2xl font-bold">
                        {item.title}
                      </h3>

                      <p className="mt-3 leading-7 text-slate-400">
                        {item.description}
                      </p>

                    </div>

                  </div>

                );
              })}

            </div>

          </div>

          {/* Stats */}

          <div className="grid grid-cols-2 gap-6">

            {stats.map((stat) => (

              <div
                key={stat.label}
                className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10"
              >

                <h3 className="text-5xl font-extrabold text-blue-400">
                  {stat.value}
                </h3>

                <p className="mt-4 text-slate-400">
                  {stat.label}
                </p>

              </div>

            ))}

          </div>

        </div>

      </div>

    </section>
  );
}