import { createHmac, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const ADMIN_COOKIE = "zemazap-admin-session";
const SESSION_TTL_MS = 12 * 60 * 60 * 1000;
const LOCAL_DEV_PASSWORD = "zemazap-local-admin";

const getAdminPassword = () => {
  const configured = process.env.ZEMAZAP_ADMIN_PASSWORD?.trim();

  if (configured) {
    return configured;
  }

  return process.env.NODE_ENV === "production" ? "" : LOCAL_DEV_PASSWORD;
};

const getSessionSecret = () =>
  process.env.ZEMAZAP_ADMIN_SESSION_SECRET?.trim() || getAdminPassword();

const sign = (value: string) =>
  createHmac("sha256", getSessionSecret()).update(value).digest("hex");

const safeEqual = (left: string, right: string) => {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);

  return leftBuffer.length === rightBuffer.length && timingSafeEqual(leftBuffer, rightBuffer);
};

export const verifyAdminPassword = (password: string) => {
  const configuredPassword = getAdminPassword();

  return Boolean(configuredPassword) && safeEqual(password, configuredPassword);
};

export const isAdminConfigured = () => Boolean(getAdminPassword());

export const createAdminSession = async () => {
  const expiresAt = Date.now() + SESSION_TTL_MS;
  const payload = String(expiresAt);
  const cookieStore = await cookies();

  cookieStore.set(ADMIN_COOKIE, `${payload}.${sign(payload)}`, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/admin",
    maxAge: Math.floor(SESSION_TTL_MS / 1000)
  });
};

export const clearAdminSession = async () => {
  const cookieStore = await cookies();
  cookieStore.delete(ADMIN_COOKIE);
};

export const hasAdminSession = async () => {
  const cookieStore = await cookies();
  const session = cookieStore.get(ADMIN_COOKIE)?.value;

  if (!session) {
    return false;
  }

  const [expiresAt, signature] = session.split(".");

  if (!expiresAt || !signature || !safeEqual(sign(expiresAt), signature)) {
    return false;
  }

  return Number(expiresAt) > Date.now();
};

export const requireAdminSession = async () => {
  if (!(await hasAdminSession())) {
    redirect("/admin/login");
  }
};

export const localDevelopmentAdminPassword = LOCAL_DEV_PASSWORD;
