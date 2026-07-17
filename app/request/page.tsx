import Link from "next/link";
import { MessageCircle, Send, ShieldCheck } from "lucide-react";

export default function RequestPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Корзина-заявка</p>
        <h1>Запрос на подбор или подтверждение заказа</h1>
        <p>
          На старте заявки можно обрабатывать вручную: клиент оставляет контакты, VIN или артикулы, а
          менеджер подтверждает применимость, цену и срок поставки.
        </p>
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
            VIN или данные автомобиля
            <input name="vehicle" placeholder="VIN, марка, модель, год, двигатель" />
          </label>
          <label>
            Что нужно найти
            <textarea name="parts" placeholder="OEM, артикулы, названия деталей или описание задачи" />
          </label>
          <label className="checkbox-row">
            <input type="checkbox" name="privacy" />
            <span>Согласен на обработку персональных данных после добавления юридического текста</span>
          </label>
          <button type="button">
            <Send size={18} aria-hidden="true" />
            Отправить заявку
          </button>
        </form>

        <aside className="request-aside">
          <ShieldCheck size={30} aria-hidden="true" />
          <h2>Что проверит менеджер</h2>
          <ul>
            <li>применимость детали к автомобилю;</li>
            <li>актуальную цену и срок у поставщиков;</li>
            <li>оригинал или заводской аналог;</li>
            <li>условия гарантии и возврата для новой детали.</li>
          </ul>
          <Link href="/contacts">
            <MessageCircle size={18} aria-hidden="true" />
            Связаться напрямую
          </Link>
        </aside>
      </section>
    </main>
  );
}
