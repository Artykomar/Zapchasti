import Link from "next/link";
import { CheckCircle2, PackageSearch, ShieldCheck, Truck } from "lucide-react";

const values = [
  "не копировать чужие базы и фото, а строить собственный каталог",
  "подтверждать состояние, применимость и срок до оплаты",
  "начать с ручной обработки заявок и перейти к API после выбора инфраструктуры",
  "держать сайт готовым к российскому домену, платежам и юридическим страницам"
];

export default function AboutPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">О компании</p>
        <h1>Zemazap как магазин автозапчастей с подтверждением менеджера</h1>
        <p>
          Эта страница фиксирует рабочую модель проекта: мультибрендовый каталог, поиск по номеру
          детали, карточки товаров, резерв через корзину и ручная проверка перед сделкой.
        </p>
      </section>

      <section className="info-grid">
        <article className="info-panel">
          <PackageSearch size={26} aria-hidden="true" />
          <h2>Каталог</h2>
          <p>Марки, модели, категории, артикулы, аналоги, состояние и сроки поставки.</p>
        </article>
        <article className="info-panel">
          <ShieldCheck size={26} aria-hidden="true" />
          <h2>Проверка</h2>
          <p>Перед заказом менеджер сверяет номер, фото, комплектность, наличие и гарантию.</p>
        </article>
        <article className="info-panel">
          <Truck size={26} aria-hidden="true" />
          <h2>Доставка</h2>
          <p>Самовывоз, курьерская доставка и транспортные компании будут настроены после выбора региона.</p>
        </article>
      </section>

      <section className="workspace workspace--split">
        <div>
          <div className="section-heading">
            <p className="eyebrow">Принципы MVP</p>
            <h2>Что уже можно показывать партнеру</h2>
          </div>
          <ul className="check-list">
            {values.map((item) => (
              <li key={item}>
                <CheckCircle2 size={20} aria-hidden="true" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <aside className="process-panel">
          <h3>Следующий слой</h3>
          <p>
            После выбора домена, платежного провайдера и политики безопасности можно подключать
            backend, базу, уведомления и настоящий поток заказов.
          </p>
          <Link className="secondary-action" href="/catalog">
            Смотреть каталог
          </Link>
        </aside>
      </section>
    </main>
  );
}
