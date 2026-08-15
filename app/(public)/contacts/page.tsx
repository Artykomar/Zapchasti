import Link from "next/link";
import { Clock, Mail, MapPin, MessageCircle, Phone } from "lucide-react";
import TwoGisMap from "@/src/components/TwoGisMap";
import { hasPublicLegalEntity, siteConfig } from "@/src/server/siteConfig";

export default function ContactsPage() {
  const legalReady = hasPublicLegalEntity();
  const mapCenter: [number, number] = [siteConfig.mapLongitude, siteConfig.mapLatitude];

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Контакты {siteConfig.brandName}</p>
        <h1>Контакты магазина управляются из единого launch-контракта</h1>
        <p>
          Перед production здесь должны быть реальные телефон, почта, MAX, адрес склада и
          юридические реквизиты. Пока используются безопасные значения по умолчанию.
        </p>
      </section>

      <section className="contact-grid">
        <div className="contact-item">
          <Phone size={24} aria-hidden="true" />
          <h2>Телефон</h2>
          <p>
            <a href={`tel:${siteConfig.phoneHref}`}>{siteConfig.phoneLabel}</a>
          </p>
        </div>
        <div className="contact-item">
          <Mail size={24} aria-hidden="true" />
          <h2>Email</h2>
          <p>
            <a href={`mailto:${siteConfig.publicEmail}`}>{siteConfig.publicEmail}</a>
          </p>
        </div>
        <div className="contact-item">
          <MessageCircle size={24} aria-hidden="true" />
          <h2>MAX</h2>
          <p>
            {siteConfig.maxUrl ? (
              <a href={siteConfig.maxUrl}>Написать в MAX</a>
            ) : (
              "Ссылка MAX будет добавлена после выбора рабочего аккаунта."
            )}
          </p>
        </div>
        <div className="contact-item">
          <Clock size={24} aria-hidden="true" />
          <h2>График</h2>
          <p>{siteConfig.businessHours}</p>
        </div>
      </section>

      <section className="contact-wide">
        <div>
          <MapPin size={26} aria-hidden="true" />
          <h2>Склад и выдача</h2>
          <p>
            {siteConfig.address ||
              "Адрес, схема проезда и карта появятся после выбора города. Для доставки можно будет оставить пункт выдачи или адрес транспортной компании в заявке."}
          </p>
        </div>
        <Link className="secondary-action" href="/request">
          Оставить заявку
        </Link>
      </section>

      <TwoGisMap
        address={siteConfig.mapAddress}
        apiKey={siteConfig.twoGisMapglKey}
        center={mapCenter}
        mapUrl={siteConfig.twoGisMapUrl}
        zoom={siteConfig.mapZoom}
      />

      <section className="legal-text">
        <h2>Реквизиты продавца</h2>
        {legalReady ? (
          <ul>
            <li>Продавец: {siteConfig.legalName}</li>
            <li>ИНН: {siteConfig.legalInn}</li>
            <li>ОГРН/ОГРНИП: {siteConfig.legalOgrn || "будет указан после финализации"}</li>
            {siteConfig.legalKpp ? <li>КПП: {siteConfig.legalKpp}</li> : null}
            {siteConfig.legalAddress ? <li>Юридический адрес: {siteConfig.legalAddress}</li> : null}
            <li>Email для претензий: {siteConfig.claimsEmail}</li>
          </ul>
        ) : (
          <p>
            Реквизиты продавца не заполнены. Реальные платежи и банк-проверку нельзя включать до
            подтверждения ИП/ООО, ИНН, домена и юридических текстов.
          </p>
        )}
      </section>
    </main>
  );
}
