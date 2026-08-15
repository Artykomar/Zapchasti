import Link from "next/link";
import { siteConfig } from "@/src/server/siteConfig";

export default function PrivacyPolicyPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Документы</p>
        <h1>Политика обработки персональных данных</h1>
        <p>
          Версия политики: {siteConfig.privacyPolicyVersion}. Это техническая заготовка под реальные
          реквизиты продавца, домен, формы сайта, платежного провайдера и способы связи.
        </p>
      </section>

      <section className="legal-text">
        <h2>Что нужно заполнить</h2>
        <ul>
          <li>полное наименование продавца и реквизиты;</li>
          <li>адрес сайта и домен;</li>
          <li>цели обработки заявок, звонков и заказов;</li>
          <li>перечень передаваемых данных платежному провайдеру и службам доставки;</li>
          <li>сроки хранения данных и контакты для удаления.</li>
        </ul>
        <p>
          Отдельный текст согласия находится на странице{" "}
          <Link href="/personal-data-consent">согласия на обработку персональных данных</Link>, а
          условия заказа вынесены в <Link href="/terms">публичные условия заказа</Link>.
        </p>
      </section>
    </main>
  );
}
