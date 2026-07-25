"use client";

import Link from "next/link";
import { Heart, ShoppingCart, Trash2 } from "lucide-react";
import { formatPrice } from "@/src/data/catalog";
import { catalogStorageKeys, type StoredCatalogItem } from "@/src/components/ProductActions";
import { useEffect, useState } from "react";

const readFavorites = (): StoredCatalogItem[] => {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const value = window.localStorage.getItem(catalogStorageKeys.favorites);
    return value ? (JSON.parse(value) as StoredCatalogItem[]) : [];
  } catch {
    return [];
  }
};

const write = (key: string, items: StoredCatalogItem[]) => {
  window.localStorage.setItem(key, JSON.stringify(items));
  window.dispatchEvent(new CustomEvent("zemazap-storage"));
};

export default function FavoritesContents() {
  const [items, setItems] = useState<StoredCatalogItem[]>([]);

  useEffect(() => {
    const sync = () => setItems(readFavorites());
    sync();
    window.addEventListener("zemazap-storage", sync);
    window.addEventListener("storage", sync);

    return () => {
      window.removeEventListener("zemazap-storage", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const removeItem = (id: string) => {
    const next = items.filter((item) => item.id !== id);
    setItems(next);
    write(catalogStorageKeys.favorites, next);
  };

  const addToCart = (item: StoredCatalogItem) => {
    const cartValue = window.localStorage.getItem(catalogStorageKeys.cart);
    const cart = cartValue ? (JSON.parse(cartValue) as StoredCatalogItem[]) : [];
    const next = cart.some((entry) => entry.id === item.id) ? cart : [...cart, item];
    write(catalogStorageKeys.cart, next);
  };

  return (
    <section className="cart-panel favorites-panel">
      <div className="cart-panel__head">
        <Heart size={22} aria-hidden="true" />
        <h2>Избранные товары</h2>
      </div>

      {items.length > 0 ? (
        <div className="cart-list">
          {items.map((item) => (
            <article key={item.id} className="cart-item">
              <div>
                <h3>
                  <Link href={`/product/${item.slug}`}>{item.name}</Link>
                </h3>
                <p>
                  {item.brand} {item.model}, арт. {item.article}
                </p>
              </div>
              <strong>{formatPrice(item.price)}</strong>
              <button type="button" className="action-button" onClick={() => addToCart(item)}>
                <ShoppingCart size={17} aria-hidden="true" />
                В корзину
              </button>
              <button type="button" className="icon-action" onClick={() => removeItem(item.id)} aria-label="Удалить">
                <Trash2 size={17} aria-hidden="true" />
              </button>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state empty-state--inside">
          <h3>Избранного пока нет</h3>
          <p>Отмечайте позиции в каталоге, чтобы вернуться к ним перед заявкой.</p>
          <Link href="/catalog">Перейти в каталог</Link>
        </div>
      )}
    </section>
  );
}
