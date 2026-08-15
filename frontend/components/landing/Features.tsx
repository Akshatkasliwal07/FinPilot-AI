import {
  BarChart3,
  BrainCircuit,
  Newspaper,
  Wallet,
  TrendingUp,
  ShieldCheck,
} from "lucide-react";

const features = [
  {
    icon: BarChart3,
    title: "Market Analytics",
    description:
      "Analyze stock performance with advanced AI-powered market insights.",
  },
  {
    icon: BrainCircuit,
    title: "AI Research",
    description:
      "Get instant company summaries, financial reports, and recommendations.",
  },
  {
    icon: Newspaper,
    title: "Live News",
    description:
      "Stay updated with real-time financial news affecting your investments.",
  },
  {
    icon: Wallet,
    title: "Portfolio Tracker",
    description:
      "Track your investments and monitor portfolio performance effortlessly.",
  },
  {
    icon: TrendingUp,
    title: "ETF Analysis",
    description:
      "Compare ETFs, returns, risk, and sector exposure in one dashboard.",
  },
  {
    icon: ShieldCheck,
    title: "Secure Platform",
    description:
      "Enterprise-grade security to keep your financial data protected.",
  },
];

export default function Features() {
  return (
    <section className="bg-slate-950 py-28 text-white">
      <div className="mx-auto max-w-7xl px-6">
        {/* Heading */}
        <div className="text-center">
          <p className="text-blue-400 font-semibold uppercase tracking-widest">
            Features
          </p>

          <h2 className="mt-4 text-5xl font-bold">
            Why Choose FinPilot AI?
          </h2>

          <p className="mx-auto mt-6 max-w-3xl text-lg text-slate-400">
            Everything investors need to analyze markets,
            discover opportunities, and make smarter financial decisions.
          </p>
        </div>

        {/* Cards */}
        <div className="mt-20 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon;

            return (
              <div
                key={index}
                className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 transition-all duration-300 hover:-translate-y-2 hover:border-blue-500 hover:shadow-xl hover:shadow-blue-500/10"
              >
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600/20">
                  <Icon className="h-8 w-8 text-blue-400" />
                </div>

                <h3 className="mt-8 text-2xl font-semibold">
                  {feature.title}
                </h3>

                <p className="mt-4 leading-7 text-slate-400">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}