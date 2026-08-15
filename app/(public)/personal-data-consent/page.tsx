import { siteConfig } from "@/src/server/siteConfig";

export default function PersonalDataConsentPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Согласие на обработку персональных данных</p>
        <h1>Согласие для заявок и корзины-заявки</h1>
        <p>
          Версия согласия: {siteConfig.privacyConsentVersion}. Финальный юридический текст должен
          быть утвержден после выбора продавца, домена и способов связи.
        </p>
      </section>

      <section className="legal-text">
        <h2>Что фиксируется при отправке заявки</h2>
        <ul>
          <li>имя, телефон или мессенджер, данные автомобиля и текст запроса;</li>
          <li>состав корзины-заявки, если заявка отправлена из корзины;</li>
          <li>версия согласия, дата и технический источник формы;</li>
          <li>IP-адрес и user-agent после подключения production-режима хранения согласий.</li>
        </ul>
        <p>
          Маркетинговые рассылки не включены в это согласие. Для них потребуется отдельная галочка и
          отдельный текст.
        </p>
      </section>
    </main>
  );
}
