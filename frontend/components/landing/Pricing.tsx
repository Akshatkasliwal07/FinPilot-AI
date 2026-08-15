"use client";

import { Check, Sparkles } from "lucide-react";

const plans = [
  {
    name: "Starter",
    price: "$0",
    description: "Perfect for beginners exploring the market.",
    popular: false,
    features: [
      "AI Stock Search",
      "Market Dashboard",
      "Basic Portfolio",
      "5 AI Queries / Day",
    ],
  },
  {
    name: "Pro",
    price: "$19",
    description: "Best for active investors.",
    popular: true,
    features: [
      "Unlimited AI Analysis",
      "Live Market Data",
      "ETF Comparison",
      "Portfolio Analytics",
      "Smart Alerts",
      "Priority Support",
    ],
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For financial advisors & institutions.",
    popular: false,
    features: [
      "Dedicated AI Models",
      "Custom Integrations",
      "Unlimited Users",
      "Advanced Security",
      "24/7 Support",
    ],
  },
];

export default function Pricing() {
  return (
    <section className="py-32">

      <div className="mx-auto max-w-7xl">

        {/* Header */}

        <div className="text-center">

          <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-5 py-2 text-sm text-blue-400">
            Pricing
          </span>

          <h2 className="mt-6 text-5xl font-bold">
            Simple Pricing
          </h2>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
            Start free and upgrade when you need more AI insights
            and advanced investment tools.
          </p>

        </div>

        {/* Billing Toggle */}

        <div className="mt-10 flex justify-center">

          <div className="flex rounded-full border border-white/10 bg-white/5 p-1">

            <button className="rounded-full bg-blue-600 px-6 py-2 font-medium">
              Monthly
            </button>

            <button className="rounded-full px-6 py-2 text-slate-400 transition hover:text-white">
              Yearly
            </button>

          </div>

        </div>

        {/* Cards */}

        <div className="mt-20 grid gap-8 lg:grid-cols-3">

          {plans.map((plan) => (

            <div
              key={plan.name}
              className={`relative overflow-hidden rounded-3xl border p-8 backdrop-blur-xl transition-all duration-500 hover:-translate-y-2 ${
                plan.popular
                  ? "border-blue-500 bg-gradient-to-b from-blue-600/10 to-cyan-500/10 shadow-2xl shadow-blue-500/20"
                  : "border-white/10 bg-white/5 hover:border-blue-500/30"
              }`}
            >

              {plan.popular && (

                <div className="absolute right-6 top-6 flex items-center gap-2 rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold">

                  <Sparkles className="h-4 w-4" />

                  Most Popular

                </div>

              )}

              <h3 className="text-3xl font-bold">
                {plan.name}
              </h3>

              <p className="mt-4 text-slate-400">
                {plan.description}
              </p>

              <div className="mt-8">

                <span className="text-5xl font-extrabold">
                  {plan.price}
                </span>

                {plan.price !== "Custom" && (
                  <span className="text-slate-400">
                    /month
                  </span>
                )}

              </div>

              <div className="mt-10 space-y-4">

                {plan.features.map((feature) => (

                  <div
                    key={feature}
                    className="flex items-center gap-3"
                  >

                    <Check className="h-5 w-5 text-green-400" />

                    <span>{feature}</span>

                  </div>

                ))}

              </div>

              <button
                className={`mt-10 w-full rounded-2xl py-4 font-semibold transition ${
                  plan.popular
                    ? "bg-blue-600 hover:bg-blue-500"
                    : "border border-white/10 bg-white/5 hover:bg-white/10"
                }`}
              >
                {plan.price === "Custom"
                  ? "Contact Sales"
                  : "Get Started"}
              </button>

            </div>

          ))}

        </div>

      </div>

    </section>
  );
}