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

export type CustomerRequestStatus = "new" | "in_work" | "waiting_customer" | "done" | "cancelled";

export type Customer = {
  id: string;
  displayName: string;
  contact: string;
  normalizedContact: string;
  createdAt: string;
  updatedAt: string;
};

export type AdminCustomerRequestItem = {
  id: string;
  partId: string | null;
  partName: string;
  article: string;
  quantity: number;
  priceSnapshotRub: number;
};

export type AdminCustomerRequestEvent = {
  id: string;
  eventType: string;
  note: string;
  createdAt: string;
};

export type AdminCustomerRequest = {
  id: string;
  customer: Customer | null;
  status: CustomerRequestStatus;
  source: CustomerRequestInput["source"];
  customerName: string;
  contact: string;
  vehicle: string;
  requestText: string;
  privacyAccepted: boolean;
  totalEstimateRub: number;
  createdAt: string;
  updatedAt: string;
  items: AdminCustomerRequestItem[];
  events: AdminCustomerRequestEvent[];
};

export type AdminDashboardStats = {
  totalRequests: number;
  newRequests: number;
  inWorkRequests: number;
  doneRequests: number;
  products: number;
  brands: number;
  categories: number;
  customers: number;
  imports: number;
};

export type AdminProduct = Part & {
  isActive: boolean;
  updatedAt: string;
};

export type PriceImportRow = {
  name: string;
  article: string;
  oem?: string;
  brand?: string;
  model?: string;
  category?: string;
  manufacturer?: string;
  price?: number;
  availability?: Part["availability"];
  stock?: string;
  delivery?: string;
};

export type PriceImportResult = {
  id: string;
  importedRows: number;
  skippedRows: number;
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
  is_active: number;
  updated_at?: string;
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

type AdminRequestRow = {
  id: string;
  customer_id: string | null;
  status: CustomerRequestStatus;
  source: CustomerRequestInput["source"];
  customer_name: string;
  contact: string;
  vehicle: string;
  request_text: string;
  privacy_accepted: number;
  total_estimate_rub: number;
  created_at: string;
  updated_at: string;
};

type CustomerRow = {
  id: string;
  display_name: string;
  contact: string;
  normalized_contact: string;
  created_at: string;
  updated_at: string;
};

type AdminRequestItemRow = {
  id: string;
  part_id: string | null;
  part_name: string;
  article: string;
  quantity: number;
  price_snapshot_rub: number;
};

type AdminRequestEventRow = {
  id: string;
  event_type: string;
  note: string;
  created_at: string;
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

export const normalizeContact = (value: string) => {
  const trimmed = value.trim();
  const digits = trimmed.replace(/\D/g, "");

  if (!digits) {
    return normalizeSearch(trimmed);
  }

  if (digits.length === 11 && digits.startsWith("8")) {
    return `7${digits.slice(1)}`;
  }

  return digits;
};

const stableId = (prefix: string, value: string) => {
  const slug = value
    .trim()
    .toLocaleLowerCase("ru-RU")
    .normalize("NFKD")
    .replace(/[^\p{Letter}\p{Number}]+/gu, "-")
    .replace(/^-+|-+$/g, "");

  return `${prefix}-${slug || "item"}`;
};

const slugify = (value: string) =>
  value
    .trim()
    .toLocaleLowerCase("ru-RU")
    .normalize("NFKD")
    .replace(/[^\p{Letter}\p{Number}]+/gu, "-")
    .replace(/^-+|-+$/g, "");

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

const ensureColumn = (db: DatabaseSync, table: string, column: string, definition: string) => {
  const columns = db.prepare(`PRAGMA table_info(${table})`).all() as Array<{ name: string }>;

  if (!columns.some((item) => item.name === column)) {
    db.exec(`ALTER TABLE ${table} ADD COLUMN ${column} ${definition}`);
  }
};

const ensureDatabaseShape = (db: DatabaseSync) => {
  ensureColumn(db, "parts", "is_active", "INTEGER NOT NULL DEFAULT 1");
  ensureColumn(db, "customer_requests", "customer_id", "TEXT REFERENCES customers(id) ON DELETE SET NULL");
  db.exec("CREATE INDEX IF NOT EXISTS idx_parts_active ON parts(is_active)");
  db.exec("CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_normalized_contact ON customers(normalized_contact)");
};

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

  ensureDatabaseShape(db);
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
       is_active, sort_order, updated_at
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, datetime('now'))
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
  const upsertNotificationSettings = db.prepare(
    `INSERT INTO notification_settings (id, manager_email, telegram_chat_id, telegram_bot_token_configured, updated_at)
     VALUES ('default', '', '', 0, datetime('now'))
     ON CONFLICT(id) DO NOTHING`
  );

  db.exec("BEGIN");
  try {
    upsertMeta.run("database_mode", "sqlite-development");
    upsertMeta.run("production_database_target", "postgresql");
    upsertMeta.run("catalog_seed_version", "2026-08-01");
    upsertNotificationSettings.run();
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
    po.stock,
    p.is_active,
    p.updated_at
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
  const where: string[] = ["p.is_active = 1"];
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
    .prepare(`${partSelect} WHERE p.slug = ? AND p.is_active = 1 LIMIT 1`)
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

  return (
    db.prepare("SELECT slug FROM parts WHERE is_active = 1 ORDER BY sort_order, name").all() as Array<{
      slug: string;
    }>
  ).map((part) => part.slug);
};

export const getCatalogSnapshot = (filters: CatalogFilters = {}): CatalogSnapshot => ({
  brands: getBrands(),
  categories: getCategories(),
  parts: getParts(filters)
});

export const createCustomerRequest = (input: CustomerRequestInput) => {
  const db = getDatabase();
  const id = randomUUID();
  const normalizedContact = normalizeContact(input.contact);
  const customerId = `customer:${normalizedContact || randomUUID()}`;
  const items = input.items ?? [];
  const totalEstimateRub = items.reduce(
    (sum, item) => sum + Math.max(0, Math.round(item.price ?? 0)) * Math.max(1, Math.round(item.quantity)),
    0
  );

  const insertRequest = db.prepare(
    `INSERT INTO customer_requests (
       id, customer_id, status, source, customer_name, contact, vehicle, request_text,
       privacy_accepted, total_estimate_rub, created_at, updated_at
     )
     VALUES (?, ?, 'new', ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))`
  );
  const upsertCustomer = db.prepare(
    `INSERT INTO customers (id, display_name, contact, normalized_contact, created_at, updated_at)
     VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
     ON CONFLICT(normalized_contact) DO UPDATE SET
       display_name = excluded.display_name,
       contact = excluded.contact,
       updated_at = datetime('now')`
  );
  const findCustomer = db.prepare("SELECT id FROM customers WHERE normalized_contact = ? LIMIT 1");
  const insertItem = db.prepare(
    `INSERT INTO customer_request_items (
       id, request_id, part_id, part_name, article, quantity, price_snapshot_rub
     )
     VALUES (?, ?, ?, ?, ?, ?, ?)`
  );
  const insertEvent = db.prepare(
    `INSERT INTO customer_request_events (id, request_id, event_type, note, created_at)
     VALUES (?, ?, 'created', ?, datetime('now'))`
  );
  const partExists = db.prepare("SELECT id FROM parts WHERE id = ? LIMIT 1");

  db.exec("BEGIN");
  try {
    upsertCustomer.run(customerId, input.customerName, input.contact, normalizedContact);
    const customer = findCustomer.get(normalizedContact) as { id: string } | undefined;
    insertRequest.run(
      id,
      customer?.id ?? customerId,
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
    insertEvent.run(
      randomUUID(),
      id,
      input.source === "cart" ? "Заявка создана из корзины" : "Заявка создана из формы подбора"
    );

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

const mapAdminRequest = (db: DatabaseSync, row: AdminRequestRow): AdminCustomerRequest => {
  const customerRow = row.customer_id
    ? (db
        .prepare(
          `SELECT id, display_name, contact, normalized_contact, created_at, updated_at
           FROM customers
           WHERE id = ?
           LIMIT 1`
        )
        .get(row.customer_id) as CustomerRow | undefined)
    : undefined;
  const itemRows = db
    .prepare(
      `SELECT id, part_id, part_name, article, quantity, price_snapshot_rub
       FROM customer_request_items
       WHERE request_id = ?
       ORDER BY id`
    )
    .all(row.id) as AdminRequestItemRow[];
  const eventRows = db
    .prepare(
      `SELECT id, event_type, note, created_at
       FROM customer_request_events
       WHERE request_id = ?
       ORDER BY created_at DESC`
    )
    .all(row.id) as AdminRequestEventRow[];

  return {
    id: row.id,
    customer: customerRow
      ? {
          id: customerRow.id,
          displayName: customerRow.display_name,
          contact: customerRow.contact,
          normalizedContact: customerRow.normalized_contact,
          createdAt: customerRow.created_at,
          updatedAt: customerRow.updated_at
        }
      : null,
    status: row.status,
    source: row.source,
    customerName: row.customer_name,
    contact: row.contact,
    vehicle: row.vehicle,
    requestText: row.request_text,
    privacyAccepted: row.privacy_accepted === 1,
    totalEstimateRub: row.total_estimate_rub,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    items: itemRows.map((item) => ({
      id: item.id,
      partId: item.part_id,
      partName: item.part_name,
      article: item.article,
      quantity: item.quantity,
      priceSnapshotRub: item.price_snapshot_rub
    })),
    events: eventRows.map((event) => ({
      id: event.id,
      eventType: event.event_type,
      note: event.note,
      createdAt: event.created_at
    }))
  };
};

export const getAdminCustomerRequests = (status?: string): AdminCustomerRequest[] => {
  const db = getDatabase();
  const normalizedStatus = status?.trim();
  const sql = normalizedStatus
    ? `SELECT id, customer_id, status, source, customer_name, contact, vehicle, request_text, privacy_accepted,
         total_estimate_rub, created_at, updated_at
       FROM customer_requests
       WHERE status = ?
       ORDER BY created_at DESC`
    : `SELECT id, customer_id, status, source, customer_name, contact, vehicle, request_text, privacy_accepted,
         total_estimate_rub, created_at, updated_at
       FROM customer_requests
       ORDER BY created_at DESC`;
  const rows = normalizedStatus
    ? (db.prepare(sql).all(normalizedStatus) as AdminRequestRow[])
    : (db.prepare(sql).all() as AdminRequestRow[]);

  return rows.map((row) => mapAdminRequest(db, row));
};

export const getAdminDashboardStats = (): AdminDashboardStats => {
  const db = getDatabase();
  const count = (sql: string, value?: string) => {
    const row = value
      ? (db.prepare(sql).get(value) as { count: number })
      : (db.prepare(sql).get() as { count: number });
    return row.count;
  };

  return {
    totalRequests: count("SELECT COUNT(*) AS count FROM customer_requests"),
    newRequests: count("SELECT COUNT(*) AS count FROM customer_requests WHERE status = ?", "new"),
    inWorkRequests: count("SELECT COUNT(*) AS count FROM customer_requests WHERE status = ?", "in_work"),
    doneRequests: count("SELECT COUNT(*) AS count FROM customer_requests WHERE status = ?", "done"),
    products: count("SELECT COUNT(*) AS count FROM parts"),
    brands: count("SELECT COUNT(*) AS count FROM brands"),
    categories: count("SELECT COUNT(*) AS count FROM categories"),
    customers: count("SELECT COUNT(*) AS count FROM customers"),
    imports: count("SELECT COUNT(*) AS count FROM price_imports")
  };
};

export const updateCustomerRequestStatus = (
  requestId: string,
  status: CustomerRequestStatus,
  note: string
) => {
  const db = getDatabase();
  const updateRequest = db.prepare(
    `UPDATE customer_requests
     SET status = ?, updated_at = datetime('now')
     WHERE id = ?`
  );
  const insertEvent = db.prepare(
    `INSERT INTO customer_request_events (id, request_id, event_type, note, created_at)
     VALUES (?, ?, 'status_changed', ?, datetime('now'))`
  );

  db.exec("BEGIN");
  try {
    updateRequest.run(status, requestId);
    insertEvent.run(randomUUID(), requestId, note);
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
};

export const getAdminCustomerRequestById = (requestId: string) => {
  const db = getDatabase();
  const row = db
    .prepare(
      `SELECT id, customer_id, status, source, customer_name, contact, vehicle, request_text, privacy_accepted,
         total_estimate_rub, created_at, updated_at
       FROM customer_requests
       WHERE id = ?
       LIMIT 1`
    )
    .get(requestId) as AdminRequestRow | undefined;

  return row ? mapAdminRequest(db, row) : undefined;
};

export const addCustomerRequestComment = (requestId: string, note: string) => {
  const db = getDatabase();
  const trimmedNote = note.trim().slice(0, 1000);

  if (!trimmedNote) {
    return;
  }

  db.prepare(
    `INSERT INTO customer_request_events (id, request_id, event_type, note, created_at)
     VALUES (?, ?, 'comment', ?, datetime('now'))`
  ).run(randomUUID(), requestId, trimmedNote);
};

export const getAdminCustomers = () => {
  const db = getDatabase();
  const rows = db
    .prepare(
      `SELECT id, display_name, contact, normalized_contact, created_at, updated_at
       FROM customers
       ORDER BY updated_at DESC`
    )
    .all() as CustomerRow[];
  const countRequests = db.prepare("SELECT COUNT(*) AS count FROM customer_requests WHERE customer_id = ?");

  return rows.map((row) => ({
    id: row.id,
    displayName: row.display_name,
    contact: row.contact,
    normalizedContact: row.normalized_contact,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    requestsCount: (countRequests.get(row.id) as { count: number }).count
  }));
};

const mapAdminProductRow = (db: DatabaseSync, row: PartRow): AdminProduct => ({
  ...mapPartRow(db, row),
  isActive: row.is_active === 1,
  updatedAt: row.updated_at ?? ""
});

export const getAdminProducts = (query?: string): AdminProduct[] => {
  const db = getDatabase();
  const normalizedQuery = query?.trim();
  const where = normalizedQuery ? "WHERE p.search_text LIKE ?" : "";
  const params = normalizedQuery ? [`%${normalizeSearch(normalizedQuery)}%`] : [];
  const rows = db
    .prepare(`${partSelect} ${where} ORDER BY p.updated_at DESC, p.sort_order, p.name LIMIT 300`)
    .all(...params) as PartRow[];

  return rows.map((row) => mapAdminProductRow(db, row));
};

export const updateProductActivity = (partId: string, isActive: boolean) => {
  const db = getDatabase();
  db.prepare("UPDATE parts SET is_active = ?, updated_at = datetime('now') WHERE id = ?").run(
    isActive ? 1 : 0,
    partId
  );
};

const resolveBrandId = (db: DatabaseSync, nameOrSlug: string) => {
  const value = nameOrSlug.trim();
  const slug = slugify(value);
  const existing = db
    .prepare("SELECT id FROM brands WHERE slug = ? OR name = ? LIMIT 1")
    .get(slug, value) as { id: string } | undefined;

  if (existing) {
    return existing.id;
  }

  const id = slug || stableId("brand", value);
  db.prepare(
    `INSERT INTO brands (id, slug, name, country, sort_order, created_at, updated_at)
     VALUES (?, ?, ?, 'уточнить', 999, datetime('now'), datetime('now'))
     ON CONFLICT(id) DO NOTHING`
  ).run(id, id, value);
  return id;
};

const resolveCategoryId = (db: DatabaseSync, nameOrSlug: string) => {
  const value = nameOrSlug.trim();
  const slug = slugify(value);
  const existing = db
    .prepare("SELECT id FROM categories WHERE slug = ? OR name = ? LIMIT 1")
    .get(slug, value) as { id: string } | undefined;

  if (existing) {
    return existing.id;
  }

  const id = slug || stableId("category", value);
  db.prepare(
    `INSERT INTO categories (id, slug, name, description, sort_order, created_at, updated_at)
     VALUES (?, ?, ?, 'Импортированная категория, описание нужно заполнить.', 999, datetime('now'), datetime('now'))
     ON CONFLICT(id) DO NOTHING`
  ).run(id, id, value);
  return id;
};

const resolveManufacturerId = (db: DatabaseSync, name: string) => {
  const value = name.trim() || "уточнить";
  const id = stableId("manufacturer", value);

  db.prepare(
    `INSERT INTO manufacturers (id, name, created_at, updated_at)
     VALUES (?, ?, datetime('now'), datetime('now'))
     ON CONFLICT(id) DO UPDATE SET name = excluded.name, updated_at = datetime('now')`
  ).run(id, value);
  return id;
};

export const importPriceRows = (filename: string, fileKind: string, rows: PriceImportRow[]): PriceImportResult => {
  const db = getDatabase();
  const importId = randomUUID();
  let importedRows = 0;
  let skippedRows = 0;

  const upsertPart = db.prepare(
    `INSERT INTO parts (
       id, slug, name, category_id, brand_id, model_name, manufacturer_id, condition, quality,
       description, primary_oem, primary_article, search_text, is_active, sort_order, created_at, updated_at
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, 'новая', 'заводской аналог', ?, ?, ?, ?, 1, 999, datetime('now'), datetime('now'))
     ON CONFLICT(id) DO UPDATE SET
       name = excluded.name,
       category_id = excluded.category_id,
       brand_id = excluded.brand_id,
       model_name = excluded.model_name,
       manufacturer_id = excluded.manufacturer_id,
       description = excluded.description,
       primary_oem = excluded.primary_oem,
       primary_article = excluded.primary_article,
       search_text = excluded.search_text,
       updated_at = datetime('now')`
  );
  const clearOffers = db.prepare("DELETE FROM price_offers WHERE part_id = ?");
  const upsertNumber = db.prepare(
    `INSERT INTO part_numbers (id, part_id, kind, value, normalized_value, sort_order)
     VALUES (?, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET value = excluded.value, normalized_value = excluded.normalized_value`
  );
  const insertOffer = db.prepare(
    `INSERT INTO price_offers (
       id, part_id, supplier_id, price_rub, availability, delivery, stock, is_primary, updated_at
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, 1, datetime('now'))`
  );
  const insertImport = db.prepare(
    `INSERT INTO price_imports (id, filename, file_kind, imported_rows, skipped_rows, created_at)
     VALUES (?, ?, ?, ?, ?, datetime('now'))`
  );

  db.exec("BEGIN");
  try {
    rows.forEach((row) => {
      const name = row.name.trim();
      const article = row.article.trim();

      if (!name || !article) {
        skippedRows += 1;
        return;
      }

      const brandId = resolveBrandId(db, row.brand || "Zemazap");
      const categoryId = resolveCategoryId(db, row.category || "Импорт");
      const manufacturerId = resolveManufacturerId(db, row.manufacturer || "уточнить");
      const partId = `import:${normalizePartNumber(article) || slugify(name)}`;
      const slug = slugify(`${article}-${name}`).slice(0, 90) || partId.replace(":", "-");
      const oem = row.oem?.trim() || article;
      const model = row.model?.trim() || "уточнить";
      const price = Math.max(0, Math.round(row.price ?? 0));
      const availability = row.availability || "уточнить";
      const stock = row.stock?.trim() || "уточнить";
      const delivery = row.delivery?.trim() || "Срок и наличие подтверждает менеджер";
      const searchText = normalizeSearch(
        [name, article, oem, row.brand, model, row.category, row.manufacturer, normalizePartNumber(article), normalizePartNumber(oem)]
          .filter(Boolean)
          .join(" ")
      );

      upsertPart.run(
        partId,
        slug,
        name,
        categoryId,
        brandId,
        model,
        manufacturerId,
        "Импортированная позиция. Описание, применимость и гарантию нужно уточнить.",
        oem,
        article,
        searchText
      );
      upsertNumber.run(`${partId}:article`, partId, "article", article, normalizePartNumber(article), 0);
      upsertNumber.run(`${partId}:oem`, partId, "oem", oem, normalizePartNumber(oem), 1);
      clearOffers.run(partId);
      insertOffer.run(`${partId}:primary-offer`, partId, DEMO_SUPPLIER_ID, price, availability, delivery, stock);
      importedRows += 1;
    });

    insertImport.run(importId, filename, fileKind, importedRows, skippedRows);
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }

  return { id: importId, importedRows, skippedRows };
};
