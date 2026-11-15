import {
  NextResponse,
} from "next/server";

import {
  dispatchRefreshWorkflow,
} from "@/lib/admin/github";

import {
  isAdminAuthenticated,
} from "@/lib/admin/session";


export async function POST() {
  if (
    !(await isAdminAuthenticated())
  ) {
    return NextResponse.json(
      {
        detail: "Unauthorized.",
      },
      {
        status: 401,
      },
    );
  }

  try {
    const run =
      await dispatchRefreshWorkflow();

    return NextResponse.json({
      status: "requested",
      run_id:
        run.workflow_run_id,
      html_url:
        run.html_url,
      requested_at:
        new Date().toISOString(),
    });
  } catch (error) {
    console.error(
      "CostScope refresh dispatch failed:",
      error,
    );

    return NextResponse.json(
      {
        detail:
          "Unable to start the refresh workflow.",
      },
      {
        status: 502,
      },
    );
  }
}
