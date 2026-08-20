import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, CheckCircle2, PackageCheck, ShieldCheck, Truck } from "lucide-react";
import ProductActions from "@/src/components/ProductActions";
import { formatPrice, getProductPath } from "@/src/data/catalog";
import { getPartBySlug, getSimilarParts } from "@/src/server/django/catalog";
import { getCanonicalUrl, hasPublicLegalEntity, siteConfig } from "@/src/server/siteConfig";

export const dynamic = "force-dynamic";

type ProductPageProps = {
  params: Promise<{
    slug: string;
  }>;
};

export async function generateMetadata({ params }: ProductPageProps) {
  const { slug } = await params;
  const part = await getPartBySlug(slug);

  if (!part) {
    return {
      title: "Товар не найден | Zemazap",
      robots: { index: false, follow: false }
    };
  }

  const title = `${part.name} | ${siteConfig.brandName}`;
  const description = `${part.brand} ${part.model}: ${part.article}, ${part.condition}, ${part.availability}.`;
  const url = getCanonicalUrl(`/product/${part.slug}`);
  return {
    title,
    description,
    alternates: { canonical: url },
    openGraph: { title, description, url, type: "website", images: [] },
    twitter: { card: "summary", title, description, images: [] }
  };
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { slug } = await params;
  const part = await getPartBySlug(slug);

  if (!part) {
    notFound();
  }

  const similarParts = await getSimilarParts(part, 4);
  const productJsonLd = siteConfig.indexingAllowed && hasPublicLegalEntity()
    ? {
        "@context": "https://schema.org",
        "@type": "Product",
        name: part.name,
        sku: part.article,
        mpn: part.oem,
        brand: { "@type": "Brand", name: part.manufacturer },
        description: part.description,
        itemCondition: part.condition === "новая"
          ? "https://schema.org/NewCondition"
          : "https://schema.org/UsedCondition",
        offers: {
          "@type": "Offer",
          url: getCanonicalUrl(`/product/${part.slug}`),
          priceCurrency: "RUB",
          price: part.price,
          availability: part.availability === "в наличии"
            ? "https://schema.org/InStock"
            : "https://schema.org/PreOrder",
          seller: { "@type": "Organization", name: siteConfig.legalName }
        }
      }
    : null;

  return (
    <main className="page-shell">
      {productJsonLd ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(productJsonLd).replace(/</g, "\\u003c") }}
        />
      ) : null}
      <section className="product-detail">
        <div className="product-detail__visual">
          <PackageCheck size={70} aria-hidden="true" />
          <span>{part.category}</span>
        </div>
        <div className="product-detail__content">
          <p className="eyebrow">{part.brand} {part.model}</p>
          <h1>{part.name}</h1>
          <p>{part.description}</p>
          <div className="product-detail__meta">
            <span>{part.condition}</span>
            <span>{part.quality}</span>
            <span>{part.availability}</span>
          </div>
          <div className="product-detail__price">
            <strong>{formatPrice(part.price)}</strong>
            <ProductActions part={part} />
          </div>
        </div>
      </section>

      <section className="product-info-grid">
        <article className="info-panel">
          <CheckCircle2 size={24} aria-hidden="true" />
          <h2>Номера и применимость</h2>
          <dl>
            <div>
              <dt>Номер</dt>
              <dd>{part.oem}</dd>
            </div>
            <div>
              <dt>Артикул</dt>
              <dd>{part.article}</dd>
            </div>
            <div>
              <dt>Производитель</dt>
              <dd>{part.manufacturer}</dd>
            </div>
            <div>
              <dt>Аналоги</dt>
              <dd>{part.analogs.join(", ")}</dd>
            </div>
          </dl>
        </article>

        <article className="info-panel">
          <Truck size={24} aria-hidden="true" />
          <h2>Резерв и доставка</h2>
          <p>{part.delivery}</p>
          <p>Склад: {part.stock}. Доставка рассчитывается после подтверждения города и габаритов.</p>
        </article>

        <article className="info-panel">
          <ShieldCheck size={24} aria-hidden="true" />
          <h2>Проверка перед заказом</h2>
          <ul>
            <li>сверка номера детали и модификации автомобиля;</li>
            <li>подтверждение состояния и комплектации;</li>
            <li>согласование гарантии, возврата и срока поставки.</li>
          </ul>
        </article>
      </section>

      <section className="workspace product-specs">
        <div className="section-heading">
          <p className="eyebrow">Характеристики</p>
          <h2>Данные карточки</h2>
        </div>
        <div className="spec-table">
          {Object.entries(part.specs).map(([name, value]) => (
            <div key={name}>
              <span>{name}</span>
              <strong>{value}</strong>
            </div>
          ))}
          <div>
            <span>Совместимость</span>
            <strong>{part.compatibility.join(", ")}</strong>
          </div>
        </div>
      </section>

      <section className="workspace">
        <div className="section-heading section-heading--row">
          <div>
            <p className="eyebrow">Похожие товары</p>
            <h2>Еще позиции из каталога</h2>
          </div>
          <Link className="text-action" href="/catalog">
            В каталог
            <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>
        <div className="related-grid">
          {similarParts.map((item) => (
            <Link key={item.id} className="category-card" href={getProductPath(item)}>
              <PackageCheck size={22} aria-hidden="true" />
              <strong>{item.name}</strong>
              <span>{item.brand} {item.model}, {formatPrice(item.price)}</span>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
