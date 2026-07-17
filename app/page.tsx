"use client";

import Link from "next/link";
import { ArrowRight, Car, CheckCircle2, ClipboardList, Cog, Search, ShieldCheck } from "lucide-react";
import { brands, categories, formatPrice, parts } from "@/src/data/catalog";
import { useMemo, useState } from "react";

const quickStats = [
  { label: "OEM и артикулы", value: "поиск" },
  { label: "Заводские аналоги", value: "MVP" },
  { label: "Подтверждение", value: "менеджер" }
];

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [brand, setBrand] = useState(brands[0].name);
  const [model, setModel] = useState(brands[0].models[0].name);

  const selectedBrand = brands.find((item) => item.name === brand) ?? brands[0];

  const filteredParts = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return parts.filter((part) => {
      const vehicleMatch = part.compatibility.some((item) =>
        item.toLowerCase().includes(`${brand} ${model}`.toLowerCase())
      );

      if (!normalizedQuery) {
        return vehicleMatch || part.compatibility.some((item) => item.startsWith(brand));
      }

      const haystack = [
        part.name,
        part.oem,
        part.article,
        part.manufacturer,
        part.category,
        ...part.analogs,
        ...part.compatibility
      ]
        .join(" ")
        .toLowerCase();

      return haystack.includes(normalizedQuery);
    });
  }, [brand, model, query]);

  return (
    <main>
      <section className="hero">
        <div className="hero__blueprint" aria-hidden="true">
          <div className="blueprint-board">
            <div className="blueprint-board__header">
              <span>OEM</span>
              <span>Каталог MVP</span>
            </div>
            <div className="blueprint-board__grid">
              <span>Brand</span>
              <span>Model</span>
              <span>Part</span>
              <span>Offer</span>
            </div>
            <div className="blueprint-board__lines">
              <i />
              <i />
              <i />
              <i />
            </div>
          </div>
        </div>
        <div className="hero__overlay" />
        <div className="hero__content">
          <div className="hero__copy">
            <p className="eyebrow">MVP витрина новых автозапчастей</p>
            <h1>Заводские запчасти по OEM, артикулу и автомобилю</h1>
            <p>
              Первый рабочий каркас магазина: поиск, подбор авто, карточки товаров и заявка менеджеру
              для подтверждения цены, срока и применимости.
            </p>
          </div>

          <form className="search-panel" action="/catalog">
            <label htmlFor="global-search">Номер, OEM, название или аналог</label>
            <div className="search-row">
              <Search size={20} aria-hidden="true" />
              <input
                id="global-search"
                name="q"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Например: 8W0615301T или тормозной диск"
              />
              <button type="submit">
                <span>Искать</span>
                <ArrowRight size={18} aria-hidden="true" />
              </button>
            </div>
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
          <p className="eyebrow">Подбор авто</p>
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
                setBrand(nextBrand);
                setModel(nextModels[0]?.name ?? "");
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
              {brand} {model}: {selectedBrand.models.find((item) => item.name === model)?.years}
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
            Для MVP корзина работает как заявка: клиент выбирает товар, оставляет контакты, менеджер
            проверяет применимость, цену и срок.
          </p>
          <Link className="secondary-action" href="/request">
            Отправить заявку
          </Link>
        </aside>
      </section>

      <section className="workspace">
        <div className="section-heading section-heading--row">
          <div>
            <p className="eyebrow">Товары</p>
            <h2>Первые тестовые позиции</h2>
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
                <div className="product-card__visual">
                  <Cog size={42} aria-hidden="true" />
                  <span>{part.category}</span>
                </div>
                <div className="product-card__body">
                  <span className="tag">{part.quality}</span>
                  <h3>{part.name}</h3>
                  <dl>
                    <div>
                      <dt>OEM</dt>
                      <dd>{part.oem}</dd>
                    </div>
                    <div>
                      <dt>Производитель</dt>
                      <dd>{part.manufacturer}</dd>
                    </div>
                    <div>
                      <dt>Срок</dt>
                      <dd>{part.availability}</dd>
                    </div>
                  </dl>
                  <div className="product-card__footer">
                    <strong>{formatPrice(part.price)}</strong>
                    <Link href="/request">
                      <CheckCircle2 size={17} aria-hidden="true" />
                      В заявку
                    </Link>
                  </div>
                </div>
              </article>
            ))
          ) : (
            <div className="empty-state">
              <h3>Пока нет точного совпадения</h3>
              <p>Оставьте VIN или артикул, и менеджер проверит поставщиков вручную.</p>
              <Link href="/request">Отправить запрос</Link>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
