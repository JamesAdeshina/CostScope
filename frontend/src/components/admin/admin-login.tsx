"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";


export function AdminLogin() {
  const router =
    useRouter();

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  const [
    loading,
    setLoading,
  ] = useState(false);


  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLoading(true);
    setError(null);

    try {
      const response =
        await fetch(
          "/api/admin/login",
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              password,
            }),
          },
        );

      const body =
        await response.json();

      if (!response.ok) {
        throw new Error(
          body.detail ??
            "Login failed.",
        );
      }

      setPassword("");

      router.refresh();
    } catch (loginError) {
      setError(
        loginError instanceof Error
          ? loginError.message
          : "Login failed.",
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <form
      onSubmit={handleSubmit}
      className="mt-8 max-w-md rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm"
    >
      <label
        htmlFor="admin-password"
        className="text-sm font-medium text-zinc-700"
      >
        Admin password
      </label>

      <input
        id="admin-password"
        type="password"
        value={password}
        onChange={(event) =>
          setPassword(
            event.target.value,
          )
        }
        autoComplete="current-password"
        required
        className="mt-2 min-h-12 w-full rounded-xl border border-zinc-300 px-4 text-zinc-950 outline-none focus:border-zinc-900"
      />

      {error && (
        <p className="mt-3 text-sm text-red-600">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="mt-4 min-h-12 w-full rounded-xl bg-zinc-950 px-5 font-medium text-white hover:bg-zinc-800 disabled:opacity-60"
      >
        {loading
          ? "Signing in..."
          : "Sign in"}
      </button>
    </form>
  );
}
