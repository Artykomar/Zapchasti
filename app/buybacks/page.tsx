import Link from "next/link";
import { CarFront, ClipboardCheck, PackagePlus, Send } from "lucide-react";

export default function BuybacksPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Выкуп авто и остатков</p>
        <h1>Будущий канал пополнения склада Zemazap</h1>
        <p>
          Раздел подготовлен по структуре сайта-образца, но без узкой специализации: сюда можно
          принимать автомобили, агрегаты, партии запчастей и складские остатки разных марок.
        </p>
      </section>

      <section className="info-grid">
        <article className="info-panel">
          <CarFront size={26} aria-hidden="true" />
          <h2>Автомобили</h2>
          <p>Заявка на оценку автомобиля целиком после ДТП, поломки или простоя.</p>
        </article>
        <article className="info-panel">
          <PackagePlus size={26} aria-hidden="true" />
          <h2>Запчасти</h2>
          <p>Партии новых, контрактных или восстановленных деталей с проверкой происхождения.</p>
        </article>
        <article className="info-panel">
          <ClipboardCheck size={26} aria-hidden="true" />
          <h2>Оценка</h2>
          <p>Фото, список позиций, состояние, город, документы и быстрый обратный контакт.</p>
        </article>
      </section>

      <section className="request-layout">
        <form className="request-form">
          <label>
            Имя
            <input name="name" placeholder="Как к вам обращаться" />
          </label>
          <label>
            Телефон или мессенджер
            <input name="phone" placeholder="+7 (___) ___-__-__" />
          </label>
          <label>
            Что хотите предложить
            <textarea name="offer" placeholder="Автомобиль, агрегат, партия деталей, город, состояние и примерная комплектация" />
          </label>
          <button type="button">
            <Send size={18} aria-hidden="true" />
            Отправить на оценку
          </button>
        </form>
        <aside className="request-aside">
          <h2>Что добавить позже</h2>
          <ul>
            <li>загрузку фото;</li>
            <li>отдельную CRM-воронку выкупа;</li>
            <li>проверку документов;</li>
            <li>статусы оценки и выезда.</li>
          </ul>
          <Link href="/contacts">Контакты</Link>
        </aside>
      </section>
    </main>
  );
}
