import CatalogExplorer from "@/src/components/CatalogExplorer";
import { getCatalogSnapshot } from "@/src/server/django/catalog";

export const dynamic = "force-dynamic";

type CatalogPageProps = {
  searchParams?: Promise<{
    q?: string;
    brand?: string;
    category?: string;
    condition?: string;
  }>;
};

export default async function CatalogPage({ searchParams }: CatalogPageProps) {
  const params = (await searchParams) ?? {};
  const baseCatalog = await getCatalogSnapshot({ limit: 1 });
  const requestedBrand = params.brand ?? "all";
  const initialBrand =
    baseCatalog.brands.find((brand) => brand.slug === requestedBrand || brand.name === requestedBrand)?.slug ??
    "all";
  const requestedCategory = params.category ?? "all";
  const initialCategory =
    baseCatalog.categories.find(
      (category) => category.slug === requestedCategory || category.name === requestedCategory
    )?.slug ?? "all";
  const initialCondition = params.condition ?? "all";
  const catalog = await getCatalogSnapshot({
    query: params.q,
    brandSlug: initialBrand === "all" ? undefined : initialBrand,
    categorySlug: initialCategory === "all" ? undefined : initialCategory,
    condition: initialCondition === "all" ? undefined : initialCondition
  });

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Каталог Zemazap</p>
        <h1>Автозапчасти по маркам, категориям и артикулам</h1>
        <p>
          Витрина показывает рабочую структуру магазина: фильтры, поиск, карточки товаров,
          избранное и добавление в корзину-заявку. Данные читаются через основной Django API.
        </p>
      </section>

      <CatalogExplorer
        parts={catalog.parts}
        brands={baseCatalog.brands}
        categories={baseCatalog.categories}
        initialQuery={params.q ?? ""}
        initialBrand={initialBrand}
        initialCategory={initialCategory}
        initialCondition={initialCondition}
      />
    </main>
  );
}
