import Link from "next/link";
import { ArrowLeft, PhoneCall } from "lucide-react";
import { requireAdminSession } from "@/src/server/auth/admin";
import { getAdminCustomers } from "@/src/server/db/catalog";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Клиенты | Админка Zemazap"
};

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(new Date(value.replace(" ", "T")));

export default async function AdminCustomersPage() {
  await requireAdminSession();

  const customers = getAdminCustomers();

  return (
    <main className="admin-shell">
      <section className="admin-head">
        <div>
          <Link className="text-action" href="/admin">
            <ArrowLeft size={17} aria-hidden="true" />
            Панель
          </Link>
          <p className="eyebrow">Клиенты</p>
          <h1>Контакты покупателей</h1>
          <p>Пока клиент создается автоматически при заявке и связывается по нормализованному телефону.</p>
        </div>
      </section>

      <section className="admin-table">
        {customers.length > 0 ? (
          customers.map((customer) => (
            <article key={customer.id} className="admin-table-row">
              <div>
                <h2>{customer.displayName}</h2>
                <a href={`tel:${customer.contact.replace(/[^\d+]/g, "")}`}>
                  <PhoneCall size={16} aria-hidden="true" />
                  {customer.contact}
                </a>
              </div>
              <div>
                <span>Нормализованный контакт</span>
                <strong>{customer.normalizedContact}</strong>
              </div>
              <div>
                <span>Заявок</span>
                <strong>{customer.requestsCount}</strong>
              </div>
              <div>
                <span>Обновлен</span>
                <strong>{formatDate(customer.updatedAt)}</strong>
              </div>
            </article>
          ))
        ) : (
          <div className="empty-state">
            <h2>Клиентов пока нет</h2>
            <p>Они появятся после первой заявки из формы или корзины.</p>
          </div>
        )}
      </section>
    </main>
  );
}
