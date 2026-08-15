"use client";

import { Star } from "lucide-react";

const testimonials = [
  {
    name: "Rahul Sharma",
    role: "Retail Investor",
    rating: 5,
    quote:
      "FinPilot AI helped me compare ETFs and understand my portfolio in minutes. The AI insights are incredibly useful.",
  },
  {
    name: "Priya Mehta",
    role: "Financial Analyst",
    rating: 5,
    quote:
      "The dashboard is clean, fast and provides all the information I need without switching between multiple websites.",
  },
  {
    name: "Amit Verma",
    role: "Portfolio Manager",
    rating: 5,
    quote:
      "The AI-powered research saves hours every week. Portfolio tracking and market analysis are excellent.",
  },
];

export default function Testimonials() {
  return (
    <section className="py-32">

      <div className="mx-auto max-w-7xl">

        {/* Heading */}

        <div className="mb-16 text-center">

          <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-5 py-2 text-sm text-blue-400">
            Testimonials
          </span>

          <h2 className="mt-6 text-5xl font-bold">
            Trusted by Investors
          </h2>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
            Thousands of investors rely on FinPilot AI
            for smarter investment research and portfolio
            management.
          </p>

        </div>

        {/* Featured Card */}

        <div className="mb-10 rounded-3xl border border-white/10 bg-gradient-to-br from-blue-600/10 to-cyan-500/10 p-10 backdrop-blur-xl">

          <div className="flex items-center gap-1">

            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className="h-5 w-5 fill-yellow-400 text-yellow-400"
              />
            ))}

          </div>

          <h3 className="mt-8 text-3xl font-bold leading-relaxed">
            “FinPilot AI transformed the way I analyze stocks.
            Everything I need is available in one beautiful platform.”
          </h3>

          <div className="mt-8 flex items-center gap-4">

            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 text-xl font-bold">
              AK
            </div>

            <div>

              <h4 className="font-semibold">
                Akash Kulkarni
              </h4>

              <p className="text-slate-400">
                Long-Term Investor
              </p>

            </div>

          </div>

        </div>

        {/* Grid */}

        <div className="grid gap-6 md:grid-cols-3">

          {testimonials.map((item) => (

            <div
              key={item.name}
              className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10"
            >

              <div className="mb-6 flex">

                {[...Array(item.rating)].map((_, i) => (
                  <Star
                    key={i}
                    className="h-5 w-5 fill-yellow-400 text-yellow-400"
                  />
                ))}

              </div>

              <p className="leading-8 text-slate-300">
                "{item.quote}"
              </p>

              <div className="mt-8 flex items-center gap-4">

                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 font-bold">
                  {item.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>

                <div>

                  <h4 className="font-semibold">
                    {item.name}
                  </h4>

                  <p className="text-sm text-slate-400">
                    {item.role}
                  </p>

                </div>

              </div>

            </div>

          ))}

        </div>

      </div>

    </section>
  );
}