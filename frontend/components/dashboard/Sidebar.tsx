"use client";

import {
  LayoutDashboard,
  TrendingUp,
  WalletCards,
  Newspaper,
  Bot,
  FileText,
  Settings,
  ChevronRight,
} from "lucide-react";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const [userName, setUserName] = useState("User");

  useEffect(() => {
    function loadUserName() {
      const storedName =
        localStorage.getItem("user_name") ||
        localStorage.getItem("name") ||
        localStorage.getItem("username");

      if (storedName?.trim()) {
        setUserName(storedName.trim());
      }
    }

    loadUserName();

    window.addEventListener(
      "storage",
      loadUserName
    );

    return () => {
      window.removeEventListener(
        "storage",
        loadUserName
      );
    };
  }, []);

  const menuItems = [
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
    },
    {
      label: "Stocks",
      href: "/stocks",
      icon: TrendingUp,
    },
    {
      label: "ETFs",
      href: "/etfs",
      icon: WalletCards,
    },
    {
      label: "News",
      href: "/news",
      icon: Newspaper,
    },
    {
      label: "AI Assistant",
      href: "/ai-assistant",
      icon: Bot,
    },
    {
      label: "Reports",
      href: "/reports",
      icon: FileText,
    },
    {
      label: "Settings",
      href: "/settings",
      icon: Settings,
    },
  ];

  const firstLetter =
    userName.charAt(0).toUpperCase();

  return (
    <aside className="flex w-[312px] shrink-0 flex-col border-r border-white/10 bg-slate-950">

      {/* =====================================================
          LOGO
      ====================================================== */}

      <div className="border-b border-white/10 px-6 py-7">

        <Link
          href="/dashboard"
          className="block"
        >
          <h1 className="text-4xl font-extrabold tracking-tight text-blue-400">
            FinPilot AI
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Financial Research Platform
          </p>
        </Link>

      </div>

      {/* =====================================================
          NAVIGATION
      ====================================================== */}

      <nav className="flex-1 space-y-2 px-4 py-7">

        {menuItems.map((item) => {
          const Icon = item.icon;

          const active =
            pathname === item.href ||
            (
              item.href !== "/dashboard" &&
              pathname.startsWith(
                `${item.href}/`
              )
            );

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group flex items-center justify-between rounded-2xl px-5 py-4 transition ${
                active
                  ? "border border-blue-500/40 bg-blue-600/20 text-blue-400"
                  : "text-slate-300 hover:bg-white/5 hover:text-white"
              }`}
            >

              <div className="flex items-center gap-4">

                <Icon
                  size={21}
                  className={
                    active
                      ? "text-blue-400"
                      : "text-slate-300"
                  }
                />

                <span className="text-base font-medium">
                  {item.label}
                </span>

              </div>

              {active && (
                <ChevronRight
                  size={18}
                  className="text-blue-400"
                />
              )}

            </Link>
          );
        })}

      </nav>

      {/* =====================================================
          USER PROFILE
      ====================================================== */}

      <div className="border-t border-white/10 p-5">

        <Link
          href="/settings"
          className="block rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-blue-500/30 hover:bg-white/10"
        >

          <div className="flex items-center gap-4">

            {/* Avatar */}

            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-blue-600 text-xl font-bold text-white">
              {firstLetter}
            </div>

            {/* User information */}

            <div className="min-w-0">

              <p className="truncate text-lg font-bold text-white">
                {userName}
              </p>

              <p className="mt-1 text-sm text-slate-400">
                Premium Plan
              </p>

            </div>

          </div>

          {/* Online status */}

          <div className="mt-4 flex items-center gap-2">

            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />

            <span className="text-sm text-emerald-400">
              Online
            </span>

          </div>

        </Link>

      </div>

    </aside>
  );
}