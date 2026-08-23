import Link from "next/link";
import { CheckCircle2, Clock3 } from "lucide-react";
import { getOrderByToken } from "@/src/server/django/orders";

export const dynamic = "force-dynamic";

type PaymentSuccessPageProps = {
  searchParams: Promise<{ order?: string }>;
};

const CONFIRMED_STATUSES = new Set(["paid", "partially_refunded", "refunded", "fulfilled"]);

export default async function PaymentSuccessPage({ searchParams }: PaymentSuccessPageProps) {
  const { order: token } = await searchParams;
  const order = token ? await getOrderByToken(token) : undefined;
  const isConfirmed = Boolean(order && CONFIRMED_STATUSES.has(order.status));

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Оплата</p>
        <h1>{isConfirmed ? "Оплата подтверждена" : "Платеж проверяется"}</h1>
        <p>
          Возврат браузера из банка сам по себе не подтверждает оплату. Финальный статус сайт получает
          напрямую от платежного провайдера.
        </p>
      </section>
      <section className="info-panel">
        {isConfirmed ? (
          <CheckCircle2 size={28} aria-hidden="true" />
        ) : (
          <Clock3 size={28} aria-hidden="true" />
        )}
        <h2>Следующий шаг</h2>
        <p>
          {isConfirmed
            ? "Заказ оплачен и передан менеджеру в дальнейшую обработку."
            : "Статус обновится после server-to-server проверки. Если он не изменится, свяжитесь с магазином."}
        </p>
        <Link className="secondary-action" href={token ? `/orders/${token}` : "/contacts"}>
          {token ? "Открыть заказ" : "Контакты"}
        </Link>
      </section>
    </main>
  );
}
