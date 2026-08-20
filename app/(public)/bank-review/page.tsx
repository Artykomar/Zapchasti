import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { hasPublicLegalEntity, siteConfig } from "@/src/server/siteConfig";

export const metadata: Metadata = {
  title: "Информация для проверки банка | Zemazap",
  robots: { index: false, follow: false }
};

export default function BankReviewPage() {
  if (!hasPublicLegalEntity() || !siteConfig.actualAddress || !siteConfig.legalOgrn) {
    notFound();
  }

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Информация для банковской проверки</p>
        <h1>{siteConfig.legalName}</h1>
        <p>Публичная сводка продавца, контактов и условий интернет-магазина.</p>
      </section>
      <section className="legal-text">
        <h2>Реквизиты и контакты</h2>
        <ul>
          <li>ИНН: {siteConfig.legalInn}</li>
          <li>ОГРН/ОГРНИП: {siteConfig.legalOgrn}</li>
          {siteConfig.legalKpp ? <li>КПП: {siteConfig.legalKpp}</li> : null}
          <li>Юридический адрес: {siteConfig.legalAddress}</li>
          <li>Фактический адрес: {siteConfig.actualAddress}</li>
          <li>Телефон: <a href={`tel:${siteConfig.phoneHref}`}>{siteConfig.phoneLabel}</a></li>
          <li>Email: <a href={`mailto:${siteConfig.publicEmail}`}>{siteConfig.publicEmail}</a></li>
          <li>Email для претензий: <a href={`mailto:${siteConfig.claimsEmail}`}>{siteConfig.claimsEmail}</a></li>
        </ul>
      </section>
      <section className="legal-text">
        <h2>Публичные условия</h2>
        <ul>
          <li><Link href="/delivery">Доставка, оплата, гарантия и возврат</Link></li>
          <li><Link href="/terms">Условия заказа</Link></li>
          <li><Link href="/privacy-policy">Политика персональных данных</Link></li>
          <li><Link href="/personal-data-consent">Согласие на обработку ПДн</Link></li>
          <li><Link href="/catalog">Описание товаров и каталог</Link></li>
          <li><Link href="/contacts">Контакты и схема проезда</Link></li>
        </ul>
      </section>
    </main>
  );
}
