import Link from "next/link";
import {
  Bell,
  FileSpreadsheet,
  Inbox,
  LayoutDashboard,
  LogOut,
  Package,
  ShieldCheck,
  Users
} from "lucide-react";
import { logoutAdmin } from "@/app/admin/actions";
import { requireAdminSession } from "@/src/server/auth/admin";

const adminNavItems = [
  { href: "/admin", label: "Сводка", icon: LayoutDashboard },
  { href: "/admin/requests", label: "Заявки", icon: Inbox },
  { href: "/admin/customers", label: "Клиенты", icon: Users },
  { href: "/admin/products", label: "Товары", icon: Package },
  { href: "/admin/products/import", label: "Импорт", icon: FileSpreadsheet },
  { href: "/admin/notifications", label: "Уведомления", icon: Bell }
];

export default async function AdminProtectedLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  await requireAdminSession();

  return (
    <div className="admin-app">
      <header className="admin-topbar">
        <Link className="admin-brand" href="/admin" aria-label="В админскую сводку Zemazap">
          <ShieldCheck size={24} aria-hidden="true" />
          <span>
            <strong>Zemazap Admin</strong>
            <small>закрытый контур продавца</small>
          </span>
        </Link>

        <nav className="admin-nav" aria-label="Навигация админки">
          {adminNavItems.map((item) => {
            const Icon = item.icon;

            return (
              <Link key={item.href} href={item.href}>
                <Icon size={17} aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <form className="admin-logout-form" action={logoutAdmin}>
          <button type="submit" aria-label="Выйти из админки">
            <LogOut size={17} aria-hidden="true" />
            <span>Выйти</span>
          </button>
        </form>
      </header>

      {children}
    </div>
  );
}
