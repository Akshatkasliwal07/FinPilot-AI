"use client";

const stats = [
  { value: "50K+", label: "Investors" },
  { value: "99.8%", label: "AI Accuracy" },
  { value: "$5B+", label: "Assets Analyzed" },
];

export default function HeroStats() {
  return (
    <div className="mt-14 grid grid-cols-3 gap-8">
      {stats.map((stat) => (
        <div key={stat.label}>
          <h3 className="text-3xl font-bold">{stat.value}</h3>
          <p className="mt-2 text-slate-400">{stat.label}</p>
        </div>
      ))}
    </div>
  );
}