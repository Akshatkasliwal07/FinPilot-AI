"use client";

export default function BackgroundEffects() {
  return (
    <>
      <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_top_right,#2563eb25,transparent_40%),radial-gradient(circle_at_bottom_left,#06b6d425,transparent_40%)]" />

      <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:60px_60px]" />

      <div className="absolute left-1/3 top-20 h-72 w-72 rounded-full bg-blue-500/20 blur-[120px]" />

      <div className="absolute right-10 bottom-20 h-96 w-96 rounded-full bg-cyan-500/20 blur-[150px]" />
    <div
  className="
    absolute inset-0
    bg-[linear-gradient(to_right,#1e293b22_1px,transparent_1px),
        linear-gradient(to_bottom,#1e293b22_1px,transparent_1px)]
    bg-[size:60px_60px]
    [mask-image:radial-gradient(circle_at_center,black,transparent_90%)]
  "
/></>
  );
}