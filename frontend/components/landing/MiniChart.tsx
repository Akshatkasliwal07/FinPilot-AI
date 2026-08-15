"use client";

export default function MiniChart() {
  const bars = [40, 55, 45, 70, 85, 60, 95];

  return (
    <div className="mt-6 flex items-end gap-2">
      {bars.map((bar, index) => (
        <div
          key={index}
          className="flex-1 rounded-full bg-gradient-to-t from-blue-600 to-cyan-400 transition-all duration-500 hover:scale-y-110"
          style={{
            height: `${bar}px`,
          }}
        />
      ))}
    </div>
  );
}