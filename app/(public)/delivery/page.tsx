import Link from "next/link";
import { CreditCard, PackageCheck, RotateCcw, Truck } from "lucide-react";

const steps = [
  { icon: PackageCheck, title: "Резерв", text: "Позиция закрепляется после подтверждения менеджером." },
  { icon: CreditCard, title: "Оплата", text: "Онлайн-оплата появится после подключения российского платежного провайдера." },
  { icon: Truck, title: "Доставка", text: "Самовывоз, курьер и транспортные компании будут настроены под выбранный город." },
  { icon: RotateCcw, title: "Возврат", text: "Правила возврата и гарантии нужно финализировать с юридическими реквизитами." }
];

export default function DeliveryPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Доставка, оплата и гарантии</p>
        <h1>Страница условий готова к юридическому заполнению</h1>
        <p>
          Сейчас это безопасная заготовка без обещаний, которые зависят от платежной системы,
          склада, региона и выбранной транспортной схемы.
        </p>
      </section>

      <section className="info-grid info-grid--four">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <article key={step.title} className="info-panel">
              <Icon size={26} aria-hidden="true" />
              <h2>{step.title}</h2>
              <p>{step.text}</p>
            </article>
          );
        })}
      </section>

      <section className="workspace workspace--split">
        <div>
          <div className="section-heading">
            <p className="eyebrow">Что важно решить</p>
            <h2>Перед подключением платежей</h2>
          </div>
          <ul className="check-list">
            <li><PackageCheck size={20} aria-hidden="true" /><span>кто юридически принимает оплату и выдает документы;</span></li>
            <li><PackageCheck size={20} aria-hidden="true" /><span>какие товары можно вернуть, а какие продаются под заказ;</span></li>
            <li><PackageCheck size={20} aria-hidden="true" /><span>как фиксируются фото, состояние и комплектность контрактных деталей;</span></li>
            <li><PackageCheck size={20} aria-hidden="true" /><span>куда приходят уведомления о заказах и оплатах.</span></li>
          </ul>
        </div>
        <aside className="process-panel">
          <h3>Формат MVP</h3>
          <p>
            До онлайн-оплаты корзина остается заявкой. Это снижает риск ошибок в цене, наличии и
            применимости, пока каталог питается моковыми данными.
          </p>
          <Link className="secondary-action" href="/cart">
            Корзина-заявка
          </Link>
        </aside>
      </section>
    </main>
  );
}
