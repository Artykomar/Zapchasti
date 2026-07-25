"use client";

import { Check, Heart, ShoppingCart } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { Part } from "@/src/data/catalog";

export type StoredCatalogItem = {
  id: string;
  slug: string;
  name: string;
  article: string;
  brand: string;
  model: string;
  price: number;
  quantity: number;
};

const CART_KEY = "zemazap-cart";
const FAVORITES_KEY = "zemazap-favorites";

const toStoredItem = (part: Part): StoredCatalogItem => ({
  id: part.id,
  slug: part.slug,
  name: part.name,
  article: part.article,
  brand: part.brand,
  model: part.model,
  price: part.price,
  quantity: 1
});

const readItems = (key: string): StoredCatalogItem[] => {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const value = window.localStorage.getItem(key);
    return value ? (JSON.parse(value) as StoredCatalogItem[]) : [];
  } catch {
    return [];
  }
};

const writeItems = (key: string, items: StoredCatalogItem[]) => {
  window.localStorage.setItem(key, JSON.stringify(items));
  window.dispatchEvent(new CustomEvent("zemazap-storage"));
};

const upsertItem = (key: string, item: StoredCatalogItem) => {
  const current = readItems(key);
  const existing = current.find((entry) => entry.id === item.id);
  const next = existing
    ? current.map((entry) =>
        entry.id === item.id ? { ...entry, quantity: Math.max(1, entry.quantity) } : entry
      )
    : [...current, item];

  writeItems(key, next);
  return next.some((entry) => entry.id === item.id);
};

type ProductActionsProps = {
  part: Part;
  compact?: boolean;
};

export default function ProductActions({ part, compact = false }: ProductActionsProps) {
  const item = useMemo(() => toStoredItem(part), [part]);
  const [inCart, setInCart] = useState(false);
  const [inFavorites, setInFavorites] = useState(false);

  useEffect(() => {
    const sync = () => {
      setInCart(readItems(CART_KEY).some((entry) => entry.id === item.id));
      setInFavorites(readItems(FAVORITES_KEY).some((entry) => entry.id === item.id));
    };

    sync();
    window.addEventListener("zemazap-storage", sync);
    window.addEventListener("storage", sync);

    return () => {
      window.removeEventListener("zemazap-storage", sync);
      window.removeEventListener("storage", sync);
    };
  }, [item.id]);

  return (
    <div className={compact ? "product-actions product-actions--compact" : "product-actions"}>
      <button
        type="button"
        className={inCart ? "action-button action-button--done" : "action-button"}
        onClick={() => setInCart(upsertItem(CART_KEY, item))}
      >
        {inCart ? <Check size={17} aria-hidden="true" /> : <ShoppingCart size={17} aria-hidden="true" />}
        {inCart ? "В корзине" : "В корзину"}
      </button>
      <button
        type="button"
        className={inFavorites ? "icon-action icon-action--done" : "icon-action"}
        aria-label={inFavorites ? "Товар уже в избранном" : "Добавить товар в избранное"}
        onClick={() => setInFavorites(upsertItem(FAVORITES_KEY, item))}
      >
        {inFavorites ? <Check size={17} aria-hidden="true" /> : <Heart size={17} aria-hidden="true" />}
      </button>
    </div>
  );
}

export const catalogStorageKeys = {
  cart: CART_KEY,
  favorites: FAVORITES_KEY
};
