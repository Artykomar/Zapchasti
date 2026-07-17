import type { Metadata } from "next";
import Link from "next/link";
import { Clock, MapPin, MessageCircle, Phone, ShoppingCart } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Заводские автозапчасти | MVP витрина",
  description: "MVP интернет-витрины для подбора новых заводских автозапчастей по OEM, артикулу, авто или VIN."
};

const navItems = [
  { href: "/catalog", label: "Автозапчасти" },
  { href: "/catalog#tires", label: "Шины и диски" },
  { href: "/request", label: "Заявка" },
  { href: "/contacts", label: "Контакты" }
];

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>
        <header className="site-header">
          <div className="topline">
            <div className="topline__item">
              <MapPin size={16} aria-hidden="true" />
              <span>Регион работы уточняется</span>
            </div>
            <div className="topline__item">
              <Clock size={16} aria-hidden="true" />
              <span>Пн-Сб, график будет задан</span>
            </div>
            <a className="topline__item" href="tel:+70000000000">
              <Phone size={16} aria-hidden="true" />
              <span>+7 (000) 000-00-00</span>
            </a>
            <a className="topline__item" href="/request">
              <MessageCircle size={16} aria-hidden="true" />
              <span>Подбор по VIN</span>
            </a>
          </div>

          <div className="mainnav">
            <Link className="brand" href="/" aria-label="На главную">
              <span className="brand__mark">OEM</span>
              <span>
                <strong>Заводские запчасти</strong>
                <small>MVP витрина</small>
              </span>
            </Link>

            <nav className="mainnav__links" aria-label="Основная навигация">
              {navItems.map((item) => (
                <Link key={item.href} href={item.href}>
                  {item.label}
                </Link>
              ))}
            </nav>

            <Link className="cart-link" href="/request">
              <ShoppingCart size={18} aria-hidden="true" />
              <span>Корзина-заявка</span>
            </Link>
          </div>
        </header>

        {children}

        <footer className="site-footer">
          <div>
            <strong>Заводские запчасти</strong>
            <p>Новые детали, OEM-номера, заводские аналоги и ручное подтверждение применимости.</p>
          </div>
          <div className="site-footer__links">
            <Link href="/catalog">Каталог</Link>
            <Link href="/request">Оформить заявку</Link>
            <Link href="/contacts">Контакты</Link>
          </div>
        </footer>
      </body>
    </html>
  );
}
