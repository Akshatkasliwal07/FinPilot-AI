"use client";

import DashboardMockup from "./DashboardMockup";
import FloatingCards from "./FloatingCards";

export default function DashboardPreview() {
  return (
    <div className="relative mt-20">

      <FloatingCards />

      <div className="mx-auto max-w-5xl">
        <DashboardMockup />
      </div>

    </div>
  );
}