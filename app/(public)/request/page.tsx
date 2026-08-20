import Link from "next/link";
import { MessageCircle, PackageSearch, ShieldCheck } from "lucide-react";
import RequestForm from "@/src/components/RequestForm";
import { siteConfig } from "@/src/server/siteConfig";

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
        <RequestForm maxUrl={siteConfig.maxUrl} />

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
