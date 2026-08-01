"use client";

import Link from "next/link";
import {
  ArrowRight,
  Car,
  ClipboardList,
  Cog,
  PackageSearch,
  Search,
  ShieldCheck,
  Truck
} from "lucide-react";
import ProductActions from "@/src/components/ProductActions";
import type { Brand, Category, Part } from "@/src/data/catalog";
import { formatPrice, getPartSearchText } from "@/src/data/catalog";
import { useMemo, useState } from "react";

type HomePageClientProps = {
  brands: Brand[];
  categories: Category[];
  parts: Part[];
};

const fallbackBrand: Brand = {
  name: "",
  slug: "",
  country: "",
  models: [{ name: "", slug: "", years: "", generations: [] }]
};

export default function HomePageClient({ brands, categories, parts }: HomePageClientProps) {
  const firstBrand = brands[0] ?? fallbackBrand;
  const firstModel = firstBrand.models[0] ?? fallbackBrand.models[0];
  const [query, setQuery] = useState("");
  const [brand, setBrand] = useState(firstBrand.name);
  const [model, setModel] = useState(firstModel.name);

  const selectedBrand = brands.find((item) => item.name === brand) ?? firstBrand;
  const selectedModel = selectedBrand.models.find((item) => item.name === model) ?? selectedBrand.models[0];
  const quickStats = [
    { label: "марок в MVP-каталоге", value: `${brands.length}` },
    { label: "товарных категорий", value: `${categories.length}` },
    { label: "формат заказа", value: "заявка" }
  ];

  const filteredParts = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    if (!normalizedQuery) {
      const byVehicle = parts.filter((part) => part.brand === brand && part.model === model);
      return byVehicle.length > 0 ? byVehicle : parts.slice(0, 8);
    }

    return parts.filter((part) => getPartSearchText(part).includes(normalizedQuery)).slice(0, 8);
  }, [brand, model, parts, query]);

  return (
    <main>
      <section className="hero hero--market">
        <div className="gear-backdrop" aria-hidden="true">
          <span className="gear gear--one" />
          <span className="gear gear--two" />
          <span className="gear gear--three" />
        </div>
        <div className="hero__overlay" />
        <div className="hero__content hero__content--market">
          <div className="hero__copy">
            <p className="eyebrow">Zemazap: мультибрендовая витрина автозапчастей</p>
            <h1>Поиск запчастей по номеру, марке, модели и категории</h1>
            <p>
              Структура магазина собрана под каталог, карточки товаров, корзину-заявку, избранное,
              доставку, отзывы и сервисные страницы. Заказы на старте подтверждает менеджер.
            </p>
            <div className="hero-actions">
              <Link href="/catalog">
                <Search size={18} aria-hidden="true" />
                Каталог
              </Link>
              <Link href="/cart">
                <PackageSearch size={18} aria-hidden="true" />
                Корзина
              </Link>
            </div>
          </div>

          <form className="parts-search" action="/catalog">
            <div className="parts-search__head">
              <Search size={22} aria-hidden="true" />
              <div>
                <h2>Найти запчасть</h2>
                <p>Введите номер, артикул или выберите автомобиль</p>
              </div>
            </div>

            <label className="parts-search__query" htmlFor="global-search">
              Номер детали, артикул или название
              <input
                id="global-search"
                name="q"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Например: ZP-LGT-5015L"
              />
            </label>

            <div className="parts-search__grid parts-search__grid--two">
              <label>
                Марка
                <select
                  name="brand"
                  value={brand}
                  onChange={(event) => {
                    const nextBrand = event.target.value;
                    const nextModels = brands.find((item) => item.name === nextBrand)?.models ?? [];
                    const nextModel = nextModels[0];
                    setBrand(nextBrand);
                    setModel(nextModel?.name ?? "");
                  }}
                >
                  {brands.map((item) => (
                    <option key={item.name}>{item.name}</option>
                  ))}
                </select>
              </label>

              <label>
                Модель
                <select name="model" value={model} onChange={(event) => setModel(event.target.value)}>
                  {selectedBrand.models.map((item) => (
                    <option key={item.name}>{item.name}</option>
                  ))}
                </select>
              </label>
            </div>

            <button type="submit" className="parts-search__submit">
              Перейти к результатам
              <ArrowRight size={18} aria-hidden="true" />
            </button>
          </form>
        </div>
      </section>

      <section className="quick-stats" aria-label="Ключевые особенности">
        {quickStats.map((item) => (
          <div key={item.label} className="quick-stat">
            <strong>{item.value}</strong>
            <span>{item.label}</span>
          </div>
        ))}
      </section>

      <section className="workspace">
        <div className="section-heading">
          <p className="eyebrow">Марки</p>
          <h2>Каталог не привязан к одной группе автомобилей</h2>
        </div>

        <div className="brand-cloud brand-cloud--large" aria-label="Популярные марки">
          {brands.map((item) => (
            <Link key={item.name} href={`/product-category/${item.slug}`}>
              {item.name}
              <span>{item.models.length} модели</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="workspace">
        <div className="section-heading">
          <p className="eyebrow">Подбор по автомобилю</p>
          <h2>Быстрый путь к совместимым деталям</h2>
        </div>

        <div className="vehicle-picker">
          <label>
            Марка
            <select
              value={brand}
              onChange={(event) => {
                const nextBrand = event.target.value;
                const nextModels = brands.find((item) => item.name === nextBrand)?.models ?? [];
                const nextModel = nextModels[0];
                setBrand(nextBrand);
                setModel(nextModel?.name ?? "");
              }}
            >
              {brands.map((item) => (
                <option key={item.name}>{item.name}</option>
              ))}
            </select>
          </label>

          <label>
            Модель
            <select value={model} onChange={(event) => setModel(event.target.value)}>
              {selectedBrand.models.map((item) => (
                <option key={item.name}>{item.name}</option>
              ))}
            </select>
          </label>

          <div className="vehicle-summary">
            <Car size={20} aria-hidden="true" />
            <span>
              {brand} {model}: {selectedModel?.years}
            </span>
          </div>
        </div>
      </section>

      <section className="workspace workspace--split">
        <div>
          <div className="section-heading">
            <p className="eyebrow">Категории</p>
            <h2>Стартовое дерево каталога</h2>
          </div>
          <div className="category-grid">
            {categories.map((category) => (
              <Link key={category.name} className="category-card" href="/catalog">
                <ClipboardList size={22} aria-hidden="true" />
                <strong>{category.name}</strong>
                <span>{category.description}</span>
              </Link>
            ))}
          </div>
        </div>

        <aside className="process-panel">
          <ShieldCheck size={28} aria-hidden="true" />
          <h3>Заказ через подтверждение</h3>
          <p>
            Корзина работает как заявка: клиент выбирает позиции, оставляет контакты, менеджер
            подтверждает наличие, состояние, срок и итоговую стоимость.
          </p>
          <Link className="secondary-action" href="/cart">
            Открыть корзину
          </Link>
        </aside>
      </section>

      <section className="workspace">
        <div className="section-heading section-heading--row">
          <div>
            <p className="eyebrow">Популярные товары</p>
            <h2>Первые позиции для витрины</h2>
          </div>
          <Link className="text-action" href="/catalog">
            Весь каталог
            <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>

        <div className="product-grid">
          {filteredParts.length > 0 ? (
            filteredParts.map((part) => (
              <article key={part.id} className="product-card">
                <Link href={`/product/${part.slug}`} className="product-card__visual">
                  <Cog size={42} aria-hidden="true" />
                  <span>{part.category}</span>
                </Link>
                <div className="product-card__body">
                  <span className="tag">{part.quality}</span>
                  <h3>
                    <Link href={`/product/${part.slug}`}>{part.name}</Link>
                  </h3>
                  <dl>
                    <div>
                      <dt>Номер</dt>
                      <dd>{part.oem}</dd>
                    </div>
                    <div>
                      <dt>Марка</dt>
                      <dd>{part.brand}</dd>
                    </div>
                    <div>
                      <dt>Срок</dt>
                      <dd>{part.availability}</dd>
                    </div>
                  </dl>
                  <div className="product-card__footer">
                    <strong>{formatPrice(part.price)}</strong>
                    <ProductActions part={part} compact />
                  </div>
                </div>
              </article>
            ))
          ) : (
            <div className="empty-state">
              <h3>Пока нет точного совпадения</h3>
              <p>Оставьте номер детали, название или данные автомобиля, и менеджер проверит поставщиков вручную.</p>
              <Link href="/request">Оставить запрос</Link>
            </div>
          )}
        </div>
      </section>

      <section className="workspace workspace--split">
        <aside className="process-panel process-panel--teal">
          <ShieldCheck size={28} aria-hidden="true" />
          <h3>Проверка перед заказом</h3>
          <p>
            Для каждой заявки менеджер сверяет номер детали, применимость, актуальную цену,
            наличие у поставщика и условия гарантии.
          </p>
          <Link className="secondary-action" href="/request">
            Отправить запрос
          </Link>
        </aside>
        <aside className="process-panel">
          <Truck size={28} aria-hidden="true" />
          <h3>Доставка и гарантии</h3>
          <p>
            Отдельная страница уже заложена под оплату, доставку, резерв, гарантию и возврат после
            добавления реальных юридических данных.
          </p>
          <Link className="secondary-action" href="/delivery">
            Условия
          </Link>
        </aside>
      </section>
    </main>
  );
}
