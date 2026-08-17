"use client";

import {
  FormEvent,
  useState,
} from "react";

import { useRouter } from "next/navigation";

export default function SignUpPage() {
  const router = useRouter();

  // ============================================================
  // FORM STATE
  // ============================================================

  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  // ============================================================
  // SIGN UP
  // ============================================================

  async function handleSubmit(
    e: FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    const cleanName =
      name.trim();

    const cleanEmail =
      email.trim();

    // Basic validation
    if (!cleanName) {
      setError(
        "Please enter your name."
      );
      setLoading(false);
      return;
    }

    if (!cleanEmail) {
      setError(
        "Please enter your email."
      );
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError(
        "Password must be at least 6 characters."
      );
      setLoading(false);
      return;
    }

    try {
      // ========================================================
      // CREATE ACCOUNT
      // ========================================================

      const response =
        await fetch(
          "https://finpilot-ai-q4nk.onrender.com/users/signup",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              name: cleanName,
              email: cleanEmail,
              password,
            }),
          }
        );

      const data =
        await response.json();

      // ========================================================
      // HANDLE ERROR
      // ========================================================

      if (!response.ok) {
        throw new Error(
          data?.error ||
            data?.message ||
            "Signup failed"
        );
      }

      // ========================================================
      // SAVE USER INFORMATION
      // ========================================================
      //
      // The dashboard will read user_name
      // and display:
      //
      // Good Morning, Akshat
      // Good Afternoon, Akshat
      // Good Evening, Akshat
      // Good Night, Akshat
      //
      // ========================================================

      localStorage.setItem(
        "user_name",
        cleanName
      );

      localStorage.setItem(
        "user_email",
        cleanEmail
      );

      // ========================================================
      // SUCCESS
      // ========================================================

      setSuccess(
        "Account created successfully! Redirecting to login..."
      );

      // ========================================================
      // REDIRECT TO LOGIN
      // ========================================================

      setTimeout(() => {
        router.push(
          "/login"
        );
      }, 1500);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // UI
  // ============================================================

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#050b24] px-4">

      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-[#101832] p-8 shadow-2xl">

        {/* =====================================================
            HEADER
        ====================================================== */}

        <div className="mb-8 text-center">

          <h1 className="text-3xl font-bold text-white">
            Create your FinPilot account
          </h1>

          <p className="mt-2 text-gray-400">
            Start your AI-powered financial journey
          </p>

        </div>

        {/* =====================================================
            FORM
        ====================================================== */}

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >

          {/* ===================================================
              NAME
          ==================================================== */}

          <div>

            <label
              htmlFor="name"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Name
            </label>

            <input
              id="name"
              name="name"
              type="text"
              value={name}
              onChange={(e) =>
                setName(
                  e.target.value
                )
              }
              placeholder="Enter your name"
              autoComplete="name"
              required
              disabled={loading}
              className="w-full rounded-lg border border-white/10 bg-[#080f29] px-4 py-3 text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            />

          </div>

          {/* ===================================================
              EMAIL
          ==================================================== */}

          <div>

            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Email
            </label>

            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(e) =>
                setEmail(
                  e.target.value
                )
              }
              placeholder="you@example.com"
              autoComplete="email"
              required
              disabled={loading}
              className="w-full rounded-lg border border-white/10 bg-[#080f29] px-4 py-3 text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            />

          </div>

          {/* ===================================================
              PASSWORD
          ==================================================== */}

          <div>

            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Password
            </label>

            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(
                  e.target.value
                )
              }
              placeholder="Create a password"
              autoComplete="new-password"
              required
              minLength={6}
              disabled={loading}
              className="w-full rounded-lg border border-white/10 bg-[#080f29] px-4 py-3 text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            />

            <p className="mt-2 text-xs text-gray-500">
              Password must be at least 6 characters.
            </p>

          </div>

          {/* ===================================================
              ERROR
          ==================================================== */}

          {error && (
            <div
              role="alert"
              className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400"
            >
              {error}
            </div>
          )}

          {/* ===================================================
              SUCCESS
          ==================================================== */}

          {success && (
            <div
              role="status"
              className="rounded-lg border border-green-500/30 bg-green-500/10 p-3 text-sm text-green-400"
            >
              {success}
            </div>
          )}

          {/* ===================================================
              SUBMIT
          ==================================================== */}

          <button
            type="submit"
            disabled={
              loading ||
              !name.trim() ||
              !email.trim() ||
              !password
            }
            className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading
              ? "Creating account..."
              : "Create Account"}
          </button>

        </form>

        {/* =====================================================
            LOGIN LINK
        ====================================================== */}

        <p className="mt-6 text-center text-sm text-gray-400">

          Already have an account?{" "}

          <button
            type="button"
            onClick={() =>
              router.push(
                "/login"
              )
            }
            disabled={loading}
            className="font-semibold text-blue-400 transition hover:text-blue-300 disabled:opacity-50"
          >
            Login
          </button>

        </p>

      </div>

    </main>
  );
}