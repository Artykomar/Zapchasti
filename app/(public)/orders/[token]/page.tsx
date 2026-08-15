import Link from "next/link";
import { notFound } from "next/navigation";
import { CreditCard, PackageCheck, ShieldCheck } from "lucide-react";
import { formatPrice } from "@/src/data/catalog";
import { getOrderByToken } from "@/src/server/django/orders";

export const dynamic = "force-dynamic";

type OrderPageProps = {
  params: Promise<{
    token: string;
  }>;
};

export async function generateMetadata({ params }: OrderPageProps) {
  const { token } = await params;
  const order = await getOrderByToken(token);

  if (!order) {
    return {
      title: "Заказ не найден | Zemazap"
    };
  }

  return {
    title: `Заказ ${order.token} | Zemazap`,
    description: "Подтвержденный заказ Zemazap с составом, суммой и тестовой платежной ссылкой."
  };
}

export default async function OrderPage({ params }: OrderPageProps) {
  const { token } = await params;
  const order = await getOrderByToken(token);

  if (!order) {
    notFound();
  }

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Подтвержденный заказ</p>
        <h1>Заказ {order.token}</h1>
        <p>
          Оплата доступна только после проверки менеджером. Сайт не принимает и не хранит данные
          банковских карт.
        </p>
      </section>

      <section className="workspace workspace--split">
        <div>
          <div className="section-heading">
            <p className="eyebrow">Состав</p>
            <h2>{order.customer_name}</h2>
          </div>
          <div className="cart-list">
            {order.items.map((item) => (
              <article key={`${item.article}-${item.part_name}`} className="cart-item">
                <div>
                  <h3>{item.part_name}</h3>
                  <p>{item.article || "Артикул уточняется"}</p>
                </div>
                <span>{item.quantity} шт.</span>
                <strong>{formatPrice(item.line_total_rub)}</strong>
              </article>
            ))}
          </div>
        </div>

        <aside className="process-panel">
          <CreditCard size={28} aria-hidden="true" />
          <h2>{formatPrice(order.total_amount_rub)}</h2>
          <p>Статус: {order.status}</p>
          <p>{order.vat_label}</p>
          {order.payment_url ? (
            <a className="secondary-action" href={order.payment_url}>
              Перейти к тестовой оплате
            </a>
          ) : (
            <p>Платежная ссылка появится после подтверждения менеджером.</p>
          )}
        </aside>
      </section>

      <section className="info-grid">
        <article className="info-panel">
          <PackageCheck size={24} aria-hidden="true" />
          <h2>Доставка</h2>
          <p>{order.delivery_terms || "Условия доставки фиксируются менеджером перед оплатой."}</p>
        </article>
        <article className="info-panel">
          <ShieldCheck size={24} aria-hidden="true" />
          <h2>Гарантия</h2>
          <p>{order.warranty_terms || "Гарантия и возврат зависят от состояния и типа детали."}</p>
        </article>
      </section>

      <Link className="secondary-action" href="/contacts">
        Связаться с магазином
      </Link>
    </main>
  );
}
