import type { Metadata } from "next";
import "./globals.css";
import { siteConfig } from "@/src/server/siteConfig";

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.siteUrl),
  title: `${siteConfig.brandName} | Мультибрендовые автозапчасти`,
  description:
    `${siteConfig.brandName}: интернет-витрина для поиска автозапчастей по номеру, артикулу, марке, модели и категории.`,
  alternates: {
    canonical: "/"
  },
  openGraph: {
    title: `${siteConfig.brandName} | Мультибрендовые автозапчасти`,
    description:
      "Каталог, корзина-заявка и ручное подтверждение менеджером перед оплатой.",
    url: siteConfig.siteUrl,
    siteName: siteConfig.brandName,
    locale: "ru_RU",
    type: "website"
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
