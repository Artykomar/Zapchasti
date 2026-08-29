"use client";

import Link from "next/link";
import { Cookie } from "lucide-react";
import { useEffect, useState } from "react";

export const cookieNoticeName = "zemazap_cookie_notice";

const hasAcknowledgedCookieNotice = () =>
  document.cookie
    .split(";")
    .map((item) => item.trim())
    .some((item) => item.startsWith(`${cookieNoticeName}=`));

export default function CookieNotice() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(!hasAcknowledgedCookieNotice());
  }, []);

  const acknowledge = () => {
    const secure = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${cookieNoticeName}=acknowledged; Max-Age=31536000; Path=/; SameSite=Lax${secure}`;
    setIsVisible(false);
  };

  if (!isVisible) {
    return null;
  }

  return (
    <aside
      className="cookie-notice"
      role="dialog"
      aria-modal="false"
      aria-labelledby="cookie-notice-title"
      aria-describedby="cookie-notice-description"
    >
      <div className="cookie-notice__icon" aria-hidden="true">
        <Cookie size={22} />
      </div>
      <div className="cookie-notice__content">
        <strong id="cookie-notice-title">Файлы cookie</strong>
        <p id="cookie-notice-description">
          Сайт использует только необходимые cookie для входа в административный кабинет, сохранения выбранной темы
          и подтверждения этого уведомления. Корзина и избранное хранятся локально в браузере. Рекламные и
          аналитические cookie сейчас не используются.
        </p>
        <Link href="/privacy-policy">Подробнее в политике ПДн</Link>
      </div>
      <button type="button" onClick={acknowledge}>Понятно</button>
    </aside>
  );
}
