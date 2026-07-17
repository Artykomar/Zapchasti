import { Clock, Mail, MapPin, Phone } from "lucide-react";

export default function ContactsPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Контакты</p>
        <h1>Данные магазина будут уточнены</h1>
        <p>
          Эта страница оставлена как рабочая заготовка: после выбора города, адреса, телефона и почты
          данные попадут в шапку, футер, микроразметку и формы заявок.
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
          <MapPin size={24} aria-hidden="true" />
          <h2>Регион</h2>
          <p>Город и адрес нужно выбрать</p>
        </div>
        <div className="contact-item">
          <Clock size={24} aria-hidden="true" />
          <h2>График</h2>
          <p>Будет задан после этапа требований</p>
        </div>
      </section>

      <section className="map-placeholder" aria-label="Карта">
        <span>Карта будет подключена после выбора адреса</span>
      </section>
    </main>
  );
}
