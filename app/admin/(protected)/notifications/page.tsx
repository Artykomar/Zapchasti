import Link from "next/link";
import { ArrowLeft, Bell, Mail, Send } from "lucide-react";
import { requireAdminSession } from "@/src/server/auth/admin";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Уведомления | Админка Zemazap"
};

export default async function AdminNotificationsPage() {
  await requireAdminSession();

  const managerEmail = process.env.ZEMAZAP_MANAGER_EMAIL?.trim() ?? "";
  const smtpHost = process.env.ZEMAZAP_SMTP_HOST?.trim() ?? "";
  const smtpUser = process.env.ZEMAZAP_SMTP_USER?.trim() ?? "";
  const smtpFrom = process.env.ZEMAZAP_SMTP_FROM?.trim() ?? "";
  const smtpPasswordConfigured = Boolean(process.env.ZEMAZAP_SMTP_PASSWORD?.trim());
  const telegramChatId = process.env.ZEMAZAP_TELEGRAM_CHAT_ID?.trim() ?? "";
  const telegramBotConfigured = Boolean(process.env.ZEMAZAP_TELEGRAM_BOT_TOKEN?.trim());
  const emailConfigured = Boolean(managerEmail && smtpHost && smtpUser && smtpPasswordConfigured);
  const telegramConfigured = Boolean(telegramChatId && telegramBotConfigured);

  return (
    <main className="admin-shell">
      <section className="admin-head">
        <div>
          <Link className="text-action" href="/admin">
            <ArrowLeft size={17} aria-hidden="true" />
            Панель
          </Link>
          <p className="eyebrow">Уведомления</p>
          <h1>Email и Telegram</h1>
          <p>
            Этот раздел фиксирует, какие каналы готовы. После добавления реальных данных подключим отправку
            уведомления при каждой новой заявке.
          </p>
        </div>
      </section>

      <section className="admin-detail-layout">
        <article className="admin-panel">
          <Mail size={24} aria-hidden="true" />
          <h2>Email</h2>
          <dl className="admin-definition-list">
            <div>
              <dt>Получатель</dt>
              <dd>{managerEmail || "не задан"}</dd>
            </div>
            <div>
              <dt>SMTP</dt>
              <dd>{smtpHost || "не задан"}</dd>
            </div>
            <div>
              <dt>Отправитель</dt>
              <dd>{smtpFrom || smtpUser || "не задан"}</dd>
            </div>
            <div>
              <dt>Статус</dt>
              <dd>{emailConfigured ? "готово к отправке" : "нужно заполнить .env"}</dd>
            </div>
          </dl>
        </article>

        <article className="admin-panel">
          <Send size={24} aria-hidden="true" />
          <h2>Telegram</h2>
          <dl className="admin-definition-list">
            <div>
              <dt>Chat ID</dt>
              <dd>{telegramChatId || "не задан"}</dd>
            </div>
            <div>
              <dt>Bot token</dt>
              <dd>{telegramBotConfigured ? "задан в окружении" : "не задан"}</dd>
            </div>
            <div>
              <dt>Статус</dt>
              <dd>{telegramConfigured ? "готово к отправке" : "нужно заполнить .env"}</dd>
            </div>
          </dl>
        </article>

        <article className="admin-panel">
          <Bell size={24} aria-hidden="true" />
          <h2>Что нужно от владельца</h2>
          <ul className="admin-checklist">
            <li>email, куда присылать новые заявки;</li>
            <li>решение, какой почтовый канал использовать: SMTP доменной почты или сервис рассылки;</li>
            <li>Telegram: username/ссылка на рабочий чат или готовый `chat_id`;</li>
            <li>после создания бота: `TELEGRAM_BOT_TOKEN`.</li>
          </ul>
        </article>
      </section>
    </main>
  );
}
