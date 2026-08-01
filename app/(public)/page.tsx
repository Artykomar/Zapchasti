import HomePageClient from "@/src/components/HomePageClient";
import { getCatalogSnapshot } from "@/src/server/db/catalog";

export const dynamic = "force-dynamic";

export default function HomePage() {
  const catalog = getCatalogSnapshot({ limit: 12 });

  return (
    <HomePageClient
      brands={catalog.brands}
      categories={catalog.categories}
      parts={catalog.parts}
    />
  );
}
