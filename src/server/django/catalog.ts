import type { Brand, Category, Part } from "@/src/data/catalog";
import { DjangoApiError, fetchDjangoJson } from "@/src/server/django/client";

export type CatalogFilters = {
  query?: string;
  brandSlug?: string;
  categorySlug?: string;
  condition?: string;
  limit?: number;
};

export type CatalogSnapshot = {
  brands: Brand[];
  categories: Category[];
  parts: Part[];
};

type DjangoCatalogResponse = CatalogSnapshot & {
  meta?: {
    backend?: string;
  };
};

type DjangoPartResponse = {
  part?: Part;
  error?: string;
};

const withCatalogParams = (filters: CatalogFilters = {}) => {
  const params = new URLSearchParams();

  if (filters.query?.trim()) {
    params.set("q", filters.query.trim());
  }

  if (filters.brandSlug?.trim()) {
    params.set("brand", filters.brandSlug.trim());
  }

  if (filters.categorySlug?.trim()) {
    params.set("category", filters.categorySlug.trim());
  }

  if (filters.condition?.trim()) {
    params.set("condition", filters.condition.trim());
  }

  if (filters.limit) {
    params.set("limit", String(filters.limit));
  }

  return `/api/catalog/${params.size ? `?${params.toString()}` : ""}`;
};

export const getCatalogSnapshot = async (filters: CatalogFilters = {}): Promise<CatalogSnapshot> => {
  const payload = await fetchDjangoJson<DjangoCatalogResponse>(withCatalogParams(filters));

  return {
    brands: payload.brands ?? [],
    categories: payload.categories ?? [],
    parts: payload.parts ?? []
  };
};

export const getPartBySlug = async (slug: string) => {
  try {
    const payload = await fetchDjangoJson<DjangoPartResponse>(`/api/catalog/${encodeURIComponent(slug)}/`);
    return payload.part;
  } catch (error) {
    if (error instanceof DjangoApiError && error.status === 404) {
      return undefined;
    }
    throw error;
  }
};

export const getSimilarParts = async (part: Part, limit = 4) => {
  const catalog = await getCatalogSnapshot({ limit: 100 });

  return catalog.parts
    .filter(
      (item) =>
        item.id !== part.id &&
        (item.categorySlug === part.categorySlug || item.brandSlug === part.brandSlug)
    )
    .slice(0, limit);
};

export const getBrandBySlug = async (slug: string) => {
  const catalog = await getCatalogSnapshot({ limit: 1 });
  return catalog.brands.find((brand) => brand.slug === slug);
};

export const getPartsByBrandSlug = async (brandSlug: string) => {
  const catalog = await getCatalogSnapshot({ brandSlug, limit: 100 });
  return catalog.parts;
};
