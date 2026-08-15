import Link from "next/link";
import { CheckCircle2 } from "lucide-react";

export default function PaymentSuccessPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Оплата</p>
        <h1>Платеж отмечен как успешный</h1>
        <p>
          В production финальный статус будет подтверждаться server-to-server проверкой у платежного
          провайдера, а не только переходом браузера.
        </p>
      </section>
      <section className="info-panel">
        <CheckCircle2 size={28} aria-hidden="true" />
        <h2>Следующий шаг</h2>
        <p>Менеджер проверит оплату в админке и продолжит обработку заказа.</p>
        <Link className="secondary-action" href="/contacts">
          Контакты
        </Link>
      </section>
    </main>
  );
}
