import Link from "next/link";
import { MessageSquare } from "lucide-react";

export default function ReviewsPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Отзывы</p>
        <h1>Отзывы появятся после запуска и модерации</h1>
        <p>
          Здесь будут опубликованы только реальные отзывы клиентов после проверки. Демонстрационные
          имена и тексты удалены из публичной витрины.
        </p>
      </section>

      <section className="empty-state">
        <MessageSquare size={30} aria-hidden="true" />
        <h2>Пока нет опубликованных отзывов</h2>
        <p>После запуска магазин сможет принимать отзывы и публиковать их через модерацию.</p>
      </section>

      <section className="contact-wide">
        <div>
          <MessageSquare size={26} aria-hidden="true" />
          <h2>Нужна помощь с подбором?</h2>
          <p>Оставьте заявку — менеджер сверит номер детали, совместимость, цену и срок.</p>
        </div>
        <Link className="secondary-action" href="/request">
          Оставить заявку
        </Link>
      </section>
    </main>
  );
}
