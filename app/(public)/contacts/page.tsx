import Link from "next/link";
import { Clock, Mail, MapPin, MessageCircle, Phone } from "lucide-react";

export default function ContactsPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Контакты Zemazap</p>
        <h1>Контакты магазина будут заполнены перед запуском</h1>
        <p>
          Страница готова под реальные телефон, почту, мессенджеры, адрес склада и юридические
          реквизиты. Пока здесь стоят безопасные заглушки, чтобы не публиковать случайные данные.
        </p>
      </section>

      <section className="contact-grid">
        <div className="contact-item">
          <Phone size={24} aria-hidden="true" />
          <h2>Телефон</h2>
          <p>+7 (000) 000-00-00</p>
        </div>
        <div className="contact-item">
          <Mail size={24} aria-hidden="true" />
          <h2>Email</h2>
          <p>orders@example.ru</p>
        </div>
        <div className="contact-item">
          <MessageCircle size={24} aria-hidden="true" />
          <h2>Мессенджеры</h2>
          <p>Telegram и WhatsApp будут добавлены после выбора рабочих номеров.</p>
        </div>
        <div className="contact-item">
          <Clock size={24} aria-hidden="true" />
          <h2>График</h2>
          <p>Будет задан после подтверждения региона и формата склада.</p>
        </div>
      </section>

      <section className="contact-wide">
        <div>
          <MapPin size={26} aria-hidden="true" />
          <h2>Склад и выдача</h2>
          <p>
            Адрес, схема проезда и карта появятся после выбора города. Для доставки можно будет
            оставить пункт выдачи или адрес транспортной компании в заявке.
          </p>
        </div>
        <Link className="secondary-action" href="/request">
          Оставить заявку
        </Link>
      </section>

      <section className="map-placeholder" aria-label="Карта">
        <span>Карта будет подключена после выбора адреса</span>
      </section>
    </main>
  );
}
