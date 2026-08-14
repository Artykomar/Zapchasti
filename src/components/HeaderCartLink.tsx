"use client";

import Link from "next/link";
import { ShoppingCart } from "lucide-react";
import { useEffect, useState } from "react";
import {
  catalogStorageEventName,
  catalogStorageKeys,
  countStoredCatalogItems
} from "@/src/components/catalogStorage";

export default function HeaderCartLink() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const sync = () => setCount(countStoredCatalogItems(catalogStorageKeys.cart));

    sync();
    window.addEventListener(catalogStorageEventName, sync);
    window.addEventListener("storage", sync);

    return () => {
      window.removeEventListener(catalogStorageEventName, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  return (
    <Link className="cart-link" href="/cart">
      <ShoppingCart size={18} aria-hidden="true" />
      <span>Корзина</span>
      {count > 0 ? (
        <strong className="cart-link__badge" aria-label={`В корзине ${count} поз.`}>
          {count}
        </strong>
      ) : null}
    </Link>
  );
}
