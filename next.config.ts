import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  allowedDevOrigins: ["127.0.0.1", "localhost"],
  reactStrictMode: true,
  async headers() {
    const productionHeaders = process.env.NODE_ENV === "production"
      ? [
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "base-uri 'self'",
              "object-src 'none'",
              "frame-ancestors 'none'",
              "form-action 'self' https://pay.alfabank.ru https://alfa.rbsuat.com",
              "script-src 'self' 'unsafe-inline' https://mapgl.2gis.com",
              "style-src 'self' 'unsafe-inline' https://mapgl.2gis.com",
              "img-src 'self' data: blob: https://*.2gis.com",
              "font-src 'self' data:",
              "connect-src 'self' https://*.2gis.com",
              "upgrade-insecure-requests"
            ].join("; ")
          }
        ]
      : [];
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(), payment=()"
          },
          ...productionHeaders
        ]
      }
    ];
  }
};

export default nextConfig;
