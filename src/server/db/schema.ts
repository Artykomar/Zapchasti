export const schemaStatements = [
  `CREATE TABLE IF NOT EXISTS database_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE TABLE IF NOT EXISTS brands (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE TABLE IF NOT EXISTS car_models (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    years TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (brand_id, slug)
  )`,
  `CREATE TABLE IF NOT EXISTS model_generations (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES car_models(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
  )`,
  `CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE TABLE IF NOT EXISTS manufacturers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE TABLE IF NOT EXISTS suppliers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'demo',
    contact_note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE TABLE IF NOT EXISTS parts (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category_id TEXT NOT NULL REFERENCES categories(id),
    brand_id TEXT NOT NULL REFERENCES brands(id),
    model_name TEXT NOT NULL,
    manufacturer_id TEXT NOT NULL REFERENCES manufacturers(id),
    condition TEXT NOT NULL,
    quality TEXT NOT NULL,
    description TEXT NOT NULL,
    primary_oem TEXT NOT NULL,
    primary_article TEXT NOT NULL,
    search_text TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE TABLE IF NOT EXISTS part_numbers (
    id TEXT PRIMARY KEY,
    part_id TEXT NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    value TEXT NOT NULL,
    normalized_value TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
  )`,
  `CREATE TABLE IF NOT EXISTS part_compatibility (
    id TEXT PRIMARY KEY,
    part_id TEXT NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
  )`,
  `CREATE TABLE IF NOT EXISTS part_specs (
    id TEXT PRIMARY KEY,
    part_id TEXT NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
  )`,
  `CREATE TABLE IF NOT EXISTS price_offers (
    id TEXT PRIMARY KEY,
    part_id TEXT NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    supplier_id TEXT NOT NULL REFERENCES suppliers(id),
    price_rub INTEGER NOT NULL,
    availability TEXT NOT NULL,
    delivery TEXT NOT NULL,
    stock TEXT NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE TABLE IF NOT EXISTS customer_requests (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'new',
    source TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    contact TEXT NOT NULL,
    vehicle TEXT NOT NULL DEFAULT '',
    request_text TEXT NOT NULL DEFAULT '',
    privacy_accepted INTEGER NOT NULL DEFAULT 0,
    total_estimate_rub INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE TABLE IF NOT EXISTS customer_request_items (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES customer_requests(id) ON DELETE CASCADE,
    part_id TEXT REFERENCES parts(id) ON DELETE SET NULL,
    part_name TEXT NOT NULL,
    article TEXT NOT NULL DEFAULT '',
    quantity INTEGER NOT NULL DEFAULT 1,
    price_snapshot_rub INTEGER NOT NULL DEFAULT 0
  )`,
  `CREATE TABLE IF NOT EXISTS customer_request_events (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES customer_requests(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`,
  `CREATE UNIQUE INDEX IF NOT EXISTS idx_brands_slug ON brands(slug)`,
  `CREATE INDEX IF NOT EXISTS idx_car_models_brand ON car_models(brand_id, slug)`,
  `CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug)`,
  `CREATE UNIQUE INDEX IF NOT EXISTS idx_parts_slug ON parts(slug)`,
  `CREATE INDEX IF NOT EXISTS idx_parts_brand_category ON parts(brand_id, category_id)`,
  `CREATE INDEX IF NOT EXISTS idx_parts_condition ON parts(condition)`,
  `CREATE INDEX IF NOT EXISTS idx_parts_search_text ON parts(search_text)`,
  `CREATE INDEX IF NOT EXISTS idx_part_numbers_value ON part_numbers(normalized_value)`,
  `CREATE INDEX IF NOT EXISTS idx_price_offers_part_primary ON price_offers(part_id, is_primary)`,
  `CREATE INDEX IF NOT EXISTS idx_customer_requests_status_created ON customer_requests(status, created_at)`,
  `CREATE INDEX IF NOT EXISTS idx_customer_request_events_request ON customer_request_events(request_id, created_at)`
];
