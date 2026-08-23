export type CarModel = {
  name: string;
  slug: string;
  years: string;
  generations: string[];
};

export type Brand = {
  name: string;
  slug: string;
  country: string;
  models: CarModel[];
};

export type Category = {
  name: string;
  slug: string;
  description: string;
};

export type PartCondition = "новая" | "контрактная" | "восстановленная" | "б/у";

export type Part = {
  id: string;
  slug: string;
  name: string;
  oem: string;
  article: string;
  manufacturer: string;
  category: string;
  categorySlug: string;
  brand: string;
  brandSlug: string;
  model: string;
  compatibility: string[];
  price: number;
  availability: "в наличии" | "1-3 дня" | "под заказ" | "уточнить";
  delivery: string;
  analogs: string[];
  condition: PartCondition;
  photo_kind?: "illustrative" | "actual";
  warranty_terms?: string;
  return_terms?: string;
  marking_required?: boolean;
  marking_status?: "not_required" | "requires_review" | "confirmed" | "blocked";
  marking_category?: string;
  quality: "оригинал" | "заводской аналог" | "проверенная контрактная";
  stock: string;
  description: string;
  specs: Record<string, string>;
};

export const formatPrice = (value: number) =>
  new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(value);

export const normalize = (value: string) => value.trim().toLowerCase();

export const getProductIdentifier = (part: Pick<Part, "slug"> & Partial<Pick<Part, "article">>) =>
  part.article?.trim() || part.slug;

export const getProductPath = (part: Pick<Part, "slug"> & Partial<Pick<Part, "article">>) =>
  `/product/${encodeURIComponent(getProductIdentifier(part))}`;

export const getPartSearchText = (part: Part) =>
  [
    part.name,
    part.oem,
    part.article,
    part.manufacturer,
    part.category,
    part.brand,
    part.model,
    part.condition,
    part.quality,
    ...part.analogs,
    ...part.compatibility,
    ...Object.values(part.specs)
  ]
    .join(" ")
    .toLowerCase();
