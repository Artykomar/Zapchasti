import Link from "next/link";
import { Clock, Heart, MapPin, MessageCircle, Phone } from "lucide-react";
import HeaderCartLink from "@/src/components/HeaderCartLink";
import { hasPublicLegalEntity, siteConfig } from "@/src/server/siteConfig";

// Public contacts, legal details and feature flags are injected at container runtime.
// Rendering this segment per request prevents Docker build-time placeholders from
// being frozen into otherwise static pages.
export const dynamic = "force-dynamic";

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
  const organizationJsonLd = hasPublicLegalEntity()
    ? {
        "@context": "https://schema.org",
        "@type": "AutoPartsStore",
        name: siteConfig.legalName,
        url: siteConfig.siteUrl,
        telephone: siteConfig.phoneLabel,
        email: siteConfig.publicEmail,
        address: siteConfig.actualAddress || siteConfig.address,
        taxID: siteConfig.legalInn
      }
    : null;

  return (
    <>
      {organizationJsonLd ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(organizationJsonLd).replace(/</g, "\\u003c")
          }}
        />
      ) : null}
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
          {siteConfig.maxUrl ? (
            <a className="topline__item" href={siteConfig.maxUrl}>
              <MessageCircle size={16} aria-hidden="true" />
              <span>MAX</span>
            </a>
          ) : null}
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
          {siteConfig.maxUrl ? <a href={siteConfig.maxUrl}>MAX</a> : null}
        </div>
      </footer>
    </>
  );
}
