"use client";

import Link from "next/link";
import { Minus, Plus, Send, ShoppingCart, Trash2 } from "lucide-react";
import { formatPrice } from "@/src/data/catalog";
import { catalogStorageKeys, type StoredCatalogItem } from "@/src/components/ProductActions";
import { useEffect, useMemo, useState } from "react";

const readCart = (): StoredCatalogItem[] => {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const value = window.localStorage.getItem(catalogStorageKeys.cart);
    return value ? (JSON.parse(value) as StoredCatalogItem[]) : [];
  } catch {
    return [];
  }
};

const writeCart = (items: StoredCatalogItem[]) => {
  window.localStorage.setItem(catalogStorageKeys.cart, JSON.stringify(items));
  window.dispatchEvent(new CustomEvent("zemazap-storage"));
};

export default function CartContents() {
  const [items, setItems] = useState<StoredCatalogItem[]>([]);
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [submitState, setSubmitState] = useState<
    | { status: "idle" }
    | { status: "sending" }
    | { status: "success"; requestId: string }
    | { status: "error"; message: string }
  >({ status: "idle" });

  useEffect(() => {
    const sync = () => setItems(readCart());
    sync();
    window.addEventListener("zemazap-storage", sync);
    window.addEventListener("storage", sync);

    return () => {
      window.removeEventListener("zemazap-storage", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const total = useMemo(
    () => items.reduce((sum, item) => sum + item.price * item.quantity, 0),
    [items]
  );

  const updateQuantity = (id: string, delta: number) => {
    const next = items.map((item) =>
      item.id === id ? { ...item, quantity: Math.max(1, item.quantity + delta) } : item
    );
    setItems(next);
    writeCart(next);
  };

  const removeItem = (id: string) => {
    const next = items.filter((item) => item.id !== id);
    setItems(next);
    writeCart(next);
  };

  const submitCartRequest = async () => {
    setSubmitState({ status: "sending" });

    try {
      const response = await fetch("/api/requests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          source: "cart",
          customerName: name,
          contact,
          privacyAccepted,
          requestText: "Корзина-заявка с сайта",
          items: items.map((item) => ({
            id: item.id,
            name: item.name,
            article: item.article,
            quantity: item.quantity,
            price: item.price
          }))
        })
      });
      const result = (await response.json()) as { id?: string; error?: string };

      if (!response.ok || !result.id) {
        setSubmitState({
          status: "error",
          message: result.error ?? "Не удалось сохранить заявку"
        });
        return;
      }

      setName("");
      setContact("");
      setPrivacyAccepted(false);
      setItems([]);
      writeCart([]);
      setSubmitState({ status: "success", requestId: result.id });
    } catch {
      setSubmitState({
        status: "error",
        message: "Не удалось связаться с сервером"
      });
    }
  };

  return (
    <section className="cart-layout">
      <div className="cart-panel">
        <div className="cart-panel__head">
          <ShoppingCart size={22} aria-hidden="true" />
          <h2>Состав корзины</h2>
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
                <div className="quantity-control" aria-label={`Количество ${item.name}`}>
                  <button type="button" onClick={() => updateQuantity(item.id, -1)} aria-label="Уменьшить">
                    <Minus size={16} aria-hidden="true" />
                  </button>
                  <span>{item.quantity}</span>
                  <button type="button" onClick={() => updateQuantity(item.id, 1)} aria-label="Увеличить">
                    <Plus size={16} aria-hidden="true" />
                  </button>
                </div>
                <strong>{formatPrice(item.price * item.quantity)}</strong>
                <button type="button" className="icon-action" onClick={() => removeItem(item.id)} aria-label="Удалить">
                  <Trash2 size={17} aria-hidden="true" />
                </button>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state empty-state--inside">
            <h3>Корзина пока пустая</h3>
            <p>Добавьте товары из каталога, чтобы собрать заявку менеджеру.</p>
            <Link href="/catalog">Перейти в каталог</Link>
          </div>
        )}
      </div>

      <aside className="request-aside cart-summary">
        <h2>Итого к подтверждению</h2>
        <strong>{formatPrice(total)}</strong>
        <p>Цена предварительная. Менеджер подтвердит наличие, состояние, срок доставки и применимость.</p>
        <label>
          Имя
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Как к вам обращаться" />
        </label>
        <label>
          Телефон или мессенджер
          <input
            value={contact}
            onChange={(event) => setContact(event.target.value)}
            placeholder="+7 (___) ___-__-__"
          />
        </label>
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={privacyAccepted}
            onChange={(event) => setPrivacyAccepted(event.target.checked)}
          />
          <span>Согласен на обработку персональных данных после добавления юридического текста</span>
        </label>
        <button
          type="button"
          disabled={
            !items.length ||
            !name.trim() ||
            !contact.trim() ||
            !privacyAccepted ||
            submitState.status === "sending"
          }
          onClick={submitCartRequest}
        >
          <Send size={18} aria-hidden="true" />
          {submitState.status === "sending" ? "Сохраняем" : "Оформить заявку"}
        </button>
        {submitState.status === "success" ? (
          <p className="form-note">Заявка сохранена в базе: {submitState.requestId}</p>
        ) : null}
        {submitState.status === "error" ? (
          <p className="form-note form-note--error">{submitState.message}</p>
        ) : null}
      </aside>
    </section>
  );
}
