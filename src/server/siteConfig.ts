const cleanUrl = (value: string | undefined, fallback: string) => {
  const candidate = (value || fallback).trim().replace(/\/+$/, "");
  try {
    return new URL(candidate).toString().replace(/\/+$/, "");
  } catch {
    return fallback;
  }
};

const envFlag = (name: string, fallback = false) => {
  const value = process.env[name];
  if (value === undefined) {
    return fallback;
  }
  return ["1", "true", "yes", "on"].includes(value.trim().toLowerCase());
};

const envNumber = (name: string, fallback: number) => {
  const value = Number.parseFloat(process.env[name] || "");
  return Number.isFinite(value) ? value : fallback;
};

const defaultAddress = "Москва, Лубянская площадь";
const configuredAddress = process.env.ZEMAZAP_ADDRESS || defaultAddress;
const mapAddress = process.env.ZEMAZAP_2GIS_MAP_ADDRESS || configuredAddress;
const defaultTwoGisMapUrl = `https://2gis.ru/moscow/search/${encodeURIComponent(mapAddress)}`;

export const siteConfig = {
  brandName: process.env.ZEMAZAP_BRAND_NAME || "Zemazap",
  tagline: process.env.ZEMAZAP_TAGLINE || "автозапчасти под заказ",
  siteUrl: cleanUrl(process.env.ZEMAZAP_SITE_URL, "http://127.0.0.1:3000"),
  indexingAllowed: envFlag("ZEMAZAP_INDEXING_ALLOWED", false),
  region: process.env.ZEMAZAP_REGION || "Регион работы уточняется",
  businessHours: process.env.ZEMAZAP_BUSINESS_HOURS || "Пн-Сб, график будет задан",
  address: configuredAddress,
  mapAddress,
  mapLatitude: envNumber("ZEMAZAP_2GIS_LATITUDE", 55.7596),
  mapLongitude: envNumber("ZEMAZAP_2GIS_LONGITUDE", 37.6263),
  mapZoom: envNumber("ZEMAZAP_2GIS_ZOOM", 15),
  twoGisMapUrl: cleanUrl(process.env.ZEMAZAP_2GIS_MAP_URL, defaultTwoGisMapUrl),
  twoGisMapglKey:
    process.env.ZEMAZAP_2GIS_MAPGL_KEY || process.env.NEXT_PUBLIC_2GIS_MAPGL_KEY || "",
  phoneLabel: process.env.ZEMAZAP_PUBLIC_PHONE_LABEL || "+7 (000) 000-00-00",
  phoneHref: process.env.ZEMAZAP_PUBLIC_PHONE_HREF || "+70000000000",
  publicEmail: process.env.ZEMAZAP_PUBLIC_EMAIL || "orders@example.ru",
  maxUrl: envFlag("MAX_ENABLED", false) ? process.env.ZEMAZAP_MAX_URL || "" : "",
  sellerProfile: process.env.ZEMAZAP_SELLER_PROFILE || "unknown",
  legalName: process.env.ZEMAZAP_LEGAL_NAME || "",
  legalInn: process.env.ZEMAZAP_LEGAL_INN || "",
  legalOgrn: process.env.ZEMAZAP_LEGAL_OGRN || "",
  legalKpp: process.env.ZEMAZAP_LEGAL_KPP || "",
  legalAddress: process.env.ZEMAZAP_LEGAL_ADDRESS || "",
  actualAddress: process.env.ZEMAZAP_ACTUAL_ADDRESS || "",
  claimsEmail: process.env.ZEMAZAP_CLAIMS_EMAIL || process.env.ZEMAZAP_PUBLIC_EMAIL || "orders@example.ru",
  bankName: process.env.ZEMAZAP_BANK_NAME || "",
  bankAccount: process.env.ZEMAZAP_BANK_ACCOUNT || "",
  bankBik: process.env.ZEMAZAP_BANK_BIK || "",
  taxMode: process.env.ZEMAZAP_TAX_MODE || "unknown",
  vatLabel: process.env.ZEMAZAP_VAT_LABEL || "НДС не задан",
  privacyPolicyVersion: process.env.ZEMAZAP_PRIVACY_POLICY_VERSION || "draft-2026-08-15",
  privacyConsentVersion: process.env.ZEMAZAP_PRIVACY_CONSENT_VERSION || "draft-2026-08-15",
  termsVersion: process.env.ZEMAZAP_TERMS_VERSION || "draft-2026-08-15",
  paymentsEnabled: envFlag("PAYMENTS_ENABLED", false),
  paymentsProvider: process.env.PAYMENTS_PROVIDER || "alfa",
  paymentsMode: process.env.PAYMENTS_MODE || "test",
  fiscalizationEnabled: envFlag("FISCALIZATION_ENABLED", false),
  analyticsEnabled: envFlag("ANALYTICS_ENABLED", false)
};

export const getCanonicalUrl = (path = "/") => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${siteConfig.siteUrl}${normalizedPath}`;
};

export const hasPublicLegalEntity = () =>
  siteConfig.sellerProfile !== "unknown" && Boolean(siteConfig.legalName && siteConfig.legalInn);
