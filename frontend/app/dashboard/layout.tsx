import Sidebar from "@/components/dashboard/Sidebar";
import TopNavbar from "@/components/dashboard/TopNavbar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen w-full overflow-x-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-white">
      {/* Sidebar */}
      <Sidebar />

      {/* Main application area */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top navigation */}
        <TopNavbar />

        {/* Dashboard content */}
        <main
          className="
            min-w-0
            flex-1
            overflow-x-hidden
            overflow-y-auto
            px-4
            py-5
            sm:px-6
            sm:py-6
            lg:px-8
            lg:py-8
          "
        >
          <div className="mx-auto w-full max-w-[1800px]">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}