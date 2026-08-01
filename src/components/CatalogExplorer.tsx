"use client";

import Link from "next/link";
import { ArrowRight, Filter, PackageCheck, Search } from "lucide-react";
import ProductActions from "@/src/components/ProductActions";
import type { Brand, Category, Part } from "@/src/data/catalog";
import { formatPrice } from "@/src/data/catalog";
import { useEffect, useState } from "react";

type CatalogExplorerProps = {
  parts: Part[];
  brands: Brand[];
  categories: Category[];
  initialQuery?: string;
  initialBrand?: string;
  initialCategory?: string;
};

const allValue = "all";

export default function CatalogExplorer({
  parts,
  brands,
  categories,
  initialQuery = "",
  initialBrand = allValue,
  initialCategory = allValue
}: CatalogExplorerProps) {
  const [query, setQuery] = useState(initialQuery);
  const [brand, setBrand] = useState(initialBrand);
  const [category, setCategory] = useState(initialCategory);
  const [condition, setCondition] = useState(allValue);
  const [filteredParts, setFilteredParts] = useState(parts);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams();

    if (query.trim()) {
      params.set("q", query.trim());
    }

    if (brand !== allValue) {
      params.set("brand", brand);
    }

    if (category !== allValue) {
      params.set("category", category);
    }

    if (condition !== allValue) {
      params.set("condition", condition);
    }

    setIsLoading(true);
    setErrorMessage("");

    fetch(`/api/catalog?${params.toString()}`, { signal: controller.signal })
      .then(async (response) => {
        const data = (await response.json()) as { parts?: Part[]; error?: string };

        if (!response.ok || !data.parts) {
          throw new Error(data.error ?? "Не удалось обновить каталог");
        }

        setFilteredParts(data.parts);
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setErrorMessage(error instanceof Error ? error.message : "Не удалось обновить каталог");
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      });

    return () => controller.abort();
  }, [brand, category, condition, query]);

  return (
    <>
      <section className="catalog-tools" aria-label="Инструменты каталога">
        <label>
          <Search size={18} aria-hidden="true" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Поиск по номеру, артикулу, марке или названию"
          />
        </label>
        <button
          type="button"
          onClick={() => {
            setQuery("");
            setBrand(allValue);
            setCategory(allValue);
            setCondition(allValue);
          }}
        >
          <Filter size={18} aria-hidden="true" />
          Сбросить
        </button>
      </section>

      <section className="catalog-layout">
        <aside className="catalog-sidebar">
          <h2>Марки</h2>
          <label className="filter-option">
            <input
              type="radio"
              name="brand"
              checked={brand === allValue}
              onChange={() => setBrand(allValue)}
            />
            Все марки
          </label>
          {brands.map((item) => (
            <div key={item.slug} className="sidebar-group">
              <label className="filter-option">
                <input
                  type="radio"
                  name="brand"
                  checked={brand === item.slug}
                  onChange={() => setBrand(item.slug)}
                />
                <strong>{item.name}</strong>
              </label>
              {item.models.map((model) => (
                <Link key={model.slug} href={`/product-category/${item.slug}`}>
                  {model.name}, {model.years}
                </Link>
              ))}
            </div>
          ))}

          <h2>Категории</h2>
          <label className="filter-option">
            <input
              type="radio"
              name="category"
              checked={category === allValue}
              onChange={() => setCategory(allValue)}
            />
            Все категории
          </label>
          {categories.map((item) => (
            <label key={item.slug} className="filter-option">
              <input
                type="radio"
                name="category"
                checked={category === item.slug}
                onChange={() => setCategory(item.slug)}
              />
              {item.name}
            </label>
          ))}

          <h2>Состояние</h2>
          {[
            { value: allValue, label: "Любое" },
            { value: "новая", label: "Новые" },
            { value: "контрактная", label: "Контрактные" },
            { value: "восстановленная", label: "Восстановленные" }
          ].map((item) => (
            <label key={item.value} className="filter-option">
              <input
                type="radio"
                name="condition"
                checked={condition === item.value}
                onChange={() => setCondition(item.value)}
              />
              {item.label}
            </label>
          ))}
        </aside>

        <div className="catalog-products">
          <div className="catalog-count">
            {isLoading ? "Обновляем каталог" : "Найдено позиций"}: <strong>{filteredParts.length}</strong>
          </div>
          {errorMessage ? <p className="form-note form-note--error">{errorMessage}</p> : null}
          {filteredParts.length > 0 ? (
            filteredParts.map((part) => (
              <article key={part.id} className="wide-product">
                <Link className="wide-product__visual" href={`/product/${part.slug}`}>
                  <PackageCheck size={42} aria-hidden="true" />
                  <span>{part.condition}</span>
                </Link>
                <div className="wide-product__content">
                  <span className="tag">{part.category}</span>
                  <h2>
                    <Link href={`/product/${part.slug}`}>{part.name}</Link>
                  </h2>
                  <p>{part.delivery}</p>
                  <div className="spec-list">
                    <span>Номер: {part.oem}</span>
                    <span>Артикул: {part.article}</span>
                    <span>Марка: {part.brand} {part.model}</span>
                    <span>Производитель: {part.manufacturer}</span>
                  </div>
                </div>
                <div className="wide-product__action">
                  <strong>{formatPrice(part.price)}</strong>
                  <span>{part.availability}</span>
                  <ProductActions part={part} compact />
                  <Link href={`/product/${part.slug}`} className="text-action">
                    Подробнее
                    <ArrowRight size={17} aria-hidden="true" />
                  </Link>
                </div>
              </article>
            ))
          ) : (
            <div className="empty-state">
              <h3>Пока нет точного совпадения</h3>
              <p>Можно оставить заявку по номеру детали, названию или модели автомобиля.</p>
              <Link href="/request">Оставить заявку</Link>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
