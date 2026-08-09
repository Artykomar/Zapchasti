import { NextResponse } from "next/server";
import { fetchDjangoRaw } from "@/src/server/django/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const jsonHeaders = {
  "Content-Type": "application/json; charset=utf-8"
};

export async function POST(request: Request) {
  try {
    const upstream = await fetchDjangoRaw("/api/requests/", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": request.headers.get("content-type") ?? "application/json",
        "X-Forwarded-For": request.headers.get("x-forwarded-for") ?? "",
        "X-Real-IP": request.headers.get("x-real-ip") ?? ""
      },
      body: await request.text()
    });

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
