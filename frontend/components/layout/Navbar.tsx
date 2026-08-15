import Link from "next/link";
export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        {/* Logo */}
        <Link
          href="/"
          className="text-2xl font-bold tracking-tight text-blue-500 transition duration-300 hover:text-blue-400"
        >
          📈 FinPilot AI
        </Link>

        {/* Navigation Links */}
        <ul className="hidden items-center gap-8 text-slate-300 md:flex">
          <li>
            <Link href="/" className="transition duration-300 hover:text-white">
              Home
            </Link>
          </li>

          <li>
            <Link
              href="/#features"
              className="transition duration-300 hover:text-white"
            >
              Features
            </Link>
          </li>

          <li>
            <Link
              href="/pricing"
              className="transition duration-300 hover:text-white"
            >
              Pricing
            </Link>
          </li>

          <li>
            <Link
              href="/about"
              className="transition duration-300 hover:text-white"
            >
              About
            </Link>
          </li>

          <li>
            <Link
              href="/contact"
              className="transition duration-300 hover:text-white"
            >
              Contact
            </Link>
          </li>
        </ul>

        {/* Right Buttons */}
        <div className="flex items-center gap-3">
         <div className="flex items-center gap-4">
  <button className="rounded-xl border border-white/20 px-5 py-2 text-white hover:bg-white/10 transition">
    Login
  </button>

  <button className="rounded-xl bg-blue-600 px-5 py-2 text-white hover:bg-blue-500 transition">
    Get Started
  </button>
</div>
        </div>
      </div>
    </nav>
  );
}