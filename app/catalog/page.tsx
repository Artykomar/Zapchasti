import CatalogExplorer from "@/src/components/CatalogExplorer";
import { brands, categories, parts } from "@/src/data/catalog";

type CatalogPageProps = {
  searchParams?: Promise<{
    q?: string;
    brand?: string;
    category?: string;
  }>;
};

export default async function CatalogPage({ searchParams }: CatalogPageProps) {
  const params = (await searchParams) ?? {};
  const requestedBrand = params.brand ?? "all";
  const initialBrand =
    brands.find((brand) => brand.slug === requestedBrand || brand.name === requestedBrand)?.slug ?? "all";
  const requestedCategory = params.category ?? "all";
  const initialCategory =
    categories.find((category) => category.slug === requestedCategory || category.name === requestedCategory)?.slug ??
    "all";

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Каталог Zemazap</p>
        <h1>Автозапчасти по маркам, категориям и артикулам</h1>
        <p>
          Витрина показывает рабочую структуру магазина: фильтры, поиск, карточки товаров,
          избранное и добавление в корзину-заявку. Данные пока моковые и готовы к переносу в API.
        </p>
      </section>

      <CatalogExplorer
        parts={parts}
        brands={brands}
        categories={categories}
        initialQuery={params.q ?? ""}
        initialBrand={initialBrand}
        initialCategory={initialCategory}
      />
    </main>
  );
}
