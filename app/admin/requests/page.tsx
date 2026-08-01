import Link from "next/link";
import { ArrowLeft, CheckCircle2, Clock3, PauseCircle, PhoneCall, XCircle } from "lucide-react";
import { changeRequestStatus, logoutAdmin } from "@/app/admin/actions";
import { formatPrice } from "@/src/data/catalog";
import { requireAdminSession } from "@/src/server/auth/admin";
import { getAdminCustomerRequests, type CustomerRequestStatus } from "@/src/server/db/catalog";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Заявки | Админка Zemazap"
};

type AdminRequestsPageProps = {
  searchParams?: Promise<{
    status?: string;
  }>;
};

const statusLabels: Record<CustomerRequestStatus, string> = {
  new: "Новая",
  in_work: "В работе",
  waiting_customer: "Ждем клиента",
  done: "Закрыта",
  cancelled: "Отменена"
};

const statusFilters: Array<{ value: string; label: string }> = [
  { value: "all", label: "Все" },
  { value: "new", label: "Новые" },
  { value: "in_work", label: "В работе" },
  { value: "waiting_customer", label: "Ждем клиента" },
  { value: "done", label: "Закрытые" },
  { value: "cancelled", label: "Отмененные" }
];

const statusActions: Array<{
  value: CustomerRequestStatus;
  label: string;
  note: string;
  icon: typeof CheckCircle2;
}> = [
  { value: "in_work", label: "В работу", note: "Менеджер взял заявку в работу", icon: Clock3 },
  { value: "waiting_customer", label: "Ждем клиента", note: "Менеджер ожидает ответ клиента", icon: PauseCircle },
  { value: "done", label: "Закрыть", note: "Заявка обработана", icon: CheckCircle2 },
  { value: "cancelled", label: "Отменить", note: "Заявка отменена", icon: XCircle }
];

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(new Date(value.replace(" ", "T")));

export default async function AdminRequestsPage({ searchParams }: AdminRequestsPageProps) {
  await requireAdminSession();

  const params = (await searchParams) ?? {};
  const status = params.status && params.status !== "all" ? params.status : undefined;
  const requests = getAdminCustomerRequests(status);

  return (
    <main className="admin-shell">
      <section className="admin-head">
        <div>
          <Link className="text-action" href="/admin">
            <ArrowLeft size={17} aria-hidden="true" />
            Панель
          </Link>
          <p className="eyebrow">Заявки клиентов</p>
          <h1>Входящие обращения</h1>
          <p>
            Здесь связываются телефон/мессенджер клиента, состав корзины или текст подбора,
            статус обработки и история действий менеджера.
          </p>
        </div>
        <form action={logoutAdmin}>
          <button type="submit" className="admin-ghost-button">
            Выйти
          </button>
        </form>
      </section>

      <nav className="admin-filter" aria-label="Фильтр заявок">
        {statusFilters.map((filter) => (
          <Link
            key={filter.value}
            className={!status && filter.value === "all" ? "is-active" : status === filter.value ? "is-active" : ""}
            href={filter.value === "all" ? "/admin/requests" : `/admin/requests?status=${filter.value}`}
          >
            {filter.label}
          </Link>
        ))}
      </nav>

      <section className="admin-requests-grid">
        {requests.length > 0 ? (
          requests.map((request) => (
            <article key={request.id} className="admin-request-card">
              <div className="admin-request-card__head">
                <div>
                  <span className={`admin-status admin-status--${request.status}`}>
                    {statusLabels[request.status]}
                  </span>
                  <h2>
                    <Link href={`/admin/requests/${request.id}`}>{request.customerName}</Link>
                  </h2>
                  <a href={`tel:${request.contact.replace(/[^\d+]/g, "")}`}>
                    <PhoneCall size={16} aria-hidden="true" />
                    {request.contact}
                  </a>
                </div>
                <div>
                  <span>{formatDate(request.createdAt)}</span>
                  <strong>{request.source === "cart" ? "Корзина" : "Форма подбора"}</strong>
                </div>
              </div>

              <div className="admin-request-card__body">
                {request.vehicle ? (
                  <p>
                    <strong>Автомобиль:</strong> {request.vehicle}
                  </p>
                ) : null}
                {request.requestText ? (
                  <p>
                    <strong>Запрос:</strong> {request.requestText}
                  </p>
                ) : null}

                {request.items.length > 0 ? (
                  <div className="admin-items">
                    {request.items.map((item) => (
                      <div key={item.id}>
                        <span>
                          {item.partName}
                          {item.article ? `, арт. ${item.article}` : ""}
                        </span>
                        <strong>
                          {item.quantity} шт. / {formatPrice(item.priceSnapshotRub * item.quantity)}
                        </strong>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>

              <div className="admin-request-card__actions">
                <Link className="admin-primary-button" href={`/admin/requests/${request.id}`}>
                  Открыть карточку
                </Link>
                {statusActions.map((action) => {
                  const Icon = action.icon;

                  return (
                    <form key={action.value} action={changeRequestStatus}>
                      <input type="hidden" name="requestId" value={request.id} />
                      <input type="hidden" name="status" value={action.value} />
                      <input type="hidden" name="note" value={action.note} />
                      <button type="submit" disabled={request.status === action.value}>
                        <Icon size={16} aria-hidden="true" />
                        {action.label}
                      </button>
                    </form>
                  );
                })}
              </div>

              <details className="admin-events">
                <summary>История обработки</summary>
                {request.events.length > 0 ? (
                  request.events.map((event) => (
                    <p key={event.id}>
                      <strong>{formatDate(event.createdAt)}:</strong> {event.note || event.eventType}
                    </p>
                  ))
                ) : (
                  <p>История пока пустая.</p>
                )}
              </details>
            </article>
          ))
        ) : (
          <div className="empty-state">
            <h2>Заявок с таким статусом пока нет</h2>
            <p>Новые обращения появятся после отправки формы подбора или корзины-заявки.</p>
          </div>
        )}
      </section>
    </main>
  );
}
