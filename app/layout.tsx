import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zemazap | Мультибрендовые автозапчасти",
  description:
    "Zemazap: интернет-витрина для поиска автозапчастей по номеру, артикулу, марке, модели и категории."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
