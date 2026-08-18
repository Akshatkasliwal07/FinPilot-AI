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
  Menu,
  X,
} from "lucide-react";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const [userName, setUserName] = useState("User");
  const [isMobileOpen, setIsMobileOpen] = useState(false);

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

    window.addEventListener("storage", loadUserName);

    return () => {
      window.removeEventListener("storage", loadUserName);
    };
  }, []);

  // Close sidebar when changing page
  useEffect(() => {
    setIsMobileOpen(false);
  }, [pathname]);

  // Prevent background scrolling when mobile sidebar is open
  useEffect(() => {
    if (isMobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [isMobileOpen]);

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
    <>
      {/* =====================================================
          MOBILE MENU BUTTON
      ====================================================== */}

      <button
        type="button"
        aria-label={
          isMobileOpen
            ? "Close navigation"
            : "Open navigation"
        }
        aria-expanded={isMobileOpen}
        onClick={() =>
          setIsMobileOpen((previous) => !previous)
        }
        className="
          fixed
          left-4
          top-4
          z-[60]
          flex
          h-11
          w-11
          items-center
          justify-center
          rounded-xl
          border
          border-white/10
          bg-slate-950/95
          text-white
          shadow-xl
          backdrop-blur-xl
          transition
          hover:bg-slate-900
          lg:hidden
        "
      >
        {isMobileOpen ? (
          <X size={22} />
        ) : (
          <Menu size={22} />
        )}
      </button>

      {/* =====================================================
          MOBILE OVERLAY
      ====================================================== */}

      {isMobileOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          onClick={() => setIsMobileOpen(false)}
          className="
            fixed
            inset-0
            z-40
            bg-black/70
            backdrop-blur-[2px]
            lg:hidden
          "
        />
      )}

      {/* =====================================================
          SIDEBAR
      ====================================================== */}

      <aside
        className={`
          fixed
          inset-y-0
          left-0
          z-50
          flex
          w-[290px]
          max-w-[85vw]
          shrink-0
          flex-col
          border-r
          border-white/10
          bg-slate-950
          shadow-2xl
          transition-transform
          duration-300
          ease-in-out

          lg:sticky
          lg:top-0
          lg:z-30
          lg:h-screen
          lg:w-[312px]
          lg:translate-x-0
          lg:shadow-none

          ${
            isMobileOpen
              ? "translate-x-0"
              : "-translate-x-full"
          }
        `}
      >
        {/* =================================================
            LOGO
        ================================================== */}

        <div className="border-b border-white/10 px-6 py-7">
          <div className="flex items-start justify-between">
            <Link
              href="/dashboard"
              className="block"
              onClick={() =>
                setIsMobileOpen(false)
              }
            >
              <h1 className="text-3xl font-extrabold tracking-tight text-blue-400 sm:text-4xl">
                FinPilot AI
              </h1>

              <p className="mt-2 text-sm text-slate-400">
                Financial Research Platform
              </p>
            </Link>

            {/* Mobile close button */}
            <button
              type="button"
              aria-label="Close sidebar"
              onClick={() =>
                setIsMobileOpen(false)
              }
              className="
                flex
                h-9
                w-9
                shrink-0
                items-center
                justify-center
                rounded-lg
                text-slate-400
                transition
                hover:bg-white/10
                hover:text-white
                lg:hidden
              "
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* =================================================
            NAVIGATION
        ================================================== */}

        <nav className="flex-1 space-y-2 overflow-y-auto px-4 py-7">
          {menuItems.map((item) => {
            const Icon = item.icon;

            const active =
              pathname === item.href ||
              (item.href !== "/dashboard" &&
                pathname.startsWith(
                  `${item.href}/`
                ));

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() =>
                  setIsMobileOpen(false)
                }
                className={`
                  group
                  flex
                  items-center
                  justify-between
                  rounded-2xl
                  px-5
                  py-4
                  transition

                  ${
                    active
                      ? "border border-blue-500/40 bg-blue-600/20 text-blue-400"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }
                `}
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

        {/* =================================================
            USER PROFILE
        ================================================== */}

        <div className="border-t border-white/10 p-5">
          <Link
            href="/settings"
            onClick={() =>
              setIsMobileOpen(false)
            }
            className="
              block
              rounded-2xl
              border
              border-white/10
              bg-white/5
              p-5
              transition
              hover:border-blue-500/30
              hover:bg-white/10
            "
          >
            <div className="flex items-center gap-4">
              {/* Avatar */}

              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-600 text-lg font-bold text-white sm:h-14 sm:w-14 sm:text-xl">
                {firstLetter}
              </div>

              {/* User information */}

              <div className="min-w-0">
                <p className="truncate text-base font-bold text-white sm:text-lg">
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
    </>
  );
}