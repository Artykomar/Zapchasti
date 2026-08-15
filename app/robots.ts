import type { MetadataRoute } from "next";
import { getCanonicalUrl, siteConfig } from "@/src/server/siteConfig";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: siteConfig.indexingAllowed
      ? [{ userAgent: "*", allow: "/" }]
      : [{ userAgent: "*", disallow: "/" }],
    sitemap: getCanonicalUrl("/sitemap.xml")
  };
}
