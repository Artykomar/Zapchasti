import Link from "next/link";
import { MessageSquare, Star } from "lucide-react";
import { reviews } from "@/src/data/catalog";

export default function ReviewsPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Отзывы</p>
        <h1>Страница отзывов готова к подключению реальных источников</h1>
        <p>
          Пока отзывы являются демонстрационными. После запуска их лучше подтягивать из выбранных
          площадок или добавлять вручную через админку с модерацией.
        </p>
      </section>

      <section className="review-grid">
        {reviews.map((review) => (
          <article key={`${review.name}-${review.city}`} className="review-card">
            <div className="review-card__stars" aria-label="Оценка 5 из 5">
              {Array.from({ length: 5 }).map((_, index) => (
                <Star key={index} size={17} aria-hidden="true" />
              ))}
            </div>
            <p>{review.text}</p>
            <strong>{review.name}</strong>
            <span>{review.city}</span>
          </article>
        ))}
      </section>

      <section className="contact-wide">
        <div>
          <MessageSquare size={26} aria-hidden="true" />
          <h2>Будущая механика</h2>
          <p>Можно добавить форму отзыва, модерацию, рейтинг товара и ссылку на внешние площадки.</p>
        </div>
        <Link className="secondary-action" href="/request">
          Оставить заявку
        </Link>
      </section>
    </main>
  );
}
