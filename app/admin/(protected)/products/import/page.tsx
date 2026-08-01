import Link from "next/link";
import { ArrowLeft, Upload } from "lucide-react";
import { importPriceFile } from "@/app/admin/actions";
import { requireAdminSession } from "@/src/server/auth/admin";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Импорт прайса | Админка Zemazap"
};

type ImportPageProps = {
  searchParams?: Promise<{
    result?: string;
    imported?: string;
    skipped?: string;
  }>;
};

export default async function AdminProductImportPage({ searchParams }: ImportPageProps) {
  await requireAdminSession();

  const params = (await searchParams) ?? {};

  return (
    <main className="admin-shell">
      <section className="admin-head">
        <div>
          <Link className="text-action" href="/admin/products">
            <ArrowLeft size={17} aria-hidden="true" />
            Товары
          </Link>
          <p className="eyebrow">Импорт</p>
          <h1>CSV/XLSX прайс</h1>
          <p>Загрузите таблицу поставщика. Система обновит товары по артикулу и создаст ценовые предложения.</p>
        </div>
      </section>

      <section className="admin-detail-layout">
        <article className="admin-panel">
          <h2>Файл прайса</h2>
          <form className="admin-import-form" action={importPriceFile}>
            <input name="file" type="file" accept=".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" />
            <button type="submit">
              <Upload size={18} aria-hidden="true" />
              Загрузить
            </button>
          </form>
          {params.result === "ok" ? (
            <p className="form-note">
              Импорт завершен: добавлено/обновлено {params.imported ?? "0"} строк, пропущено {params.skipped ?? "0"}.
            </p>
          ) : null}
          {params.result === "empty" ? (
            <p className="form-note form-note--error">Файл не выбран или пустой.</p>
          ) : null}
        </article>

        <aside className="admin-panel">
          <h2>Колонки</h2>
          <p className="form-note">Поддерживаются русские и английские заголовки:</p>
          <div className="admin-import-columns">
            <span>Название / name</span>
            <span>Артикул / article</span>
            <span>OEM</span>
            <span>Марка / brand</span>
            <span>Модель / model</span>
            <span>Категория / category</span>
            <span>Производитель / manufacturer</span>
            <span>Цена / price</span>
            <span>Наличие / availability</span>
            <span>Склад / stock</span>
            <span>Срок / delivery</span>
          </div>
        </aside>
      </section>
    </main>
  );
}
