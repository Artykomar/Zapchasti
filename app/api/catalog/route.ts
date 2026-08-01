import { NextResponse } from "next/server";
import { getCatalogSnapshot } from "@/src/server/db/catalog";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const jsonHeaders = {
  "Content-Type": "application/json; charset=utf-8"
};

const cleanFilter = (value: string | null) => {
  const trimmed = value?.trim();
  return trimmed && trimmed !== "all" ? trimmed : undefined;
};

export function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limit = Number(searchParams.get("limit") ?? 100);
  const catalog = getCatalogSnapshot({
    query: cleanFilter(searchParams.get("q")),
    brandSlug: cleanFilter(searchParams.get("brand")),
    categorySlug: cleanFilter(searchParams.get("category")),
    condition: cleanFilter(searchParams.get("condition")),
    limit: Number.isFinite(limit) ? limit : 100
  });

  return NextResponse.json(
    {
      ...catalog,
      meta: {
        database: "sqlite-development",
        productionTarget: "postgresql"
      }
    },
    { headers: jsonHeaders }
  );
}
