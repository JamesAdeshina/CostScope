"use client";

import {
  useRef,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";


interface WorkflowRun {
  id: number;
  status: string;
  conclusion: string | null;
  created_at: string;
  updated_at: string;
  html_url: string;
}


export function AdminDashboard() {
  const router =
    useRouter();

  const [
    run,
    setRun,
  ] = useState<WorkflowRun | null>(
    null,
  );

  const [
    runUrl,
    setRunUrl,
  ] = useState<string | null>(
    null,
  );

  const [
    message,
    setMessage,
  ] = useState<string | null>(
    null,
  );

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  const [
    dispatching,
    setDispatching,
  ] = useState(false);

  const intervalRef =
    useRef<ReturnType<
      typeof setInterval
    > | null>(null);


  function stopPolling() {
    if (
      intervalRef.current
    ) {
      clearInterval(
        intervalRef.current,
      );

      intervalRef.current =
        null;
    }
  }


  async function loadStatus(
    runId: number,
  ) {
    const response =
      await fetch(
        `/api/admin/status?run_id=${runId}`,
        {
          cache: "no-store",
        },
      );

    if (!response.ok) {
      return;
    }

    const body =
      (await response.json()) as {
        run: WorkflowRun;
      };

    setRun(body.run);

    if (
      body.run.status ===
      "completed"
    ) {
      stopPolling();

      if (
        body.run.conclusion ===
        "success"
      ) {
        setMessage(
          "CostScope data refresh completed successfully.",
        );
      } else {
        setMessage(null);

        setError(
          `Refresh finished with status: ${
            body.run.conclusion ??
            "unknown"
          }.`,
        );
      }
    } else {
      setMessage(
        `Refresh is ${body.run.status}.`,
      );
    }
  }


  async function
  handleRefresh() {
    const confirmed =
      window.confirm(
        "Refresh all CostScope datasets? This will rebuild the warehouse and update the live database.",
      );

    if (!confirmed) {
      return;
    }

    stopPolling();

    setDispatching(true);
    setError(null);
    setMessage(null);
    setRun(null);
    setRunUrl(null);

    try {
      const response =
        await fetch(
          "/api/admin/refresh",
          {
            method: "POST",
          },
        );

      const body =
        await response
          .json()
          .catch(() => ({
            detail:
              "Invalid response from refresh endpoint.",
          }));

      if (!response.ok) {
        throw new Error(
          body.detail ??
            "Unable to start refresh.",
        );
      }

      const runId =
        Number(
          body.run_id,
        );

      setRunUrl(
        body.html_url,
      );

      setMessage(
        "Refresh requested. GitHub Actions is starting...",
      );

      await loadStatus(
        runId,
      );

      intervalRef.current =
        setInterval(
          () => {
            void loadStatus(
              runId,
            );
          },
          5000,
        );
    } catch (refreshError) {
      setError(
        refreshError instanceof Error
          ? refreshError.message
          : "Unable to start refresh.",
      );
    } finally {
      setDispatching(false);
    }
  }


  async function
  handleLogout() {
    stopPolling();

    await fetch(
      "/api/admin/logout",
      {
        method: "POST",
      },
    );

    router.refresh();
  }


  const refreshRunning =
    run !== null &&
    run.status !== "completed";


  return (
    <div className="mt-8 space-y-6">
      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-xl font-semibold text-zinc-950">
              Data warehouse
            </h2>

            <p className="mt-1 text-sm text-zinc-500">
              Trigger the complete CostScope ETL pipeline and PostgreSQL refresh.
            </p>
          </div>

          <button
            type="button"
            onClick={
              handleLogout
            }
            className="text-sm font-medium text-zinc-500 hover:text-zinc-950"
          >
            Sign out
          </button>
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={
              handleRefresh
            }
            disabled={
              dispatching ||
              refreshRunning
            }
            className="min-h-12 rounded-xl bg-zinc-950 px-6 font-medium text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {dispatching
              ? "Requesting refresh..."
              : refreshRunning
                ? "Refresh running..."
                : "Refresh CostScope Data"}
          </button>

          {runUrl && (
            <a
              href={runUrl}
              target="_blank"
              rel="noreferrer"
              className="text-sm font-medium text-zinc-600 underline underline-offset-4"
            >
              View GitHub run
            </a>
          )}
        </div>

        {message && (
          <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
            {message}
          </div>
        )}

        {error && (
          <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        <dl className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl bg-zinc-50 p-4">
            <dt className="text-xs uppercase tracking-wide text-zinc-500">
              Workflow status
            </dt>

            <dd className="mt-2 font-medium text-zinc-950">
              {run?.status ??
                "idle"}
            </dd>
          </div>

          <div className="rounded-xl bg-zinc-50 p-4">
            <dt className="text-xs uppercase tracking-wide text-zinc-500">
              Result
            </dt>

            <dd className="mt-2 font-medium text-zinc-950">
              {run?.conclusion ??
                "—"}
            </dd>
          </div>
        </dl>
      </section>
    </div>
  );
}
