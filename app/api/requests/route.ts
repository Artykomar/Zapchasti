import { NextResponse } from "next/server";
import {
  createCustomerRequest,
  type CustomerRequestInput,
  type CustomerRequestItemInput
} from "@/src/server/db/catalog";
import { notifyManagerAboutRequest } from "@/src/server/notifications/manager";
import { hitRateLimit } from "@/src/server/security/rateLimit";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const jsonHeaders = {
  "Content-Type": "application/json; charset=utf-8"
};

const MAX_TEXT_LENGTH = 2000;
const MAX_FIELD_LENGTH = 240;
const MAX_ITEMS = 50;

type ValidationResult =
  | {
      ok: true;
      value: CustomerRequestInput;
    }
  | {
      ok: false;
      message: string;
    };

const cleanText = (value: unknown, maxLength = MAX_FIELD_LENGTH) =>
  typeof value === "string" ? value.trim().slice(0, maxLength) : "";

const toRequestItem = (value: unknown): CustomerRequestItemInput | undefined => {
  if (!value || typeof value !== "object") {
    return undefined;
  }

  const source = value as Record<string, unknown>;
  const name = cleanText(source.name);
  const quantity = Number(source.quantity);
  const price = Number(source.price ?? 0);

  if (!name || !Number.isFinite(quantity)) {
    return undefined;
  }

  return {
    id: cleanText(source.id),
    name,
    article: cleanText(source.article),
    quantity: Math.min(Math.max(Math.round(quantity), 1), 99),
    price: Number.isFinite(price) ? Math.max(Math.round(price), 0) : 0
  };
};

const validatePayload = (payload: unknown): ValidationResult => {
  if (!payload || typeof payload !== "object") {
    return { ok: false, message: "Некорректная заявка" };
  }

  const source = payload as Record<string, unknown>;
  const customerName = cleanText(source.customerName ?? source.name);
  const contact = cleanText(source.contact ?? source.phone);
  const vehicle = cleanText(source.vehicle);
  const requestText = cleanText(source.requestText ?? source.message ?? source.parts, MAX_TEXT_LENGTH);
  const rawItems = Array.isArray(source.items) ? source.items.slice(0, MAX_ITEMS) : [];
  const items = rawItems.map(toRequestItem).filter((item): item is CustomerRequestItemInput => Boolean(item));
  const rawSource = cleanText(source.source);
  const requestSource = rawSource === "cart" ? "cart" : "request_form";

  if (customerName.length < 2) {
    return { ok: false, message: "Укажите имя" };
  }

  if (contact.length < 5) {
    return { ok: false, message: "Укажите телефон или мессенджер" };
  }

  if (!requestText && items.length === 0) {
    return { ok: false, message: "Добавьте товары или опишите нужную деталь" };
  }

  if (source.privacyAccepted !== true) {
    return { ok: false, message: "Нужно согласие на обработку данных" };
  }

  return {
    ok: true,
    value: {
      customerName,
      contact,
      vehicle,
      requestText,
      source: requestSource,
      privacyAccepted: true,
      items
    }
  };
};

export async function POST(request: Request) {
  const clientIp =
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ??
    request.headers.get("x-real-ip") ??
    "local";

  if (hitRateLimit(`request:${clientIp}`)) {
    return NextResponse.json(
      { error: "Слишком много отправок подряд. Попробуйте чуть позже." },
      { status: 429, headers: jsonHeaders }
    );
  }

  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ error: "Некорректный JSON" }, { status: 400, headers: jsonHeaders });
  }

  const validation = validatePayload(payload);

  if (!validation.ok) {
    return NextResponse.json({ error: validation.message }, { status: 400, headers: jsonHeaders });
  }

  const result = createCustomerRequest(validation.value);
  await notifyManagerAboutRequest(validation.value, result);

  return NextResponse.json(result, { status: 201, headers: jsonHeaders });
}
