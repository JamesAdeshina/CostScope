import {
  createHmac,
  timingSafeEqual,
} from "node:crypto";

import {
  cookies,
} from "next/headers";


const COOKIE_NAME = "costscope_admin_session";

const SESSION_DURATION_SECONDS =
  60 * 60 * 8;


function getSessionSecret(): string {
  const secret =
    process.env.COSTSCOPE_ADMIN_SESSION_SECRET;

  if (!secret) {
    throw new Error(
      "COSTSCOPE_ADMIN_SESSION_SECRET is not configured.",
    );
  }

  return secret;
}


function sign(value: string): string {
  return createHmac(
    "sha256",
    getSessionSecret(),
  )
    .update(value)
    .digest("hex");
}


function safeEqual(
  left: string,
  right: string,
): boolean {
  const leftBuffer =
    Buffer.from(left);

  const rightBuffer =
    Buffer.from(right);

  if (
    leftBuffer.length !==
    rightBuffer.length
  ) {
    return false;
  }

  return timingSafeEqual(
    leftBuffer,
    rightBuffer,
  );
}


function createSessionValue(): string {
  const expiresAt =
    Math.floor(Date.now() / 1000) +
    SESSION_DURATION_SECONDS;

  const payload =
    String(expiresAt);

  const signature =
    sign(payload);

  return `${payload}.${signature}`;
}


function verifySessionValue(
  value: string,
): boolean {
  const [
    expiresAtRaw,
    signature,
  ] = value.split(".");

  if (
    !expiresAtRaw ||
    !signature
  ) {
    return false;
  }

  const expectedSignature =
    sign(expiresAtRaw);

  if (
    !safeEqual(
      signature,
      expectedSignature,
    )
  ) {
    return false;
  }

  const expiresAt =
    Number(expiresAtRaw);

  if (
    !Number.isFinite(expiresAt)
  ) {
    return false;
  }

  return (
    expiresAt >
    Math.floor(Date.now() / 1000)
  );
}


export async function
createAdminSession(): Promise<void> {
  const cookieStore =
    await cookies();

  cookieStore.set(
    COOKIE_NAME,
    createSessionValue(),
    {
      httpOnly: true,
      secure:
        process.env.NODE_ENV ===
        "production",
      sameSite: "strict",
      path: "/",
      maxAge:
        SESSION_DURATION_SECONDS,
    },
  );
}


export async function
clearAdminSession(): Promise<void> {
  const cookieStore =
    await cookies();

  cookieStore.delete(
    COOKIE_NAME,
  );
}


export async function
isAdminAuthenticated(): Promise<boolean> {
  const cookieStore =
    await cookies();

  const value =
    cookieStore.get(
      COOKIE_NAME,
    )?.value;

  if (!value) {
    return false;
  }

  return verifySessionValue(
    value,
  );
}


export function
validateAdminPassword(
  password: string,
): boolean {
  const expectedPassword =
    process.env.COSTSCOPE_ADMIN_PASSWORD;

  if (!expectedPassword) {
    throw new Error(
      "COSTSCOPE_ADMIN_PASSWORD is not configured.",
    );
  }

  return safeEqual(
    password,
    expectedPassword,
  );
}
