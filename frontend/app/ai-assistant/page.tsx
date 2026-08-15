import AIAssistant from "@/components/dashboard/AIAssistant";

export default function AIAssistantPage() {
  return (
    <main className="min-h-screen bg-[#050a18] text-white">
      <div className="mx-auto max-w-[1200px] space-y-8 px-6 py-10 lg:px-10">

        <section className="rounded-3xl border border-cyan-500/20 bg-gradient-to-br from-[#10233d] to-[#081122] p-8">
          <span className="rounded-full bg-cyan-500/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
            FinPilot Intelligence
          </span>

          <h1 className="mt-5 text-4xl font-extrabold">
            AI Financial Assistant
          </h1>

          <p className="mt-3 text-slate-400">
            Analyze stocks, understand market signals and get
            AI-powered financial research insights.
          </p>
        </section>

        <AIAssistant />

        <div className="rounded-2xl border border-yellow-500/20 bg-yellow-500/5 p-5 text-sm text-yellow-300">
          ⚠ AI-generated analysis is for research and educational
          purposes only. It is not personalized financial advice.
        </div>

      </div>
    </main>
  );
}