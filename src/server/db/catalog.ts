import { randomUUID } from "node:crypto";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import {
  brands as seedBrands,
  categories as seedCategories,
  getPartSearchText,
  parts as seedParts,
  type Brand,
  type Category,
  type Part,
  type PartCondition
} from "@/src/data/catalog";
import { schemaStatements } from "@/src/server/db/schema";

type DbGlobal = typeof globalThis & {
  __zemazapDb?: DatabaseSync;
};

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

export type CustomerRequestItemInput = {
  id?: string;
  name: string;
  article?: string;
  quantity: number;
  price?: number;
};

export type CustomerRequestInput = {
  customerName: string;
  contact: string;
  vehicle?: string;
  requestText?: string;
  source: "cart" | "request_form";
  privacyAccepted: boolean;
  items?: CustomerRequestItemInput[];
};

type BrandRow = {
  id: string;
  slug: string;
  name: string;
  country: string;
};

type ModelRow = {
  id: string;
  slug: string;
  name: string;
  years: string;
};

type GenerationRow = {
  name: string;
};

type CategoryRow = {
  id: string;
  slug: string;
  name: string;
  description: string;
};

type PartRow = {
  id: string;
  slug: string;
  name: string;
  category_name: string;
  category_slug: string;
  brand_name: string;
  brand_slug: string;
  model_name: string;
  manufacturer_name: string;
  condition: PartCondition;
  quality: Part["quality"];
  description: string;
  primary_oem: string;
  primary_article: string;
  price_rub: number;
  availability: Part["availability"];
  delivery: string;
  stock: string;
};

type NumberRow = {
  kind: string;
  value: string;
};

type TextValueRow = {
  name?: string;
  value?: string;
  label?: string;
};

const DEMO_SUPPLIER_ID = "zemazap-demo-supplier";

const databasePath = () => path.join(process.cwd(), "data", "zemazap.sqlite");

const normalizeSearch = (value: string) =>
  value
    .trim()
    .toLocaleLowerCase("ru-RU")
    .replace(/\s+/g, " ");

const normalizePartNumber = (value: string) =>
  normalizeSearch(value).replace(/[\s_-]+/g, "");

const stableId = (prefix: string, value: string) => {
  const slug = value
    .trim()
    .toLocaleLowerCase("ru-RU")
    .normalize("NFKD")
    .replace(/[^\p{Letter}\p{Number}]+/gu, "-")
    .replace(/^-+|-+$/g, "");

  return `${prefix}-${slug || "item"}`;
};

const buildSearchText = (part: Part) =>
  normalizeSearch(
    [
      getPartSearchText(part),
      normalizePartNumber(part.oem),
      normalizePartNumber(part.article),
      ...part.analogs.map(normalizePartNumber)
    ].join(" ")
  );

const clampLimit = (limit?: number) => Math.min(Math.max(limit ?? 100, 1), 200);

const getDatabase = () => {
  const globalForDb = globalThis as DbGlobal;

  if (globalForDb.__zemazapDb) {
    return globalForDb.__zemazapDb;
  }

  const dbFile = databasePath();
  mkdirSync(path.dirname(dbFile), { recursive: true });

  const db = new DatabaseSync(dbFile);
  db.exec("PRAGMA foreign_keys = ON");
  db.exec("PRAGMA journal_mode = WAL");
  db.exec("PRAGMA busy_timeout = 5000");

  for (const statement of schemaStatements) {
    db.exec(statement);
  }

  seedDatabase(db);
  db.exec("PRAGMA optimize");

  globalForDb.__zemazapDb = db;
  return db;
};

const seedDatabase = (db: DatabaseSync) => {
  const upsertMeta = db.prepare(
    `INSERT INTO database_meta (key, value, updated_at)
     VALUES (?, ?, datetime('now'))
     ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = datetime('now')`
  );
  const upsertBrand = db.prepare(
    `INSERT INTO brands (id, slug, name, country, sort_order, updated_at)
     VALUES (?, ?, ?, ?, ?, datetime('now'))
     ON CONFLICT(id) DO UPDATE SET
       slug = excluded.slug,
       name = excluded.name,
       country = excluded.country,
       sort_order = excluded.sort_order,
       updated_at = datetime('now')`
  );
  const upsertModel = db.prepare(
    `INSERT INTO car_models (id, brand_id, slug, name, years, sort_order, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
     ON CONFLICT(id) DO UPDATE SET
       brand_id = excluded.brand_id,
       slug = excluded.slug,
       name = excluded.name,
       years = excluded.years,
       sort_order = excluded.sort_order,
       updated_at = datetime('now')`
  );
  const clearGenerations = db.prepare("DELETE FROM model_generations WHERE model_id = ?");
  const insertGeneration = db.prepare(
    `INSERT INTO model_generations (id, model_id, name, sort_order)
     VALUES (?, ?, ?, ?)`
  );
  const upsertCategory = db.prepare(
    `INSERT INTO categories (id, slug, name, description, sort_order, updated_at)
     VALUES (?, ?, ?, ?, ?, datetime('now'))
     ON CONFLICT(id) DO UPDATE SET
       slug = excluded.slug,
       name = excluded.name,
       description = excluded.description,
       sort_order = excluded.sort_order,
       updated_at = datetime('now')`
  );
  const upsertManufacturer = db.prepare(
    `INSERT INTO manufacturers (id, name, updated_at)
     VALUES (?, ?, datetime('now'))
     ON CONFLICT(id) DO UPDATE SET name = excluded.name, updated_at = datetime('now')`
  );
  const upsertSupplier = db.prepare(
    `INSERT INTO suppliers (id, name, kind, contact_note, updated_at)
     VALUES (?, ?, ?, ?, datetime('now'))
     ON CONFLICT(id) DO UPDATE SET
       name = excluded.name,
       kind = excluded.kind,
       contact_note = excluded.contact_note,
       updated_at = datetime('now')`
  );
  const upsertPart = db.prepare(
    `INSERT INTO parts (
       id, slug, name, category_id, brand_id, model_name, manufacturer_id,
       condition, quality, description, primary_oem, primary_article, search_text,
       sort_order, updated_at
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
     ON CONFLICT(id) DO UPDATE SET
       slug = excluded.slug,
       name = excluded.name,
       category_id = excluded.category_id,
       brand_id = excluded.brand_id,
       model_name = excluded.model_name,
       manufacturer_id = excluded.manufacturer_id,
       condition = excluded.condition,
       quality = excluded.quality,
       description = excluded.description,
       primary_oem = excluded.primary_oem,
       primary_article = excluded.primary_article,
       search_text = excluded.search_text,
       sort_order = excluded.sort_order,
       updated_at = datetime('now')`
  );
  const clearNumbers = db.prepare("DELETE FROM part_numbers WHERE part_id = ?");
  const clearCompatibility = db.prepare("DELETE FROM part_compatibility WHERE part_id = ?");
  const clearSpecs = db.prepare("DELETE FROM part_specs WHERE part_id = ?");
  const clearOffers = db.prepare("DELETE FROM price_offers WHERE part_id = ?");
  const insertNumber = db.prepare(
    `INSERT INTO part_numbers (id, part_id, kind, value, normalized_value, sort_order)
     VALUES (?, ?, ?, ?, ?, ?)`
  );
  const insertCompatibility = db.prepare(
    `INSERT INTO part_compatibility (id, part_id, label, sort_order)
     VALUES (?, ?, ?, ?)`
  );
  const insertSpec = db.prepare(
    `INSERT INTO part_specs (id, part_id, name, value, sort_order)
     VALUES (?, ?, ?, ?, ?)`
  );
  const insertOffer = db.prepare(
    `INSERT INTO price_offers (
       id, part_id, supplier_id, price_rub, availability, delivery, stock, is_primary, updated_at
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, 1, datetime('now'))`
  );

  db.exec("BEGIN");
  try {
    upsertMeta.run("database_mode", "sqlite-development");
    upsertMeta.run("production_database_target", "postgresql");
    upsertMeta.run("catalog_seed_version", "2026-08-01");
    upsertSupplier.run(
      DEMO_SUPPLIER_ID,
      "Демо-поставщик Zemazap",
      "demo",
      "Временный источник цен и сроков для MVP"
    );

    seedBrands.forEach((brand, brandIndex) => {
      upsertBrand.run(brand.slug, brand.slug, brand.name, brand.country, brandIndex);

      brand.models.forEach((model, modelIndex) => {
        const modelId = `${brand.slug}:${model.slug}`;
        upsertModel.run(modelId, brand.slug, model.slug, model.name, model.years, modelIndex);
        clearGenerations.run(modelId);

        model.generations.forEach((generation, generationIndex) => {
          insertGeneration.run(`${modelId}:${generationIndex}`, modelId, generation, generationIndex);
        });
      });
    });

    seedCategories.forEach((category, categoryIndex) => {
      upsertCategory.run(
        category.slug,
        category.slug,
        category.name,
        category.description,
        categoryIndex
      );
    });

    seedParts.forEach((part, partIndex) => {
      const manufacturerId = stableId("manufacturer", part.manufacturer);
      upsertManufacturer.run(manufacturerId, part.manufacturer);
      upsertPart.run(
        part.id,
        part.slug,
        part.name,
        part.categorySlug,
        part.brandSlug,
        part.model,
        manufacturerId,
        part.condition,
        part.quality,
        part.description,
        part.oem,
        part.article,
        buildSearchText(part),
        partIndex
      );

      clearNumbers.run(part.id);
      clearCompatibility.run(part.id);
      clearSpecs.run(part.id);
      clearOffers.run(part.id);

      insertNumber.run(`${part.id}:oem`, part.id, "oem", part.oem, normalizePartNumber(part.oem), 0);
      insertNumber.run(
        `${part.id}:article`,
        part.id,
        "article",
        part.article,
        normalizePartNumber(part.article),
        1
      );
      part.analogs.forEach((analog, analogIndex) => {
        insertNumber.run(
          `${part.id}:analog:${analogIndex}`,
          part.id,
          "analog",
          analog,
          normalizePartNumber(analog),
          analogIndex + 2
        );
      });
      part.compatibility.forEach((label, compatibilityIndex) => {
        insertCompatibility.run(
          `${part.id}:compatibility:${compatibilityIndex}`,
          part.id,
          label,
          compatibilityIndex
        );
      });
      Object.entries(part.specs).forEach(([name, value], specIndex) => {
        insertSpec.run(`${part.id}:spec:${specIndex}`, part.id, name, value, specIndex);
      });
      insertOffer.run(
        `${part.id}:primary-offer`,
        part.id,
        DEMO_SUPPLIER_ID,
        part.price,
        part.availability,
        part.delivery,
        part.stock
      );
    });

    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
};

export const getBrands = (): Brand[] => {
  const db = getDatabase();
  const brandRows = db
    .prepare("SELECT id, slug, name, country FROM brands ORDER BY sort_order, name")
    .all() as BrandRow[];
  const modelStatement = db.prepare(
    "SELECT id, slug, name, years FROM car_models WHERE brand_id = ? ORDER BY sort_order, name"
  );
  const generationStatement = db.prepare(
    "SELECT name FROM model_generations WHERE model_id = ? ORDER BY sort_order, name"
  );

  return brandRows.map((brand) => {
    const models = modelStatement.all(brand.id) as ModelRow[];

    return {
      name: brand.name,
      slug: brand.slug,
      country: brand.country,
      models: models.map((model) => ({
        name: model.name,
        slug: model.slug,
        years: model.years,
        generations: (generationStatement.all(model.id) as GenerationRow[]).map((row) => row.name)
      }))
    };
  });
};

export const getBrandBySlug = (slug: string) =>
  getBrands().find((brand) => brand.slug === slug);

export const getBrandSlugs = () => getBrands().map((brand) => brand.slug);

export const getCategories = (): Category[] => {
  const db = getDatabase();

  return (
    db
      .prepare("SELECT id, slug, name, description FROM categories ORDER BY sort_order, name")
      .all() as CategoryRow[]
  ).map((category) => ({
    name: category.name,
    slug: category.slug,
    description: category.description
  }));
};

const partSelect = `
  SELECT
    p.id,
    p.slug,
    p.name,
    c.name AS category_name,
    c.slug AS category_slug,
    b.name AS brand_name,
    b.slug AS brand_slug,
    p.model_name,
    m.name AS manufacturer_name,
    p.condition,
    p.quality,
    p.description,
    p.primary_oem,
    p.primary_article,
    po.price_rub,
    po.availability,
    po.delivery,
    po.stock
  FROM parts p
  JOIN categories c ON c.id = p.category_id
  JOIN brands b ON b.id = p.brand_id
  JOIN manufacturers m ON m.id = p.manufacturer_id
  JOIN price_offers po ON po.part_id = p.id AND po.is_primary = 1
`;

const mapPartRow = (db: DatabaseSync, row: PartRow): Part => {
  const numberRows = db
    .prepare("SELECT kind, value FROM part_numbers WHERE part_id = ? ORDER BY sort_order")
    .all(row.id) as NumberRow[];
  const compatibilityRows = db
    .prepare("SELECT label FROM part_compatibility WHERE part_id = ? ORDER BY sort_order")
    .all(row.id) as TextValueRow[];
  const specRows = db
    .prepare("SELECT name, value FROM part_specs WHERE part_id = ? ORDER BY sort_order")
    .all(row.id) as TextValueRow[];

  const specs = specRows.reduce<Record<string, string>>((acc, spec) => {
    if (spec.name && spec.value) {
      acc[spec.name] = spec.value;
    }
    return acc;
  }, {});

  return {
    id: row.id,
    slug: row.slug,
    name: row.name,
    oem: row.primary_oem,
    article: row.primary_article,
    manufacturer: row.manufacturer_name,
    category: row.category_name,
    categorySlug: row.category_slug,
    brand: row.brand_name,
    brandSlug: row.brand_slug,
    model: row.model_name,
    compatibility: compatibilityRows.map((item) => item.label ?? "").filter(Boolean),
    price: row.price_rub,
    availability: row.availability,
    delivery: row.delivery,
    analogs: numberRows.filter((item) => item.kind === "analog").map((item) => item.value),
    condition: row.condition,
    quality: row.quality,
    stock: row.stock,
    description: row.description,
    specs
  };
};

export const getParts = (filters: CatalogFilters = {}): Part[] => {
  const db = getDatabase();
  const where: string[] = [];
  const params: Array<string | number> = [];

  if (filters.query?.trim()) {
    where.push("p.search_text LIKE ?");
    params.push(`%${normalizeSearch(filters.query)}%`);
  }

  if (filters.brandSlug?.trim()) {
    where.push("b.slug = ?");
    params.push(filters.brandSlug.trim());
  }

  if (filters.categorySlug?.trim()) {
    where.push("c.slug = ?");
    params.push(filters.categorySlug.trim());
  }

  if (filters.condition?.trim()) {
    where.push("p.condition = ?");
    params.push(filters.condition.trim());
  }

  params.push(clampLimit(filters.limit));

  const sql = `${partSelect}
    ${where.length > 0 ? `WHERE ${where.join(" AND ")}` : ""}
    ORDER BY p.sort_order, p.name
    LIMIT ?`;
  const rows = db.prepare(sql).all(...params) as PartRow[];

  return rows.map((row) => mapPartRow(db, row));
};

export const getPartBySlug = (slug: string) => {
  const db = getDatabase();
  const row = db
    .prepare(`${partSelect} WHERE p.slug = ? LIMIT 1`)
    .get(slug) as PartRow | undefined;

  return row ? mapPartRow(db, row) : undefined;
};

export const getPartsByBrandSlug = (brandSlug: string) =>
  getParts({ brandSlug, limit: 100 });

export const getSimilarParts = (part: Part, limit = 4) =>
  getParts({ limit: 100 })
    .filter(
      (item) =>
        item.id !== part.id &&
        (item.categorySlug === part.categorySlug || item.brandSlug === part.brandSlug)
    )
    .slice(0, limit);

export const getPartSlugs = () => {
  const db = getDatabase();

  return (db.prepare("SELECT slug FROM parts ORDER BY sort_order, name").all() as Array<{ slug: string }>).map(
    (part) => part.slug
  );
};

export const getCatalogSnapshot = (filters: CatalogFilters = {}): CatalogSnapshot => ({
  brands: getBrands(),
  categories: getCategories(),
  parts: getParts(filters)
});

export const createCustomerRequest = (input: CustomerRequestInput) => {
  const db = getDatabase();
  const id = randomUUID();
  const items = input.items ?? [];
  const totalEstimateRub = items.reduce(
    (sum, item) => sum + Math.max(0, Math.round(item.price ?? 0)) * Math.max(1, Math.round(item.quantity)),
    0
  );

  const insertRequest = db.prepare(
    `INSERT INTO customer_requests (
       id, status, source, customer_name, contact, vehicle, request_text,
       privacy_accepted, total_estimate_rub, created_at, updated_at
     )
     VALUES (?, 'new', ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))`
  );
  const insertItem = db.prepare(
    `INSERT INTO customer_request_items (
       id, request_id, part_id, part_name, article, quantity, price_snapshot_rub
     )
     VALUES (?, ?, ?, ?, ?, ?, ?)`
  );
  const partExists = db.prepare("SELECT id FROM parts WHERE id = ? LIMIT 1");

  db.exec("BEGIN");
  try {
    insertRequest.run(
      id,
      input.source,
      input.customerName,
      input.contact,
      input.vehicle ?? "",
      input.requestText ?? "",
      input.privacyAccepted ? 1 : 0,
      totalEstimateRub
    );

    items.forEach((item, index) => {
      const existingPart = item.id ? (partExists.get(item.id) as { id: string } | undefined) : undefined;
      insertItem.run(
        `${id}:${index}`,
        id,
        existingPart?.id ?? null,
        item.name,
        item.article ?? "",
        Math.max(1, Math.round(item.quantity)),
        Math.max(0, Math.round(item.price ?? 0))
      );
    });

    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }

  return {
    id,
    status: "new",
    totalEstimateRub
  };
};
