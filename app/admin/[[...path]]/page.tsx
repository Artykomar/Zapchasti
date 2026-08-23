import { redirect } from "next/navigation";
import { buildDjangoPublicUrl } from "@/src/server/django/client";

export const dynamic = "force-dynamic";

export default function DjangoAdminRedirectPage() {
  redirect(buildDjangoPublicUrl("/admin/"));
}
