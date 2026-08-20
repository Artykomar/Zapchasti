import Link from "next/link";
import { PackageSearch } from "lucide-react";

export default function NotFound() {
  return (
    <main className="page-shell">
      <section className="empty-state">
        <PackageSearch size={42} aria-hidden="true" />
        <p className="eyebrow">Ошибка 404</p>
        <h1>Страница не найдена</h1>
        <p>Адрес мог измениться. Вернитесь в каталог или отправьте запрос на подбор детали.</p>
        <Link href="/catalog">Перейти в каталог</Link>
      </section>
    </main>
  );
}
