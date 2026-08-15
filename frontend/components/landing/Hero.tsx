"use client";

import { motion } from "framer-motion";

import HeroBadge from "./HeroBadge";
import HeroButtons from "./HeroButtons";
import HeroStats from "./HeroStats";
import MarketTicker from "./MarketTicker";
import DashboardPreview from "./DashboardPreview";

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-slate-950 text-white">

      {/* Background Glow */}
      <div className="absolute left-1/2 top-20 h-96 w-96 -translate-x-1/2 rounded-full bg-blue-600/20 blur-[150px]" />

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative mx-auto flex min-h-screen max-w-7xl flex-col items-center justify-center px-6 text-center"
      >

        <HeroBadge />

        <h1 className="mt-8 max-w-5xl text-5xl font-extrabold leading-tight md:text-7xl">
          Smarter Investing with
          <span className="block bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 bg-clip-text text-transparent">
            FinPilot AI
          </span>
        </h1>

        <p className="mt-8 max-w-3xl text-lg leading-8 text-slate-400 md:text-xl">
          Analyze Stocks, ETFs, Mutual Funds, Company Financials,
          Earnings Reports and Market News using Artificial Intelligence.
        </p>

        <HeroButtons />

        <HeroStats />

        <MarketTicker />

        <DashboardPreview />

      </motion.div>

    </section>
  );
}