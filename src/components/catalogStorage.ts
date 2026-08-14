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

export const catalogStorageKeys = {
  cart: "zemazap-cart",
  favorites: "zemazap-favorites"
};

export const catalogStorageEventName = "zemazap-storage";

const isStoredCatalogItem = (value: unknown): value is StoredCatalogItem => {
  if (!value || typeof value !== "object") {
    return false;
  }

  const item = value as Record<string, unknown>;

  return (
    typeof item.id === "string" &&
    typeof item.slug === "string" &&
    typeof item.name === "string" &&
    typeof item.article === "string" &&
    typeof item.brand === "string" &&
    typeof item.model === "string" &&
    typeof item.price === "number"
  );
};

export const readStoredCatalogItems = (key: string): StoredCatalogItem[] => {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const value = window.localStorage.getItem(key);
    const parsed = value ? (JSON.parse(value) as unknown) : [];

    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter(isStoredCatalogItem).map((item) => ({
      ...item,
      quantity: Number.isFinite(item.quantity) ? Math.max(1, Math.trunc(item.quantity)) : 1
    }));
  } catch {
    return [];
  }
};

export const writeStoredCatalogItems = (key: string, items: StoredCatalogItem[]) => {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(key, JSON.stringify(items));
  window.dispatchEvent(new CustomEvent(catalogStorageEventName));
};

export const upsertStoredCatalogItem = (key: string, item: StoredCatalogItem) => {
  const current = readStoredCatalogItems(key);
  const existing = current.find((entry) => entry.id === item.id);
  const next = existing
    ? current.map((entry) => (entry.id === item.id ? { ...entry, quantity: Math.max(1, entry.quantity) } : entry))
    : [...current, item];

  writeStoredCatalogItems(key, next);
  return next.some((entry) => entry.id === item.id);
};

export const removeStoredCatalogItem = (key: string, id: string) => {
  const next = readStoredCatalogItems(key).filter((entry) => entry.id !== id);
  writeStoredCatalogItems(key, next);
  return false;
};

export const toggleStoredCatalogItem = (key: string, item: StoredCatalogItem) => {
  const current = readStoredCatalogItems(key);
  const exists = current.some((entry) => entry.id === item.id);
  const next = exists ? current.filter((entry) => entry.id !== item.id) : [...current, item];

  writeStoredCatalogItems(key, next);
  return !exists;
};

export const countStoredCatalogItems = (key: string) =>
  readStoredCatalogItems(key).reduce((total, item) => total + item.quantity, 0);
