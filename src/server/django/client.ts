const DEFAULT_DJANGO_API_URL = "http://127.0.0.1:8000";

export class DjangoApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export const getDjangoApiBaseUrl = () =>
  (process.env.ZEMAZAP_DJANGO_API_URL || DEFAULT_DJANGO_API_URL).replace(/\/+$/, "");

export const buildDjangoApiUrl = (path: string) => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${getDjangoApiBaseUrl()}${normalizedPath}`;
};

export const fetchDjangoRaw = (path: string, init: RequestInit = {}) =>
  fetch(buildDjangoApiUrl(path), {
    ...init,
    cache: "no-store"
  });

export const fetchDjangoJson = async <T>(path: string, init: RequestInit = {}): Promise<T> => {
  const response = await fetchDjangoRaw(path, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init.headers ?? {})
    }
  });
  const payload = (await response.json().catch(() => null)) as T | { error?: string } | null;

  if (!response.ok) {
    const message =
      payload && typeof payload === "object" && "error" in payload && payload.error
        ? payload.error
        : `Django API returned ${response.status}`;
    throw new DjangoApiError(message, response.status);
  }

  return payload as T;
};
