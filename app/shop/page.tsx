import CatalogExplorer from "@/src/components/CatalogExplorer";
import { brands, categories, parts } from "@/src/data/catalog";

export default function ShopPage() {
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

      <CatalogExplorer parts={parts} brands={brands} categories={categories} />
    </main>
  );
}
