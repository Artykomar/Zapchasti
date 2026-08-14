import { redirect } from "next/navigation";
import { buildDjangoApiUrl } from "@/src/server/django/client";

export const dynamic = "force-dynamic";

export default function DjangoAdminRedirectPage() {
  redirect(buildDjangoApiUrl("/admin/"));
}
