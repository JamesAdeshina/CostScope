import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  getRefreshRun,
} from "@/lib/admin/github";

import {
  isAdminAuthenticated,
} from "@/lib/admin/session";


export async function GET(
  request: NextRequest,
) {
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

  const runIdRaw =
    request.nextUrl.searchParams.get(
      "run_id",
    );

  const runId =
    Number(runIdRaw);

  if (
    !runIdRaw ||
    !Number.isInteger(runId) ||
    runId <= 0
  ) {
    return NextResponse.json(
      {
        detail:
          "A valid workflow run ID is required.",
      },
      {
        status: 400,
      },
    );
  }

  try {
    const run =
      await getRefreshRun(
        runId,
      );

    return NextResponse.json({
      run,
    });
  } catch (error) {
    console.error(
      "CostScope refresh status failed:",
      error,
    );

    return NextResponse.json(
      {
        detail:
          "Unable to retrieve workflow status.",
      },
      {
        status: 502,
      },
    );
  }
}
