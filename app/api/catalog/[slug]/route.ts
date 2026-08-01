import { NextResponse } from "next/server";
import { getPartBySlug } from "@/src/server/db/catalog";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const jsonHeaders = {
  "Content-Type": "application/json; charset=utf-8"
};

type CatalogPartRouteProps = {
  params: Promise<{
    slug: string;
  }>;
};

export async function GET(_request: Request, { params }: CatalogPartRouteProps) {
  const { slug } = await params;
  const part = getPartBySlug(slug);

  if (!part) {
    return NextResponse.json({ error: "Товар не найден" }, { status: 404, headers: jsonHeaders });
  }

  return NextResponse.json({ part }, { headers: jsonHeaders });
}
