"use client";

import { Send } from "lucide-react";
import { useState } from "react";

type SubmitState =
  | {
      status: "idle";
    }
  | {
      status: "sending";
    }
  | {
      status: "success";
      requestId: string;
    }
  | {
      status: "error";
      message: string;
    };

const initialSubmitState: SubmitState = { status: "idle" };
const stripNumbers = (value: string) => value.replace(/\p{N}/gu, "");
const keepDigitsOnly = (value: string) => value.replace(/\D/g, "");

export default function RequestForm() {
  const [customerName, setCustomerName] = useState("");
  const [contact, setContact] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [requestText, setRequestText] = useState("");
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [submitState, setSubmitState] = useState<SubmitState>(initialSubmitState);

  const canSubmit =
    customerName.trim().length >= 2 &&
    contact.trim().length >= 5 &&
    requestText.trim().length > 0 &&
    privacyAccepted &&
    submitState.status !== "sending";

  const submitRequest = async () => {
    setSubmitState({ status: "sending" });

    try {
      const response = await fetch("/api/requests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          source: "request_form",
          customerName,
          contact,
          vehicle,
          requestText,
          privacyAccepted
        })
      });
      const result = (await response.json()) as { id?: string; error?: string };

      if (!response.ok || !result.id) {
        setSubmitState({
          status: "error",
          message: result.error ?? "Не удалось сохранить заявку"
        });
        return;
      }

      setCustomerName("");
      setContact("");
      setVehicle("");
      setRequestText("");
      setPrivacyAccepted(false);
      setSubmitState({ status: "success", requestId: result.id });
    } catch {
      setSubmitState({
        status: "error",
        message: "Не удалось связаться с сервером"
      });
    }
  };

  return (
    <form className="request-form" onSubmit={(event) => event.preventDefault()}>
      <label>
        Имя
        <input
          name="name"
          value={customerName}
          onChange={(event) => setCustomerName(stripNumbers(event.target.value))}
          placeholder="Как к вам обращаться"
          autoComplete="name"
        />
      </label>
      <label>
        Телефон или мессенджер
        <input
          type="tel"
          inputMode="numeric"
          name="phone"
          pattern="[0-9]*"
          value={contact}
          onChange={(event) => setContact(keepDigitsOnly(event.target.value))}
          placeholder="79990000000"
          autoComplete="tel"
        />
      </label>
      <label>
        Автомобиль
        <input
          name="vehicle"
          value={vehicle}
          onChange={(event) => setVehicle(event.target.value)}
          placeholder="Марка, модель, год, двигатель или модификация"
        />
      </label>
      <label>
        Что нужно найти
        <textarea
          name="parts"
          value={requestText}
          onChange={(event) => setRequestText(event.target.value)}
          placeholder="Номер детали, артикул, название, фото/описание или список позиций"
        />
      </label>
      <label className="checkbox-row">
        <input
          type="checkbox"
          name="privacy"
          checked={privacyAccepted}
          onChange={(event) => setPrivacyAccepted(event.target.checked)}
        />
        <span>Согласен на обработку персональных данных после добавления юридического текста</span>
      </label>
      <button type="button" disabled={!canSubmit} onClick={submitRequest}>
        <Send size={18} aria-hidden="true" />
        {submitState.status === "sending" ? "Сохраняем" : "Отправить заявку"}
      </button>
      {submitState.status === "success" ? (
        <p className="form-note">Заявка сохранена в базе: {submitState.requestId}</p>
      ) : null}
      {submitState.status === "error" ? <p className="form-note form-note--error">{submitState.message}</p> : null}
    </form>
  );
}
