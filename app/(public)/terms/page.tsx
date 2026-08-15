import { siteConfig, hasPublicLegalEntity } from "@/src/server/siteConfig";

export default function TermsPage() {
  const legalReady = hasPublicLegalEntity();

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Условия заказа</p>
        <h1>Публичные условия заказа и оплаты</h1>
        <p>
          Версия условий: {siteConfig.termsVersion}. До подключения эквайринга заказ остается
          заявкой, а финальную цену, срок, доставку и применимость подтверждает менеджер.
        </p>
      </section>

      <section className="legal-text">
        <h2>Реквизиты продавца</h2>
        {legalReady ? (
          <ul>
            <li>Продавец: {siteConfig.legalName}</li>
            <li>ИНН: {siteConfig.legalInn}</li>
            <li>ОГРН/ОГРНИП: {siteConfig.legalOgrn || "будет указан после финализации"}</li>
            {siteConfig.legalKpp ? <li>КПП: {siteConfig.legalKpp}</li> : null}
            {siteConfig.legalAddress ? <li>Юридический адрес: {siteConfig.legalAddress}</li> : null}
            {siteConfig.bankName ? <li>Банк: {siteConfig.bankName}</li> : null}
            {siteConfig.bankAccount ? <li>Расчетный счет: {siteConfig.bankAccount}</li> : null}
            {siteConfig.bankBik ? <li>БИК: {siteConfig.bankBik}</li> : null}
            <li>Налоги/НДС: {siteConfig.vatLabel}</li>
            <li>Email для претензий: {siteConfig.claimsEmail}</li>
          </ul>
        ) : (
          <p>
            Реквизиты продавца еще не опубликованы. Production и реальные платежи нельзя включать,
            пока владелец бизнеса не подтвердит ИП/ООО, ИНН, договоры и юридические тексты.
          </p>
        )}
      </section>

      <section className="legal-text">
        <h2>Оплата и подтверждение</h2>
        <p>
          Онлайн-оплата будет доступна только для подтвержденного заказа. Сайт не должен принимать и
          хранить номер карты, CVV, срок действия карты или другие карточные данные.
        </p>
      </section>
    </main>
  );
}
