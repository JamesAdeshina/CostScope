import {
  NextResponse,
} from "next/server";

import {
  createAdminSession,
  validateAdminPassword,
} from "@/lib/admin/session";


export async function POST(
  request: Request,
) {
  const body =
    (await request.json()) as {
      password?: string;
    };

  if (
    !body.password ||
    !validateAdminPassword(
      body.password,
    )
  ) {
    return NextResponse.json(
      {
        detail:
          "Invalid admin password.",
      },
      {
        status: 401,
      },
    );
  }

  await createAdminSession();

  return NextResponse.json({
    authenticated: true,
  });
}
