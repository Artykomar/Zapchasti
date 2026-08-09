import HomePageClient from "@/src/components/HomePageClient";
import { getCatalogSnapshot } from "@/src/server/django/catalog";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const catalog = await getCatalogSnapshot({ limit: 12 });

  return (
    <HomePageClient
      brands={catalog.brands}
      categories={catalog.categories}
      parts={catalog.parts}
    />
  );
}
