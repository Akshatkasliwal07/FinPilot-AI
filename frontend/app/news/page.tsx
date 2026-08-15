import MarketNews from "@/components/dashboard/MarketNews";
import TopMovers from "@/components/dashboard/TopMovers";

export default function NewsPage() {
  return (
    <main className="min-h-screen bg-[#050a18] text-white">
      <div className="mx-auto max-w-[1500px] space-y-8 px-6 py-10 lg:px-10">

        <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-[#152342] to-[#081122] p-8">
          <span className="rounded-full bg-blue-500/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
            Market Intelligence
          </span>

          <h1 className="mt-5 text-4xl font-extrabold">
            Market News
          </h1>

          <p className="mt-3 max-w-2xl text-slate-400">
            Stay updated with the latest financial headlines,
            market sentiment and major market movements.
          </p>
        </section>

        <div className="grid gap-8 lg:grid-cols-2">
          <MarketNews />
          <TopMovers />
        </div>

      </div>
    </main>
  );
}