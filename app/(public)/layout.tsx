import Link from "next/link";
import { Clock, Heart, MapPin, MessageCircle, Phone } from "lucide-react";
import HeaderCartLink from "@/src/components/HeaderCartLink";
import { siteConfig } from "@/src/server/siteConfig";

const navItems = [
  { href: "/catalog", label: "Каталог" },
  { href: "/about", label: "О компании" },
  { href: "/reviews", label: "Отзывы" },
  { href: "/delivery", label: "Доставка" },
  { href: "/contacts", label: "Контакты" }
];

export default function PublicLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <header className="site-header">
        <div className="topline">
          <div className="topline__item">
            <MapPin size={16} aria-hidden="true" />
            <span>{siteConfig.region}</span>
          </div>
          <div className="topline__item">
            <Clock size={16} aria-hidden="true" />
            <span>{siteConfig.businessHours}</span>
          </div>
          <a className="topline__item" href={`tel:${siteConfig.phoneHref}`}>
            <Phone size={16} aria-hidden="true" />
            <span>{siteConfig.phoneLabel}</span>
          </a>
          <a className="topline__item" href="/request">
            <MessageCircle size={16} aria-hidden="true" />
            <span>Подбор по артикулу</span>
          </a>
        </div>

        <div className="mainnav">
          <Link className="brand" href="/" aria-label="На главную">
            <img className="brand__logo" src="/zemazap-logo.svg" alt={siteConfig.brandName} />
            <span>
              <strong>{siteConfig.brandName}</strong>
              <small>{siteConfig.tagline}</small>
            </span>
          </Link>

          <nav className="mainnav__links" aria-label="Основная навигация">
            {navItems.map((item) => (
              <Link key={item.href} href={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="header-actions">
            <Link className="icon-link" href="/izbrannoe" aria-label="Избранное">
              <Heart size={18} aria-hidden="true" />
            </Link>
            <HeaderCartLink />
          </div>
        </div>
      </header>

      {children}

      <footer className="site-footer">
        <div>
          <strong>{siteConfig.brandName}</strong>
          <p>Мультибрендовые автозапчасти, поиск по номеру, карточки товаров и заказ через подтверждение менеджера.</p>
        </div>
        <div className="site-footer__links">
          <Link href="/catalog">Каталог</Link>
          <Link href="/cart">Корзина</Link>
          <Link href="/delivery">Доставка</Link>
          <Link href="/terms">Условия заказа</Link>
          <Link href="/privacy-policy">Политика ПДн</Link>
          <Link href="/personal-data-consent">Согласие ПДн</Link>
          <Link href="/contacts">Контакты</Link>
        </div>
      </footer>
    </>
  );
}
