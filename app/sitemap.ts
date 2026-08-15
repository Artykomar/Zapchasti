import type { MetadataRoute } from "next";
import { getCanonicalUrl } from "@/src/server/siteConfig";

const routes = [
  "/",
  "/catalog",
  "/shop",
  "/cart",
  "/request",
  "/delivery",
  "/contacts",
  "/about",
  "/reviews",
  "/privacy-policy",
  "/personal-data-consent",
  "/terms"
];

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: getCanonicalUrl(route),
    lastModified: new Date("2026-08-15")
  }));
}
