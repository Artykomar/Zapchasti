import Link from "next/link";
import { ArrowRight, Filter, PackageCheck, Search } from "lucide-react";
import { brands, categories, formatPrice, parts } from "@/src/data/catalog";

export default function CatalogPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Каталог Zemazap</p>
        <h1>Автозапчасти, категории и тестовые товары Zemazap</h1>
        <p>
          Здесь будет основной каталог с URL по маркам, моделям и категориям. Пока страница работает как
          витрина структуры и первых тестовых позиций.
        </p>
      </section>

      <section className="catalog-tools" aria-label="Инструменты каталога">
        <label>
          <Search size={18} aria-hidden="true" />
          <input placeholder="Поиск по OEM, артикулу или названию" />
        </label>
        <button type="button">
          <Filter size={18} aria-hidden="true" />
          Фильтры
        </button>
      </section>

      <section className="catalog-layout">
        <aside className="catalog-sidebar">
          <h2>Марки</h2>
          {brands.map((brand) => (
            <div key={brand.name} className="sidebar-group">
              <strong>{brand.name}</strong>
              {brand.models.map((model) => (
                <span key={model.name}>
                  {model.name}, {model.years}
                </span>
              ))}
            </div>
          ))}

          <h2 id="tires">Категории</h2>
          {categories.map((category) => (
            <a key={category.name} href={`#${category.name}`}>
              {category.name}
            </a>
          ))}
        </aside>

        <div className="catalog-products">
          {parts.map((part) => (
            <article key={part.id} className="wide-product">
              <div className="wide-product__visual">
                <PackageCheck size={42} aria-hidden="true" />
                <span>{part.quality}</span>
              </div>
              <div className="wide-product__content">
                <span className="tag">{part.category}</span>
                <h2>{part.name}</h2>
                <p>{part.delivery}</p>
                <div className="spec-list">
                  <span>OEM: {part.oem}</span>
                  <span>Артикул: {part.article}</span>
                  <span>Производитель: {part.manufacturer}</span>
                  <span>Применимость: {part.compatibility.join(", ")}</span>
                </div>
              </div>
              <div className="wide-product__action">
                <strong>{formatPrice(part.price)}</strong>
                <span>{part.availability}</span>
                <Link href="/request">
                  В заявку
                  <ArrowRight size={17} aria-hidden="true" />
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
