import { redirect } from "next/navigation";
import { buildDjangoPublicUrl } from "@/src/server/django/client";

export const dynamic = "force-dynamic";

export default async function DjangoAdminRedirectPage({
  params,
  searchParams,
}: {
  params: Promise<{ path?: string[] }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { path = [] } = await params;
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(await searchParams)) {
    for (const item of Array.isArray(value) ? value : value === undefined ? [] : [value]) {
      query.append(key, item);
    }
  }
  const suffix = path.length ? `${path.map(encodeURIComponent).join("/")}/` : "";
  redirect(buildDjangoPublicUrl(`/admin/${suffix}${query.size ? `?${query}` : ""}`));
}
