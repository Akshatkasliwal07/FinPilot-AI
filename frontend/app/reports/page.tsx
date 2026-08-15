import {
  FileText,
  Sparkles,
  TrendingUp,
  Clock,
} from "lucide-react";

export default function ReportsPage() {
  return (
    <main className="min-h-screen bg-[#050a18] text-white">
      <div className="mx-auto max-w-[1400px] space-y-8 px-6 py-10 lg:px-10">

        <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-[#152342] to-[#081122] p-8">
          <span className="rounded-full bg-blue-500/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
            Research Center
          </span>

          <h1 className="mt-5 text-4xl font-extrabold">
            Research Reports
          </h1>

          <p className="mt-3 text-slate-400">
            Your generated stock research and AI analysis reports.
          </p>
        </section>

        <div className="grid gap-6 md:grid-cols-3">

          <ReportStat
            icon={<FileText />}
            title="Reports"
            value="0"
          />

          <ReportStat
            icon={<Sparkles />}
            title="AI Analyses"
            value="0"
          />

          <ReportStat
            icon={<TrendingUp />}
            title="Stocks Researched"
            value="0"
          />

        </div>

        <section className="rounded-3xl border border-white/10 bg-[#0d162b] p-10">

          <div className="flex min-h-[350px] flex-col items-center justify-center text-center">

            <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-500/10">
              <FileText className="h-10 w-10 text-blue-400" />
            </div>

            <h2 className="mt-6 text-2xl font-bold">
              No reports yet
            </h2>

            <p className="mt-3 max-w-md text-slate-400">
              Generate an AI stock analysis from the Stocks page
              and your research reports will appear here.
            </p>

            <button className="mt-6 rounded-xl bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500">
              Start Research
            </button>

          </div>

        </section>

      </div>
    </main>
  );
}

function ReportStat({
  icon,
  title,
  value,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#0d162b] p-6">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
        {icon}
      </div>

      <p className="mt-5 text-sm text-slate-500">
        {title}
      </p>

      <p className="mt-1 text-3xl font-bold">
        {value}
      </p>
    </div>
  );
}