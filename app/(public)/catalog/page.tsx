import CatalogExplorer from "@/src/components/CatalogExplorer";
import { getCatalogSnapshot } from "@/src/server/db/catalog";

export const dynamic = "force-dynamic";

type CatalogPageProps = {
  searchParams?: Promise<{
    q?: string;
    brand?: string;
    category?: string;
  }>;
};

export default async function CatalogPage({ searchParams }: CatalogPageProps) {
  const params = (await searchParams) ?? {};
  const baseCatalog = getCatalogSnapshot();
  const requestedBrand = params.brand ?? "all";
  const initialBrand =
    baseCatalog.brands.find((brand) => brand.slug === requestedBrand || brand.name === requestedBrand)?.slug ??
    "all";
  const requestedCategory = params.category ?? "all";
  const initialCategory =
    baseCatalog.categories.find(
      (category) => category.slug === requestedCategory || category.name === requestedCategory
    )?.slug ?? "all";
  const catalog = getCatalogSnapshot({
    query: params.q,
    brandSlug: initialBrand === "all" ? undefined : initialBrand,
    categorySlug: initialCategory === "all" ? undefined : initialCategory
  });

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Каталог Zemazap</p>
        <h1>Автозапчасти по маркам, категориям и артикулам</h1>
        <p>
          Витрина показывает рабочую структуру магазина: фильтры, поиск, карточки товаров,
          избранное и добавление в корзину-заявку. Данные уже читаются через серверный API и стартовую SQLite-базу.
        </p>
      </section>

      <CatalogExplorer
        parts={catalog.parts}
        brands={baseCatalog.brands}
        categories={baseCatalog.categories}
        initialQuery={params.q ?? ""}
        initialBrand={initialBrand}
        initialCategory={initialCategory}
      />
    </main>
  );
}
