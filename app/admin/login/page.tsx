import Link from "next/link";
import { ShieldCheck } from "lucide-react";
import AdminLoginForm from "@/src/components/AdminLoginForm";
import { isAdminConfigured, localDevelopmentAdminPassword } from "@/src/server/auth/admin";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Вход в админку | Zemazap"
};

export default function AdminLoginPage() {
  const configured = isAdminConfigured();
  const showDevPassword = process.env.NODE_ENV !== "production" && configured;

  return (
    <main className="admin-auth-shell">
      <section className="admin-auth-panel">
        <ShieldCheck size={36} aria-hidden="true" />
        <p className="eyebrow">Zemazap Admin</p>
        <h1>Вход для продавца</h1>
        <p>
          Админская часть нужна для обработки заявок, товаров, цен, остатков, поставщиков,
          импорта прайсов и контроля заказов.
        </p>
        {configured ? <AdminLoginForm /> : null}
        {!configured ? (
          <p className="form-note form-note--error">
            Пароль администратора не задан. Нужно добавить `ZEMAZAP_ADMIN_PASSWORD` в окружение.
          </p>
        ) : null}
        {showDevPassword ? (
          <p className="form-note">
            Локальный пароль разработки: <strong>{localDevelopmentAdminPassword}</strong>. Перед запуском сайта его
            нужно заменить в `.env`.
          </p>
        ) : null}
        <Link className="text-action" href="/">
          Вернуться на сайт
        </Link>
      </section>
    </main>
  );
}
