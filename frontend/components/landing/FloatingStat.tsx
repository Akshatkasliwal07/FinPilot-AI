"use client";

interface FloatingStatProps {
  title: string;
  value: string;
  color: string;
}

export default function FloatingStat({
  title,
  value,
  color,
}: FloatingStatProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur-xl shadow-xl">
      <p className="text-xs uppercase tracking-wider text-slate-400">
        {title}
      </p>

      <h3 className={`mt-2 text-2xl font-bold ${color}`}>
        {value}
      </h3>
    </div>
  );
}