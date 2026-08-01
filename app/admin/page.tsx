import Link from "next/link";
import {
  Bell,
  ClipboardList,
  Database,
  FileSpreadsheet,
  Inbox,
  Package,
  ShieldCheck,
  Users
} from "lucide-react";
import { logoutAdmin } from "@/app/admin/actions";
import { requireAdminSession } from "@/src/server/auth/admin";
import {
  getAdminDashboardStats,
  getAdminCustomerRequests,
  type CustomerRequestStatus
} from "@/src/server/db/catalog";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Админка | Zemazap"
};

const statusLabels: Record<CustomerRequestStatus, string> = {
  new: "Новая",
  in_work: "В работе",
  waiting_customer: "Ждем клиента",
  done: "Закрыта",
  cancelled: "Отменена"
};

export default async function AdminPage() {
  await requireAdminSession();

  const stats = getAdminDashboardStats();
  const recentRequests = getAdminCustomerRequests().slice(0, 5);
  const statItems = [
    { label: "Новые заявки", value: stats.newRequests, icon: Inbox },
    { label: "В работе", value: stats.inWorkRequests, icon: ClipboardList },
    { label: "Закрыто", value: stats.doneRequests, icon: ShieldCheck },
    { label: "Товары", value: stats.products, icon: Package },
    { label: "Марки", value: stats.brands, icon: Database },
    { label: "Клиенты", value: stats.customers, icon: Users }
  ];
  const adminSections = [
    { href: "/admin/requests", label: "Заявки", icon: Inbox },
    { href: "/admin/customers", label: "Клиенты", icon: Users },
    { href: "/admin/products", label: "Товары", icon: Package },
    { href: "/admin/products/import", label: "Импорт прайса", icon: FileSpreadsheet },
    { href: "/admin/notifications", label: "Уведомления", icon: Bell }
  ];

  return (
    <main className="admin-shell">
      <section className="admin-head">
        <div>
          <p className="eyebrow">Панель продавца</p>
          <h1>Админка Zemazap</h1>
          <p>
            Первый рабочий слой: заявки уже попадают в базу, а продавец может видеть клиента,
            состав обращения и менять статус обработки.
          </p>
        </div>
        <form action={logoutAdmin}>
          <button type="submit" className="admin-ghost-button">
            Выйти
          </button>
        </form>
      </section>

      <section className="admin-stat-grid" aria-label="Сводка">
        {statItems.map((item) => {
          const Icon = item.icon;

          return (
            <article key={item.label} className="admin-stat">
              <Icon size={22} aria-hidden="true" />
              <strong>{item.value}</strong>
              <span>{item.label}</span>
            </article>
          );
        })}
      </section>

      <section className="admin-layout">
        <div className="admin-panel">
          <div className="admin-panel__head">
            <div>
              <h2>Последние заявки</h2>
              <p>Новые обращения из формы подбора и корзины-заявки.</p>
            </div>
            <Link className="admin-primary-button" href="/admin/requests">
              Все заявки
            </Link>
          </div>

          <div className="admin-request-list">
            {recentRequests.length > 0 ? (
              recentRequests.map((request) => (
                <article key={request.id} className="admin-request-row">
                  <div>
                    <span className={`admin-status admin-status--${request.status}`}>
                      {statusLabels[request.status]}
                    </span>
                    <h3>{request.customerName}</h3>
                    <p>{request.contact}</p>
                  </div>
                  <div>
                    <strong>{request.items.length > 0 ? `${request.items.length} поз.` : "Подбор"}</strong>
                    <span>{request.vehicle || request.requestText || "Без описания"}</span>
                  </div>
                </article>
              ))
            ) : (
              <div className="empty-state empty-state--inside">
                <h3>Заявок пока нет</h3>
                <p>После отправки формы или корзины они появятся здесь.</p>
              </div>
            )}
          </div>
        </div>

        <aside className="admin-panel admin-roadmap">
          <h2>Разделы админки</h2>
          <div className="admin-section-links">
            {adminSections.map((item) => {
              const Icon = item.icon;

              return (
                <Link key={item.href} href={item.href}>
                  <Icon size={18} aria-hidden="true" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </aside>
      </section>
    </main>
  );
}
