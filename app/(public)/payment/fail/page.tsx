import Link from "next/link";
import { CircleAlert } from "lucide-react";

export default function PaymentFailPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Оплата</p>
        <h1>Платеж не завершен</h1>
        <p>
          Если это тестовый платеж, менеджер может создать новую ссылку или проверить статус в
          платежном модуле.
        </p>
      </section>
      <section className="info-panel">
        <CircleAlert size={28} aria-hidden="true" />
        <h2>Что делать</h2>
        <p>Вернитесь к заказу или свяжитесь с магазином, чтобы уточнить способ оплаты.</p>
        <Link className="secondary-action" href="/contacts">
          Контакты
        </Link>
      </section>
    </main>
  );
}
