import { NextResponse } from "next/server";
import { fetchDjangoRaw } from "@/src/server/django/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const jsonHeaders = {
  "Content-Type": "application/json; charset=utf-8"
};

export async function GET() {
  try {
    const upstream = await fetchDjangoRaw("/api/site-settings/");

    return new NextResponse(await upstream.text(), {
      status: upstream.status,
      headers: jsonHeaders
    });
  } catch {
    return NextResponse.json(
      { error: "Django API is unavailable" },
      { status: 502, headers: jsonHeaders }
    );
  }
}
