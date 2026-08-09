import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, Car, PackageCheck } from "lucide-react";
import ProductActions from "@/src/components/ProductActions";
import { formatPrice } from "@/src/data/catalog";
import { getBrandBySlug, getPartsByBrandSlug } from "@/src/server/django/catalog";

export const dynamic = "force-dynamic";

type BrandPageProps = {
  params: Promise<{
    brand: string;
  }>;
};

export async function generateMetadata({ params }: BrandPageProps) {
  const { brand: brandSlug } = await params;
  const brand = await getBrandBySlug(brandSlug);

  if (!brand) {
    return {
      title: "Марка не найдена | Zemazap"
    };
  }

  return {
    title: `${brand.name} запчасти | Zemazap`,
    description: `Каталог запчастей Zemazap для ${brand.name}: модели, категории, товары и заявка менеджеру.`
  };
}

export default async function BrandCategoryPage({ params }: BrandPageProps) {
  const { brand: brandSlug } = await params;
  const brand = await getBrandBySlug(brandSlug);

  if (!brand) {
    notFound();
  }

  const brandParts = await getPartsByBrandSlug(brand.slug);

  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Марка {brand.name}</p>
        <h1>Запчасти {brand.name} в каталоге Zemazap</h1>
        <p>
          Страница марки повторяет привычную структуру магазина: модели, годы выпуска, товарные
          позиции и быстрый переход к заявке.
        </p>
      </section>

      <section className="model-grid">
        {brand.models.map((model) => (
          <article key={model.slug} className="model-card">
            <Car size={24} aria-hidden="true" />
            <h2>{model.name}</h2>
            <p>{model.years}</p>
            <span>{model.generations.join(", ")}</span>
          </article>
        ))}
      </section>

      <section className="catalog-products brand-products">
        {brandParts.length > 0 ? (
          brandParts.map((part) => (
            <article key={part.id} className="wide-product">
              <Link className="wide-product__visual" href={`/product/${part.slug}`}>
                <PackageCheck size={42} aria-hidden="true" />
                <span>{part.condition}</span>
              </Link>
              <div className="wide-product__content">
                <span className="tag">{part.category}</span>
                <h2>
                  <Link href={`/product/${part.slug}`}>{part.name}</Link>
                </h2>
                <p>{part.delivery}</p>
                <div className="spec-list">
                  <span>Номер: {part.oem}</span>
                  <span>Артикул: {part.article}</span>
                  <span>Модель: {part.model}</span>
                  <span>Срок: {part.availability}</span>
                </div>
              </div>
              <div className="wide-product__action">
                <strong>{formatPrice(part.price)}</strong>
                <ProductActions part={part} compact />
                <Link href={`/product/${part.slug}`} className="text-action">
                  Подробнее
                  <ArrowRight size={17} aria-hidden="true" />
                </Link>
              </div>
            </article>
          ))
        ) : (
          <div className="empty-state">
            <h3>Товары этой марки еще не заведены</h3>
            <p>Страница уже готова к наполнению после появления прайса или складских остатков.</p>
            <Link href="/request">Оставить заявку</Link>
          </div>
        )}
      </section>
    </main>
  );
}
