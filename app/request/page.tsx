import Link from "next/link";
import { MessageCircle, PackageSearch, Send, ShieldCheck } from "lucide-react";

export default function RequestPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Заявка Zemazap</p>
        <h1>Запрос на подбор или подтверждение заказа</h1>
        <p>
          На старте заявки обрабатываются вручную: клиент оставляет контакты, номера деталей,
          артикулы или данные автомобиля, а менеджер подтверждает наличие, состояние и срок.
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
            Автомобиль
            <input name="vehicle" placeholder="Марка, модель, год, двигатель или модификация" />
          </label>
          <label>
            Что нужно найти
            <textarea name="parts" placeholder="Номер детали, артикул, название, фото/описание или список позиций" />
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
            <li>номер детали, артикул и совместимость;</li>
            <li>актуальную цену и срок у поставщиков;</li>
            <li>состояние, комплектность и фото для контрактных деталей;</li>
            <li>условия резерва, гарантии и возврата.</li>
          </ul>
          <Link href="/cart">
            <PackageSearch size={18} aria-hidden="true" />
            Открыть корзину
          </Link>
          <Link href="/contacts" className="request-aside__ghost">
            <MessageCircle size={18} aria-hidden="true" />
            Связаться напрямую
          </Link>
        </aside>
      </section>
    </main>
  );
}
