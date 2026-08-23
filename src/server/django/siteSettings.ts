import { fetchDjangoJson } from "@/src/server/django/client";

export type PublishedLegalDocument = {
  version: string;
  title: string;
  body: string;
  publishedAt: string | null;
};

type PublicSiteSettings = {
  documents: {
    published: Record<string, PublishedLegalDocument>;
  };
};

export const getPublishedLegalDocument = async (kind: string) => {
  try {
    const settings = await fetchDjangoJson<PublicSiteSettings>("/api/site-settings/");
    return settings.documents.published[kind];
  } catch {
    return undefined;
  }
};

export const getPublishedLegalDocuments = async (kinds: string[]) => {
  try {
    const settings = await fetchDjangoJson<PublicSiteSettings>("/api/site-settings/");
    return kinds.flatMap((kind) => {
      const document = settings.documents.published[kind];
      return document ? [{ kind, ...document }] : [];
    });
  } catch {
    return [];
  }
};
