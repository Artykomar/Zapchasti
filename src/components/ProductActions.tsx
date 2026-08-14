"use client";

import { Check, Heart, ShoppingCart } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getProductIdentifier, type Part } from "@/src/data/catalog";
import {
  catalogStorageEventName,
  catalogStorageKeys,
  readStoredCatalogItems,
  type StoredCatalogItem,
  toggleStoredCatalogItem,
  upsertStoredCatalogItem
} from "@/src/components/catalogStorage";

const toStoredItem = (part: Part): StoredCatalogItem => ({
  id: part.id,
  slug: getProductIdentifier(part),
  name: part.name,
  article: part.article,
  brand: part.brand,
  model: part.model,
  price: part.price,
  quantity: 1
});

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
      setInCart(readStoredCatalogItems(catalogStorageKeys.cart).some((entry) => entry.id === item.id));
      setInFavorites(readStoredCatalogItems(catalogStorageKeys.favorites).some((entry) => entry.id === item.id));
    };

    sync();
    window.addEventListener(catalogStorageEventName, sync);
    window.addEventListener("storage", sync);

    return () => {
      window.removeEventListener(catalogStorageEventName, sync);
      window.removeEventListener("storage", sync);
    };
  }, [item.id]);

  return (
    <div className={compact ? "product-actions product-actions--compact" : "product-actions"}>
      <button
        type="button"
        className={inCart ? "action-button action-button--done" : "action-button"}
        onClick={() => setInCart(toggleStoredCatalogItem(catalogStorageKeys.cart, item))}
      >
        {inCart ? <Check size={17} aria-hidden="true" /> : <ShoppingCart size={17} aria-hidden="true" />}
        {inCart ? "В корзине" : "В корзину"}
      </button>
      <button
        type="button"
        className={inFavorites ? "icon-action icon-action--done" : "icon-action"}
        aria-label={inFavorites ? "Товар уже в избранном" : "Добавить товар в избранное"}
        onClick={() => setInFavorites(upsertStoredCatalogItem(catalogStorageKeys.favorites, item))}
      >
        {inFavorites ? <Check size={17} aria-hidden="true" /> : <Heart size={17} aria-hidden="true" />}
      </button>
    </div>
  );
}
