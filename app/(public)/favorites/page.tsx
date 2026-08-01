import FavoritesContents from "@/src/components/FavoritesContents";

export default function FavoritesAliasPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Избранное Zemazap</p>
        <h1>Сохраненные позиции</h1>
        <p>Англоязычный маршрут оставлен как алиас для избранных товаров.</p>
      </section>

      <FavoritesContents />
    </main>
  );
}
