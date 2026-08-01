import CatalogExplorer from "@/src/components/CatalogExplorer";
import { getCatalogSnapshot } from "@/src/server/db/catalog";

export const dynamic = "force-dynamic";

export default function ShopPage() {
  const catalog = getCatalogSnapshot();

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Магазин Zemazap</p>
        <h1>Каталог товаров в формате интернет-магазина</h1>
        <p>
          Эта страница оставлена как привычный маршрут магазина. Она ведет к тем же товарам,
          фильтрам, корзине и избранному, что и основной каталог.
        </p>
      </section>

      <CatalogExplorer parts={catalog.parts} brands={catalog.brands} categories={catalog.categories} />
    </main>
  );
}
