import type { PublishedLegalDocument as PublishedLegalDocumentData } from "@/src/server/django/siteSettings";

type PublishedLegalDocumentProps = {
  document: PublishedLegalDocumentData;
};

export function PublishedLegalDocument({ document }: PublishedLegalDocumentProps) {
  return (
    <>
      <section className="page-heading">
        <p className="eyebrow">Документы</p>
        <h1>{document.title}</h1>
        <p>Версия: {document.version}</p>
      </section>
      <section className="legal-text">
        <LegalDocumentBody document={document} />
      </section>
    </>
  );
}

export function LegalDocumentBody({ document }: PublishedLegalDocumentProps) {
  const blocks = document.body
    .trim()
    .split(/\n\s*\n/)
    .filter(Boolean);

  return (
    <>{blocks.map((block, index) => (
      <p key={`${document.version}-${index}`} style={{ whiteSpace: "pre-line" }}>
        {block}
      </p>
    ))}</>
  );
}
