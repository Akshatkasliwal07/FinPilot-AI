"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { loginUser } from "@/services/auth-service";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const cleanEmail = email.trim();

      /*
       * LOGIN
       */
      const result = await loginUser({
        email: cleanEmail,
        password,
      });

      /*
       * SAVE AUTH
       */
      localStorage.setItem(
        "access_token",
        result.access_token
      );

      localStorage.setItem(
        "token_type",
        result.token_type || "bearer"
      );

      /*
       * =====================================================
       * GET CURRENT USER
       * =====================================================
       *
       * Login response currently contains the token,
       * so we use that token to get the actual logged-in
       * user's name from the backend.
       */

      try {
        const userResponse = await fetch(
          `${API_BASE_URL}/users/me`,
          {
            method: "GET",
            cache: "no-store",
            headers: {
              Authorization: `${
                result.token_type || "bearer"
              } ${result.access_token}`,
              "Content-Type":
                "application/json",
            },
          }
        );

        if (userResponse.ok) {
          const userResult =
            await userResponse.json();

          /*
           * Support both:
           *
           * { name: "Rahul" }
           *
           * and
           *
           * { data: { name: "Rahul" } }
           */

          const user =
            userResult?.data ??
            userResult;

          const name =
            user?.name ??
            user?.full_name ??
            user?.username ??
            "";

          if (
            typeof name === "string" &&
            name.trim()
          ) {
            localStorage.setItem(
              "user_name",
              name.trim()
            );
          }

          if (
            typeof user?.email === "string" &&
            user.email.trim()
          ) {
            localStorage.setItem(
              "user_email",
              user.email.trim()
            );
          }
        }
      } catch (userError) {
        /*
         * Do not fail login if fetching the profile
         * fails. The authentication itself succeeded.
         */
        console.warn(
          "Unable to load user profile:",
          userError
        );
      }

      /*
       * Clear any old hardcoded/previous account name
       * only if the current login did not provide one.
       */
      if (!localStorage.getItem("user_name")) {
        localStorage.setItem(
          "user_name",
          cleanEmail.split("@")[0]
        );
      }

      /*
       * GO TO DASHBOARD
       */
      router.push("/dashboard");
      router.refresh();

    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Login failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 shadow-xl backdrop-blur-xl"
      >

        {/* HEADER */}

        <div>
          <p className="text-sm font-medium text-blue-400">
            FinPilot
          </p>

          <h1 className="mt-2 text-3xl font-bold">
            Login to your account
          </h1>

          <p className="mt-2 text-slate-400">
            Enter your registered email and password.
          </p>
        </div>

        {/* FORM */}

        <div className="mt-8 space-y-5">

          {/* EMAIL */}

          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Email
            </label>

            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="you@example.com"
              required
              disabled={loading}
              className="w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>

          {/* PASSWORD */}

          <div>
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Password
            </label>

            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter your password"
              required
              disabled={loading}
              className="w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>

        </div>

        {/* ERROR */}

        {error && (
          <div
            role="alert"
            className="mt-5 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300"
          >
            {error}
          </div>
        )}

        {/* BUTTON */}

        <button
          type="submit"
          disabled={
            loading ||
            !email.trim() ||
            !password
          }
          className="mt-6 w-full rounded-xl bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading
            ? "Signing in..."
            : "Login"}
        </button>

        {/* SIGN UP */}

        <p className="mt-6 text-center text-sm text-slate-400">
          Don't have an account?{" "}

          <button
            type="button"
            onClick={() =>
              router.push("/sign-up")
            }
            className="font-semibold text-blue-400 hover:text-blue-300"
          >
            Create Account
          </button>
        </p>

      </form>

    </main>
  );
}