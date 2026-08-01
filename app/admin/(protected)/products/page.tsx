import Link from "next/link";
import { ArrowLeft, Eye, EyeOff, FileSpreadsheet } from "lucide-react";
import { setProductActivity } from "@/app/admin/actions";
import { formatPrice } from "@/src/data/catalog";
import { requireAdminSession } from "@/src/server/auth/admin";
import { getAdminProducts } from "@/src/server/db/catalog";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Товары | Админка Zemazap"
};

type AdminProductsPageProps = {
  searchParams?: Promise<{
    q?: string;
  }>;
};

export default async function AdminProductsPage({ searchParams }: AdminProductsPageProps) {
  await requireAdminSession();

  const params = (await searchParams) ?? {};
  const products = getAdminProducts(params.q);

  return (
    <main className="admin-shell">
      <section className="admin-head">
        <div>
          <Link className="text-action" href="/admin">
            <ArrowLeft size={17} aria-hidden="true" />
            Панель
          </Link>
          <p className="eyebrow">Товары</p>
          <h1>Управление каталогом</h1>
          <p>Пока доступно скрытие товара с витрины и импорт прайса. Полный редактор карточки будет следующим слоем.</p>
        </div>
      </section>

      <div className="admin-panel admin-panel__head">
        <form className="admin-search-form" action="/admin/products">
          <input name="q" defaultValue={params.q ?? ""} placeholder="Поиск по названию, артикулу, OEM или марке" />
          <button type="submit">Найти</button>
        </form>
        <Link className="admin-primary-button" href="/admin/products/import">
          <FileSpreadsheet size={17} aria-hidden="true" />
          Импорт прайса
        </Link>
      </div>

      <section className="admin-table">
        {products.map((part) => (
          <article key={part.id} className="admin-table-row admin-table-row--product">
            <div>
              <span className={part.isActive ? "admin-status admin-status--in_work" : "admin-status admin-status--cancelled"}>
                {part.isActive ? "На витрине" : "Скрыт"}
              </span>
              <h2>{part.name}</h2>
              <p>
                {part.brand} {part.model}, {part.category}
              </p>
            </div>
            <div>
              <span>Артикул / OEM</span>
              <strong>{part.article}</strong>
              <small>{part.oem}</small>
            </div>
            <div>
              <span>Цена и срок</span>
              <strong>{formatPrice(part.price)}</strong>
              <small>{part.availability}</small>
            </div>
            <form action={setProductActivity}>
              <input type="hidden" name="partId" value={part.id} />
              <input type="hidden" name="isActive" value={part.isActive ? "false" : "true"} />
              <button type="submit" className="admin-ghost-button">
                {part.isActive ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
                {part.isActive ? "Скрыть" : "Вернуть"}
              </button>
            </form>
          </article>
        ))}
      </section>
    </main>
  );
}
