import { NextResponse } from "next/server";
import { fetchDjangoRaw } from "@/src/server/django/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const backend = await fetchDjangoRaw("/api/health/");
    if (!backend.ok) {
      return NextResponse.json(
        { status: "unavailable", frontend: "ok", backend: "unavailable" },
        { status: 503 }
      );
    }
    return NextResponse.json({ status: "ok", frontend: "ok", backend: "ok" });
  } catch {
    return NextResponse.json(
      { status: "unavailable", frontend: "ok", backend: "unavailable" },
      { status: 503 }
    );
  }
}
