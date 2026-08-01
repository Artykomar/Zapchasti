import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, CheckCircle2, Clock3, PauseCircle, PhoneCall, XCircle } from "lucide-react";
import { addRequestComment, changeRequestStatus } from "@/app/admin/actions";
import { formatPrice } from "@/src/data/catalog";
import { requireAdminSession } from "@/src/server/auth/admin";
import { getAdminCustomerRequestById, type CustomerRequestStatus } from "@/src/server/db/catalog";

export const dynamic = "force-dynamic";

type AdminRequestDetailPageProps = {
  params: Promise<{
    id: string;
  }>;
};

const statusLabels: Record<CustomerRequestStatus, string> = {
  new: "Новая",
  in_work: "В работе",
  waiting_customer: "Ждем клиента",
  done: "Закрыта",
  cancelled: "Отменена"
};

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

export default async function AdminRequestDetailPage({ params }: AdminRequestDetailPageProps) {
  await requireAdminSession();

  const { id } = await params;
  const request = getAdminCustomerRequestById(id);

  if (!request) {
    notFound();
  }

  return (
    <main className="admin-shell">
      <section className="admin-head">
        <div>
          <Link className="text-action" href="/admin/requests">
            <ArrowLeft size={17} aria-hidden="true" />
            Все заявки
          </Link>
          <p className="eyebrow">Карточка заявки</p>
          <h1>{request.customerName}</h1>
          <p>Детальный рабочий экран менеджера: клиент, товары, контакт, статусы и комментарии.</p>
        </div>
      </section>

      <section className="admin-detail-layout">
        <article className="admin-panel">
          <div className="admin-request-card__head admin-request-card__head--inside">
            <div>
              <span className={`admin-status admin-status--${request.status}`}>
                {statusLabels[request.status]}
              </span>
              <h2>Заявка от {formatDate(request.createdAt)}</h2>
              <a href={`tel:${request.contact.replace(/[^\d+]/g, "")}`}>
                <PhoneCall size={16} aria-hidden="true" />
                {request.contact}
              </a>
            </div>
            <div>
              <span>{request.source === "cart" ? "Корзина-заявка" : "Форма подбора"}</span>
              <strong>{request.totalEstimateRub > 0 ? formatPrice(request.totalEstimateRub) : "Сумма уточняется"}</strong>
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
        </article>

        <aside className="admin-panel">
          <h2>Клиент</h2>
          {request.customer ? (
            <dl className="admin-definition-list">
              <div>
                <dt>Имя</dt>
                <dd>{request.customer.displayName}</dd>
              </div>
              <div>
                <dt>Контакт</dt>
                <dd>{request.customer.contact}</dd>
              </div>
              <div>
                <dt>Нормализованный телефон</dt>
                <dd>{request.customer.normalizedContact}</dd>
              </div>
            </dl>
          ) : (
            <p className="form-note">Клиент еще не выделен в отдельную карточку.</p>
          )}
        </aside>
      </section>

      <section className="admin-detail-layout">
        <article className="admin-panel">
          <h2>Комментарий менеджера</h2>
          <form className="admin-comment-form" action={addRequestComment}>
            <input type="hidden" name="requestId" value={request.id} />
            <textarea name="note" placeholder="Например: позвонил клиенту, уточнил год выпуска, ждем фото детали" />
            <button type="submit">Добавить комментарий</button>
          </form>
        </article>

        <aside className="admin-panel">
          <h2>История</h2>
          <div className="admin-events admin-events--plain">
            {request.events.length > 0 ? (
              request.events.map((event) => (
                <p key={event.id}>
                  <strong>{formatDate(event.createdAt)}:</strong> {event.note || event.eventType}
                </p>
              ))
            ) : (
              <p>История пока пустая.</p>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}
