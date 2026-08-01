import FavoritesContents from "@/src/components/FavoritesContents";

export default function FavoritesPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Избранное Zemazap</p>
        <h1>Сохраненные позиции</h1>
        <p>
          Избранное помогает собрать список деталей перед звонком менеджеру или оформлением
          корзины-заявки.
        </p>
      </section>

      <FavoritesContents />
    </main>
  );
}
