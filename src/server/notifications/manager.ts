import nodemailer from "nodemailer";
import { formatPrice } from "@/src/data/catalog";
import type { CustomerRequestInput } from "@/src/server/db/catalog";

type CreatedRequest = {
  id: string;
  status: string;
  totalEstimateRub: number;
};

const env = (key: string) => process.env[key]?.trim() ?? "";

const getAdminRequestUrl = (requestId: string) => {
  const baseUrl = env("ZEMAZAP_SITE_URL") || "http://127.0.0.1:3000";

  return `${baseUrl.replace(/\/$/, "")}/admin/requests/${requestId}`;
};

const buildNotificationText = (input: CustomerRequestInput, request: CreatedRequest) => {
  const itemsText =
    input.items && input.items.length > 0
      ? input.items
          .map((item) => `- ${item.name}${item.article ? `, арт. ${item.article}` : ""}, ${item.quantity} шт.`)
          .join("\n")
      : "- подбор по описанию";

  return [
    `Новая заявка Zemazap`,
    ``,
    `Клиент: ${input.customerName}`,
    `Контакт: ${input.contact}`,
    input.vehicle ? `Автомобиль: ${input.vehicle}` : "",
    input.requestText ? `Запрос: ${input.requestText}` : "",
    `Источник: ${input.source === "cart" ? "корзина" : "форма подбора"}`,
    `Сумма: ${request.totalEstimateRub > 0 ? formatPrice(request.totalEstimateRub) : "уточняется"}`,
    ``,
    `Позиции:`,
    itemsText,
    ``,
    `Открыть: ${getAdminRequestUrl(request.id)}`
  ]
    .filter((line) => line !== "")
    .join("\n");
};

const sendTelegramNotification = async (text: string) => {
  const token = env("ZEMAZAP_TELEGRAM_BOT_TOKEN");
  const chatId = env("ZEMAZAP_TELEGRAM_CHAT_ID");

  if (!token || !chatId) {
    return;
  }

  const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      disable_web_page_preview: true
    })
  });

  if (!response.ok) {
    throw new Error(`Telegram notification failed with status ${response.status}`);
  }
};

const sendEmailNotification = async (subject: string, text: string) => {
  const recipient = env("ZEMAZAP_MANAGER_EMAIL");
  const host = env("ZEMAZAP_SMTP_HOST");
  const port = Number(env("ZEMAZAP_SMTP_PORT") || "465");
  const user = env("ZEMAZAP_SMTP_USER");
  const password = env("ZEMAZAP_SMTP_PASSWORD");
  const from = env("ZEMAZAP_SMTP_FROM") || user;
  const secure = env("ZEMAZAP_SMTP_SECURE") !== "false";

  if (!recipient || !host || !port || !user || !password || !from) {
    return;
  }

  const transporter = nodemailer.createTransport({
    host,
    port,
    secure,
    auth: {
      user,
      pass: password
    }
  });

  await transporter.sendMail({
    from,
    to: recipient,
    subject,
    text
  });
};

export const notifyManagerAboutRequest = async (input: CustomerRequestInput, request: CreatedRequest) => {
  const text = buildNotificationText(input, request);
  const subject = `Новая заявка Zemazap: ${input.customerName}`;
  const results = await Promise.allSettled([
    sendTelegramNotification(text),
    sendEmailNotification(subject, text)
  ]);

  results.forEach((result) => {
    if (result.status === "rejected") {
      console.warn("[zemazap] Manager notification failed:", result.reason);
    }
  });
};
