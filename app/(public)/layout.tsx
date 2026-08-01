import Link from "next/link";
import { Clock, Heart, MapPin, MessageCircle, Phone, ShoppingCart } from "lucide-react";

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
            <span>Подбор по артикулу</span>
          </a>
        </div>

        <div className="mainnav">
          <Link className="brand" href="/" aria-label="На главную">
            <img className="brand__logo" src="/zemazap-logo.svg" alt="Zemazap" />
            <span>
              <strong>Zemazap</strong>
              <small>автозапчасти под заказ</small>
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
            <Link className="cart-link" href="/cart">
              <ShoppingCart size={18} aria-hidden="true" />
              <span>Корзина</span>
            </Link>
          </div>
        </div>
      </header>

      {children}

      <footer className="site-footer">
        <div>
          <strong>Zemazap</strong>
          <p>Мультибрендовые автозапчасти, поиск по номеру, карточки товаров и заказ через подтверждение менеджера.</p>
        </div>
        <div className="site-footer__links">
          <Link href="/catalog">Каталог</Link>
          <Link href="/cart">Корзина</Link>
          <Link href="/delivery">Доставка</Link>
          <Link href="/privacy-policy">Документы</Link>
          <Link href="/contacts">Контакты</Link>
        </div>
      </footer>
    </>
  );
}
